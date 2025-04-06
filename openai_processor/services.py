import json
import logging
import time
from typing import Dict, List, Optional, Tuple, Any, Union

from django.conf import settings
from openai import OpenAI
from openai.types.chat import ChatCompletion

from api_connector.models import FunctionDefinition
from message_receiver.models import Message, ProcessedMessage
from .models import PromptTemplate, FunctionCallLog

logger = logging.getLogger('api_hub.openai_processor')

class OpenAIService:
    """
    Service for interacting with OpenAI API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI service
        
        Args:
            api_key: OpenAI API key (defaults to settings.OPENAI_API_KEY)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
    
    def process_message(self, message: Message, prompt_template: PromptTemplate) -> ProcessedMessage:
        """
        Process a message using OpenAI
        
        Args:
            message: Message to process
            prompt_template: PromptTemplate to use
            
        Returns:
            ProcessedMessage object with the results
        """
        start_time = time.time()
        
        # Prepare the message content
        if not message.content_text:
            # Extract text from content if not already done
            message.content_text = self._extract_text_from_content(message.content)
            message.save(update_fields=['content_text'])
        
        # Update message status
        message.status = 'processing'
        message.save(update_fields=['status'])
        
        # Format the prompt
        formatted_prompt = self._format_prompt(prompt_template, message)
        
        # Get available functions
        functions = self._get_available_functions() if prompt_template.function_calling_enabled else None
        
        try:
            # Call OpenAI
            response = self._call_openai(
                prompt_template.model,
                formatted_prompt['system'],
                formatted_prompt['user'],
                functions,
                temperature=prompt_template.temperature,
                max_tokens=prompt_template.max_tokens
            )
            
            # Process the response
            function_name = None
            function_args = None
            api_request = None
            api_response = None
            
            # Check if function was called
            if response.choices[0].message.function_call:
                function_call = response.choices[0].message.function_call
                function_name = function_call.name
                function_args = json.loads(function_call.arguments)
                
                # Execute the function
                api_request, api_response = self._execute_function(function_name, function_args, message)
            
            # Create ProcessedMessage
            processed = ProcessedMessage.objects.create(
                message=message,
                prompt=formatted_prompt['user'],
                openai_response=response.model_dump(),
                function_name=function_name,
                function_arguments=function_args,
                api_request=api_request,
                api_response=api_response,
                processing_time=time.time() - start_time,
                token_usage=response.usage.model_dump() if response.usage else None
            )
            
            # Update message status
            message.status = 'processed'
            message.processed_at = processed.created_at
            message.save(update_fields=['status', 'processed_at'])
            
            return processed
            
        except Exception as e:
            # Log the error
            logger.exception(f"Error processing message {message.id}: {str(e)}")
            
            # Update message status
            message.status = 'failed'
            message.status_message = str(e)
            message.save(update_fields=['status', 'status_message'])
            
            # Create a minimal ProcessedMessage to track the failure
            return ProcessedMessage.objects.create(
                message=message,
                prompt=formatted_prompt['user'],
                processing_time=time.time() - start_time,
            )
    
    def _extract_text_from_content(self, content: Dict) -> str:
        """
        Extract text from message content
        
        Args:
            content: Message content
            
        Returns:
            Extracted text
        """
        # This is a simple implementation - in a real app, you'd have
        # source-specific extractors for different message types
        if isinstance(content, dict):
            # Try to find text in common fields
            for field in ['text', 'message', 'body', 'content', 'description', 'title']:
                if field in content and isinstance(content[field], str):
                    return content[field]
            
            # For Sentry-like payloads
            if 'event' in content and isinstance(content['event'], dict):
                event = content['event']
                parts = []
                
                # Extract title/message
                if 'title' in event and event['title']:
                    parts.append(f"Error: {event['title']}")
                
                # Extract exception
                if 'exception' in event and isinstance(event['exception'], dict):
                    exception = event['exception']
                    if 'values' in exception and isinstance(exception['values'], list):
                        for value in exception['values']:
                            if isinstance(value, dict):
                                if 'type' in value and 'value' in value:
                                    parts.append(f"{value['type']}: {value['value']}")
                                if 'stacktrace' in value and isinstance(value['stacktrace'], dict):
                                    if 'frames' in value['stacktrace'] and isinstance(value['stacktrace']['frames'], list):
                                        frames = value['stacktrace']['frames']
                                        # Include the last few frames
                                        for frame in frames[-3:]:
                                            if isinstance(frame, dict):
                                                file = frame.get('filename', '')
                                                line = frame.get('lineno', '')
                                                function = frame.get('function', '')
                                                parts.append(f"  at {function} ({file}:{line})")
                
                if parts:
                    return "\n".join(parts)
            
            # If we can't find a specific field, convert the whole content to string
            return json.dumps(content, indent=2)
        
        # If content is already a string
        if isinstance(content, str):
            return content
        
        # Fallback
        return str(content)
    
    def _format_prompt(self, prompt_template: PromptTemplate, message: Message) -> Dict[str, str]:
        """
        Format the prompt using the template and message
        
        Args:
            prompt_template: PromptTemplate to use
            message: Message to process
            
        Returns:
            Dict with 'system' and 'user' prompts
        """
        # Get the system prompt
        system_prompt = prompt_template.system_prompt
        
        # Format the user prompt
        user_prompt = prompt_template.user_prompt_template
        
        # Replace placeholders
        context = {
            'message': message.content_text,
            'source': message.source.name,
            'source_type': message.source.get_source_type_display(),
            'external_id': message.external_id or '',
            'received_at': message.received_at.isoformat(),
            'raw_content': json.dumps(message.content, indent=2),
        }
        
        # Simple placeholder replacement
        for key, value in context.items():
            user_prompt = user_prompt.replace(f"{{{{{key}}}}}", str(value))
        
        return {
            'system': system_prompt,
            'user': user_prompt
        }
    
    def _get_available_functions(self) -> List[Dict[str, Any]]:
        """
        Get available functions for OpenAI function calling
        
        Returns:
            List of function definitions in OpenAI format
        """
        functions = []
        
        # Get active function definitions
        function_defs = FunctionDefinition.objects.filter(
            is_active=True,
            api_endpoint__is_active=True,
            api_endpoint__api_config__is_active=True
        ).select_related('api_endpoint', 'api_endpoint__api_config')
        
        for func_def in function_defs:
            functions.append({
                "type": "function",
                "function": {
                    "name": func_def.name,
                    "description": func_def.description,
                    "parameters": func_def.parameters_schema
                }
            })
        
        return functions
    
    def _call_openai(
        self, 
        model: str, 
        system_prompt: str, 
        user_prompt: str,
        functions: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> ChatCompletion:
        """
        Call OpenAI API
        
        Args:
            model: OpenAI model to use
            system_prompt: System prompt
            user_prompt: User prompt
            functions: List of function definitions
            temperature: Temperature for sampling
            max_tokens: Maximum tokens to generate
            
        Returns:
            OpenAI response
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if functions:
            kwargs["tools"] = functions
            kwargs["tool_choice"] = "auto"
        
        return self.client.chat.completions.create(**kwargs)
    
    def _execute_function(
        self, 
        function_name: str, 
        function_args: Dict[str, Any],
        message: Message
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Execute a function called by OpenAI
        
        Args:
            function_name: Name of the function to execute
            function_args: Arguments for the function
            message: Original message
            
        Returns:
            Tuple of (request, response)
        """
        # Create a function call log
        function_call = FunctionCallLog.objects.create(
            function_name=function_name,
            function_arguments=function_args,
            message=message,
            status='pending'
        )
        
        start_time = time.time()
        
        try:
            # Get the function definition
            func_def = FunctionDefinition.objects.get(
                name=function_name,
                is_active=True
            )
            
            # Get the API endpoint
            endpoint = func_def.api_endpoint
            api_config = endpoint.api_config
            
            # Map function arguments to API request
            mapped_args = self._map_function_args(func_def, function_args)
            
            # Build the request
            request = {
                'url': f"{api_config.base_url.rstrip('/')}/{endpoint.path.lstrip('/')}",
                'method': endpoint.http_method,
                'headers': {**api_config.default_headers, **endpoint.request_headers},
                'data': mapped_args
            }
            
            # TODO: Implement actual API call
            # For now, we'll just log the request and return a mock response
            response = {
                'status': 'success',
                'message': f"Function {function_name} executed successfully",
                'data': mapped_args
            }
            
            # Update the function call log
            function_call.status = 'success'
            function_call.result = response
            function_call.execution_time = time.time() - start_time
            function_call.save()
            
            return request, response
            
        except Exception as e:
            # Log the error
            logger.exception(f"Error executing function {function_name}: {str(e)}")
            
            # Update the function call log
            function_call.status = 'failed'
            function_call.error_message = str(e)
            function_call.execution_time = time.time() - start_time
            function_call.save()
            
            return None, {'error': str(e)}
    
    def _map_function_args(
        self, 
        func_def: FunctionDefinition, 
        function_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map function arguments to API request parameters
        
        Args:
            func_def: Function definition
            function_args: Arguments from OpenAI
            
        Returns:
            Mapped arguments for the API request
        """
        # If no mapping is defined, use the arguments as-is
        if not func_def.parameter_mapping:
            return function_args
        
        # Apply the mapping
        mapped_args = {}
        
        for target_key, source_path in func_def.parameter_mapping.items():
            # Handle simple key mapping
            if isinstance(source_path, str) and source_path in function_args:
                mapped_args[target_key] = function_args[source_path]
            
            # Handle nested paths (e.g., "user.name")
            elif isinstance(source_path, str) and '.' in source_path:
                parts = source_path.split('.')
                value = function_args
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        value = None
                        break
                if value is not None:
                    mapped_args[target_key] = value
            
            # Handle template strings (e.g., "{user.name} <{user.email}>")
            elif isinstance(source_path, str) and '{' in source_path:
                template = source_path
                for arg_name, arg_value in function_args.items():
                    if isinstance(arg_value, (str, int, float, bool)):
                        template = template.replace(f"{{{arg_name}}}", str(arg_value))
                mapped_args[target_key] = template
            
            # Handle static values
            elif isinstance(source_path, dict) and 'static' in source_path:
                mapped_args[target_key] = source_path['static']
            
            # Handle transformations
            elif isinstance(source_path, dict) and 'transform' in source_path:
                if source_path['transform'] == 'join' and 'fields' in source_path and 'separator' in source_path:
                    values = []
                    for field in source_path['fields']:
                        if field in function_args:
                            values.append(str(function_args[field]))
                    mapped_args[target_key] = source_path['separator'].join(values)
        
        # Include any unmapped arguments if they match target keys
        for key, value in function_args.items():
            if key not in func_def.parameter_mapping and key not in mapped_args:
                mapped_args[key] = value
        
        return mapped_args
