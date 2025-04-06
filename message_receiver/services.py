import json
import logging
import time
from typing import Dict, Any, Optional, Union, List

from django.utils import timezone
from django.conf import settings
from django.db import transaction

from core.models import ErrorLog
from openai_processor.models import PromptTemplate
from openai_processor.services import OpenAIService
from .models import MessageSource, Message, ProcessedMessage

logger = logging.getLogger('api_hub.message_receiver')

class MessageReceiverService:
    """
    Service for receiving and processing messages from different sources
    """
    
    def __init__(self):
        """
        Initialize the message receiver service
        """
        self.openai_service = OpenAIService()
    
    def receive_message(
        self, 
        source: MessageSource, 
        content: Union[Dict[str, Any], str, List[Any]],
        external_id: Optional[str] = None,
        priority: int = 0
    ) -> Message:
        """
        Receive a message from a source
        
        Args:
            source: MessageSource object
            content: Message content
            external_id: External ID for the message
            priority: Priority for processing (higher = higher priority)
            
        Returns:
            Created Message object
        """
        try:
            # Convert content to JSON-serializable format if needed
            if isinstance(content, str):
                try:
                    # Try to parse as JSON
                    content = json.loads(content)
                except json.JSONDecodeError:
                    # If not valid JSON, store as text
                    content = {'text': content}
            
            # Create the message
            message = Message.objects.create(
                source=source,
                content=content,
                external_id=external_id,
                priority=priority,
                status='received'
            )
            
            logger.info(f"Received message {message.id} from {source.name}")
            
            return message
            
        except Exception as e:
            # Log the error
            logger.exception(f"Error receiving message from {source.name}: {str(e)}")
            
            # Create error log
            ErrorLog.objects.create(
                level='error',
                message=f"Error receiving message from {source.name}: {str(e)}",
                component='message_receiver',
                context={
                    'source_id': source.id,
                    'content': str(content)[:1000],  # Truncate to avoid huge logs
                    'external_id': external_id
                },
                related_object_type='MessageSource',
                related_object_id=str(source.id)
            )
            
            # Re-raise the exception
            raise
    
    def process_message(self, message: Message) -> ProcessedMessage:
        """
        Process a message using OpenAI
        
        Args:
            message: Message to process
            
        Returns:
            ProcessedMessage object with the results
        """
        start_time = time.time()
        
        try:
            # Get the prompt template
            prompt_template = self._get_prompt_template(message.source)
            
            # Process the message
            with transaction.atomic():
                # Update message status
                message.status = 'processing'
                message.save(update_fields=['status'])
                
                # Process with OpenAI
                processed = self.openai_service.process_message(message, prompt_template)
                
                # Update message status
                message.status = 'processed'
                message.processed_at = timezone.now()
                message.save(update_fields=['status', 'processed_at'])
            
            logger.info(
                f"Processed message {message.id} in {time.time() - start_time:.2f}s "
                f"(function: {processed.function_name or 'none'})"
            )
            
            return processed
            
        except Exception as e:
            # Log the error
            logger.exception(f"Error processing message {message.id}: {str(e)}")
            
            # Update message status
            message.status = 'failed'
            message.status_message = str(e)
            message.save(update_fields=['status', 'status_message'])
            
            # Create error log
            ErrorLog.objects.create(
                level='error',
                message=f"Error processing message {message.id}: {str(e)}",
                component='message_receiver',
                context={
                    'message_id': message.id,
                    'source_id': message.source.id,
                    'external_id': message.external_id
                },
                related_object_type='Message',
                related_object_id=str(message.id)
            )
            
            # Re-raise the exception
            raise
    
    def process_webhook(
        self, 
        webhook_path: str, 
        content: Union[Dict[str, Any], str, List[Any]],
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Message]:
        """
        Process a webhook request
        
        Args:
            webhook_path: Path of the webhook
            content: Webhook content
            headers: Request headers
            
        Returns:
            Created Message object or None if no matching source
        """
        try:
            # Find the message source for this webhook
            try:
                source = MessageSource.objects.get(
                    webhook_url_path=webhook_path,
                    is_active=True
                )
            except MessageSource.DoesNotExist:
                logger.warning(f"No active message source found for webhook path: {webhook_path}")
                return None
            
            # Extract external ID from headers or content
            external_id = self._extract_external_id(source, content, headers)
            
            # Receive the message
            message = self.receive_message(
                source=source,
                content=content,
                external_id=external_id
            )
            
            # Process the message asynchronously if Celery is configured
            if hasattr(settings, 'CELERY_BROKER_URL') and settings.CELERY_BROKER_URL:
                from .tasks import process_message_task
                process_message_task.delay(message.id)
            else:
                # Process synchronously
                self.process_message(message)
            
            return message
            
        except Exception as e:
            # Log the error
            logger.exception(f"Error processing webhook {webhook_path}: {str(e)}")
            
            # Create error log
            ErrorLog.objects.create(
                level='error',
                message=f"Error processing webhook {webhook_path}: {str(e)}",
                component='message_receiver',
                context={
                    'webhook_path': webhook_path,
                    'content': str(content)[:1000],  # Truncate to avoid huge logs
                    'headers': headers
                }
            )
            
            # Re-raise the exception
            raise
    
    def _get_prompt_template(self, source: MessageSource) -> PromptTemplate:
        """
        Get the prompt template for a message source
        
        Args:
            source: MessageSource object
            
        Returns:
            PromptTemplate object
        """
        # Check if source has a specific prompt template in its config
        if source.config and 'prompt_template_id' in source.config:
            try:
                return PromptTemplate.objects.get(
                    id=source.config['prompt_template_id'],
                    is_active=True
                )
            except PromptTemplate.DoesNotExist:
                pass
        
        # Get a default template based on source type
        try:
            return PromptTemplate.objects.get(
                name=f"Default {source.get_source_type_display()} Template",
                is_active=True
            )
        except PromptTemplate.DoesNotExist:
            pass
        
        # Fall back to any active template
        try:
            return PromptTemplate.objects.filter(is_active=True).first()
        except PromptTemplate.DoesNotExist:
            # If no template exists, create a basic one
            return PromptTemplate.objects.create(
                name=f"Default Template for {source.name}",
                description=f"Auto-generated template for {source.name}",
                system_prompt=(
                    "You are an AI assistant that processes messages and determines "
                    "appropriate actions to take. Your task is to analyze the message "
                    "content and decide if any API calls should be made in response."
                ),
                user_prompt_template=(
                    "Please analyze the following message from {{source}}:\n\n"
                    "{{message}}\n\n"
                    "If this message requires an action, please call the appropriate function."
                ),
                model=settings.OPENAI_MODEL,
                function_calling_enabled=True
            )
    
    def _extract_external_id(
        self, 
        source: MessageSource, 
        content: Union[Dict[str, Any], str, List[Any]],
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Extract external ID from message content or headers
        
        Args:
            source: MessageSource object
            content: Message content
            headers: Request headers
            
        Returns:
            Extracted external ID or None
        """
        # Check source config for external ID path
        if source.config and 'external_id_path' in source.config:
            path = source.config['external_id_path']
            
            # Check if path is in headers
            if path.startswith('header:') and headers:
                header_name = path.split(':', 1)[1]
                if header_name in headers:
                    return headers[header_name]
            
            # Check if path is in content
            if isinstance(content, dict):
                # Handle dot notation (e.g., "data.id")
                if '.' in path:
                    parts = path.split('.')
                    value = content
                    for part in parts:
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        else:
                            value = None
                            break
                    if value:
                        return str(value)
                # Simple key
                elif path in content:
                    return str(content[path])
        
        # Source-specific extractors
        if source.source_type == 'sentry':
            # Try to extract Sentry event ID
            if isinstance(content, dict):
                if 'event_id' in content:
                    return content['event_id']
                if 'id' in content:
                    return content['id']
                if 'event' in content and isinstance(content['event'], dict):
                    if 'event_id' in content['event']:
                        return content['event']['event_id']
                    if 'id' in content['event']:
                        return content['event']['id']
        
        elif source.source_type == 'whatsapp':
            # Try to extract WhatsApp message ID
            if isinstance(content, dict):
                if 'entry' in content and isinstance(content['entry'], list):
                    for entry in content['entry']:
                        if isinstance(entry, dict) and 'changes' in entry and isinstance(entry['changes'], list):
                            for change in entry['changes']:
                                if isinstance(change, dict) and 'value' in change and isinstance(change['value'], dict):
                                    value = change['value']
                                    if 'messages' in value and isinstance(value['messages'], list):
                                        for message in value['messages']:
                                            if isinstance(message, dict) and 'id' in message:
                                                return message['id']
        
        # Fallback: None
        return None
