import json
import logging
import time
from typing import Dict, Any, Optional, Tuple, Union
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

from django.utils import timezone
from django.conf import settings

from core.models import RateLimitLog, ErrorLog
from .models import APIConfiguration, APIEndpoint, APIAuthentication, FunctionDefinition

logger = logging.getLogger('api_hub.api_connector')

class APIConnectorService:
    """
    Service for connecting to external APIs
    """
    
    def __init__(self):
        """
        Initialize the API connector service
        """
        self.session = requests.Session()
    
    def call_api(
        self, 
        endpoint: APIEndpoint, 
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        headers: Dict[str, Any] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Call an API endpoint
        
        Args:
            endpoint: APIEndpoint to call
            data: Request data (for POST, PUT, PATCH)
            params: Query parameters (for GET)
            headers: Additional headers
            
        Returns:
            Tuple of (request, response)
        """
        start_time = time.time()
        api_config = endpoint.api_config
        
        # Check rate limits
        if api_config.rate_limit_enabled and settings.RATE_LIMIT_ENABLED:
            if not self._check_rate_limit(api_config):
                raise Exception(f"Rate limit exceeded for API {api_config.name}")
        
        # Prepare request
        url = f"{api_config.base_url.rstrip('/')}/{endpoint.path.lstrip('/')}"
        method = endpoint.http_method
        
        # Merge headers
        request_headers = {}
        if api_config.default_headers:
            request_headers.update(api_config.default_headers)
        if endpoint.request_headers:
            request_headers.update(endpoint.request_headers)
        if headers:
            request_headers.update(headers)
        
        # Add authentication
        if api_config.authentication:
            auth_headers = self._get_auth_headers(api_config.authentication)
            request_headers.update(auth_headers)
        
        # Prepare request data
        if data and endpoint.request_body_template:
            data = self._apply_template(endpoint.request_body_template, data)
        
        # Build request dict for logging
        request_dict = {
            'url': url,
            'method': method,
            'headers': request_headers,
            'params': params,
            'data': data
        }
        
        # Make the request with retry logic
        response_dict = None
        retry_count = 0
        max_retries = api_config.max_retries
        
        while retry_count <= max_retries:
            try:
                # Make the request
                response = self._make_request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    params=params,
                    data=data,
                    auth=self._get_auth_object(api_config.authentication),
                    timeout=30  # Default timeout
                )
                
                # Parse response
                try:
                    response_data = response.json()
                except ValueError:
                    response_data = {'text': response.text}
                
                response_dict = {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'data': response_data,
                    'elapsed': response.elapsed.total_seconds()
                }
                
                # Check if response is successful
                if response.status_code < 400:
                    # Apply response mapping if defined
                    if endpoint.response_mapping:
                        response_dict['mapped_data'] = self._apply_mapping(
                            endpoint.response_mapping, 
                            response_data
                        )
                    
                    # Log successful request
                    logger.info(
                        f"API call successful: {api_config.name} - {endpoint.name} "
                        f"({response.status_code}) in {response.elapsed.total_seconds():.2f}s"
                    )
                    
                    break
                else:
                    # Handle error response
                    error_msg = f"API error: {response.status_code} - {response.text}"
                    logger.warning(error_msg)
                    
                    # Check if we should retry
                    if response.status_code in (429, 500, 502, 503, 504) and retry_count < max_retries:
                        retry_count += 1
                        
                        # Calculate backoff time
                        backoff_time = self._calculate_backoff_time(
                            retry_count, 
                            api_config.retry_backoff,
                            response
                        )
                        
                        logger.info(f"Retrying in {backoff_time:.2f}s (attempt {retry_count}/{max_retries})")
                        time.sleep(backoff_time)
                    else:
                        # Log error and break
                        self._log_error(
                            api_config=api_config,
                            endpoint=endpoint,
                            request=request_dict,
                            response=response_dict,
                            error=error_msg
                        )
                        break
            
            except Exception as e:
                # Handle request exception
                error_msg = f"API request failed: {str(e)}"
                logger.exception(error_msg)
                
                response_dict = {
                    'status_code': 0,
                    'error': str(e),
                    'elapsed': time.time() - start_time
                }
                
                # Check if we should retry
                if retry_count < max_retries:
                    retry_count += 1
                    
                    # Calculate backoff time
                    backoff_time = self._calculate_backoff_time(
                        retry_count, 
                        api_config.retry_backoff
                    )
                    
                    logger.info(f"Retrying in {backoff_time:.2f}s (attempt {retry_count}/{max_retries})")
                    time.sleep(backoff_time)
                else:
                    # Log error and break
                    self._log_error(
                        api_config=api_config,
                        endpoint=endpoint,
                        request=request_dict,
                        response=response_dict,
                        error=error_msg
                    )
                    break
        
        return request_dict, response_dict
    
    def execute_function(
        self, 
        function_name: str, 
        function_args: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Execute a function by name
        
        Args:
            function_name: Name of the function to execute
            function_args: Arguments for the function
            
        Returns:
            Tuple of (request, response)
        """
        # Get the function definition
        try:
            func_def = FunctionDefinition.objects.get(
                name=function_name,
                is_active=True
            )
        except FunctionDefinition.DoesNotExist:
            raise ValueError(f"Function '{function_name}' not found or not active")
        
        # Get the API endpoint
        endpoint = func_def.api_endpoint
        
        # Map function arguments to API request
        mapped_args = self._map_function_args(func_def, function_args)
        
        # Determine if arguments should be sent as params or data
        params = None
        data = None
        
        if endpoint.http_method.upper() == 'GET':
            params = mapped_args
        else:
            data = mapped_args
        
        # Call the API
        return self.call_api(endpoint, data=data, params=params)
    
    def _make_request(
        self, 
        method: str, 
        url: str, 
        headers: Dict[str, Any] = None, 
        params: Dict[str, Any] = None, 
        data: Dict[str, Any] = None,
        auth: Optional[requests.auth.AuthBase] = None,
        timeout: int = 30
    ) -> requests.Response:
        """
        Make an HTTP request
        
        Args:
            method: HTTP method
            url: URL to call
            headers: Request headers
            params: Query parameters
            data: Request data
            auth: Authentication object
            timeout: Request timeout in seconds
            
        Returns:
            Response object
        """
        method = method.upper()
        
        # Convert data to JSON if it's a dict
        json_data = None
        if data and isinstance(data, dict):
            json_data = data
            data = None
        
        # Make the request
        if method == 'GET':
            return self.session.get(
                url, 
                headers=headers, 
                params=params, 
                auth=auth, 
                timeout=timeout
            )
        elif method == 'POST':
            return self.session.post(
                url, 
                headers=headers, 
                params=params, 
                data=data, 
                json=json_data, 
                auth=auth, 
                timeout=timeout
            )
        elif method == 'PUT':
            return self.session.put(
                url, 
                headers=headers, 
                params=params, 
                data=data, 
                json=json_data, 
                auth=auth, 
                timeout=timeout
            )
        elif method == 'PATCH':
            return self.session.patch(
                url, 
                headers=headers, 
                params=params, 
                data=data, 
                json=json_data, 
                auth=auth, 
                timeout=timeout
            )
        elif method == 'DELETE':
            return self.session.delete(
                url, 
                headers=headers, 
                params=params, 
                data=data, 
                json=json_data, 
                auth=auth, 
                timeout=timeout
            )
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    
    def _get_auth_headers(self, auth: APIAuthentication) -> Dict[str, str]:
        """
        Get authentication headers
        
        Args:
            auth: APIAuthentication object
            
        Returns:
            Dict of authentication headers
        """
        headers = {}
        
        if auth.auth_type == 'api_key':
            # API Key authentication
            if auth.api_key and auth.api_key_name:
                headers[auth.api_key_name] = auth.api_key
        
        elif auth.auth_type == 'bearer':
            # Bearer token authentication
            if auth.token:
                headers['Authorization'] = f"Bearer {auth.token}"
        
        # OAuth 2.0 token is handled by _get_auth_object
        
        return headers
    
    def _get_auth_object(self, auth: Optional[APIAuthentication]) -> Optional[requests.auth.AuthBase]:
        """
        Get authentication object for requests
        
        Args:
            auth: APIAuthentication object
            
        Returns:
            Authentication object or None
        """
        if not auth:
            return None
        
        if auth.auth_type == 'basic':
            # Basic authentication
            if auth.username and auth.password:
                return HTTPBasicAuth(auth.username, auth.password)
        
        elif auth.auth_type == 'oauth2':
            # OAuth 2.0 authentication
            # Check if token is expired and refresh if needed
            if auth.expires_at and auth.expires_at <= timezone.now():
                # Token is expired, refresh it
                # This would be implemented in a real application
                pass
        
        return None
    
    def _check_rate_limit(self, api_config: APIConfiguration) -> bool:
        """
        Check if the API call is within rate limits
        
        Args:
            api_config: APIConfiguration object
            
        Returns:
            True if within limits, False otherwise
        """
        if not api_config.rate_limit_enabled:
            return True
        
        # Parse rate limit
        try:
            limit_parts = api_config.rate_limit.split('/')
            limit = int(limit_parts[0])
            period = limit_parts[1].lower()
            
            # Calculate window
            now = timezone.now()
            
            if period == 'second':
                window_start = now.replace(microsecond=0)
                window_end = window_start + timedelta(seconds=1)
            elif period == 'minute':
                window_start = now.replace(second=0, microsecond=0)
                window_end = window_start + timedelta(minutes=1)
            elif period == 'hour':
                window_start = now.replace(minute=0, second=0, microsecond=0)
                window_end = window_start + timedelta(hours=1)
            elif period == 'day':
                window_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                window_end = window_start + timedelta(days=1)
            else:
                # Invalid period, default to hourly
                window_start = now.replace(minute=0, second=0, microsecond=0)
                window_end = window_start + timedelta(hours=1)
            
            # Check if we have a rate limit log for this window
            rate_limit_log, created = RateLimitLog.objects.get_or_create(
                target_type='api_config',
                target_id=str(api_config.id),
                window_start=window_start,
                defaults={
                    'window_end': window_end,
                    'limit': limit,
                    'request_count': 1
                }
            )
            
            if not created:
                # Increment request count
                if rate_limit_log.request_count >= rate_limit_log.limit:
                    # Rate limit exceeded
                    return False
                
                rate_limit_log.request_count += 1
                rate_limit_log.save(update_fields=['request_count', 'last_request_at'])
            
            return True
            
        except Exception as e:
            # Log error but don't block the request
            logger.exception(f"Error checking rate limit: {str(e)}")
            return True
    
    def _calculate_backoff_time(
        self, 
        retry_count: int, 
        use_exponential: bool,
        response: Optional[requests.Response] = None
    ) -> float:
        """
        Calculate backoff time for retries
        
        Args:
            retry_count: Current retry attempt
            use_exponential: Whether to use exponential backoff
            response: Response object (to check for Retry-After header)
            
        Returns:
            Backoff time in seconds
        """
        # Check for Retry-After header
        if response and 'Retry-After' in response.headers:
            try:
                return float(response.headers['Retry-After'])
            except (ValueError, TypeError):
                pass
        
        # Calculate backoff time
        if use_exponential:
            # Exponential backoff with jitter
            base_delay = 0.5
            max_delay = 60
            
            # Calculate delay: 2^retry * base_delay
            delay = min(max_delay, (2 ** retry_count) * base_delay)
            
            # Add jitter (±25%)
            import random
            jitter = random.uniform(-0.25, 0.25)
            delay = delay * (1 + jitter)
            
            return delay
        else:
            # Linear backoff
            return 1.0 * retry_count
    
    def _apply_template(self, template: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a template to request data
        
        Args:
            template: Template dict
            data: Input data
            
        Returns:
            Processed data
        """
        # Simple implementation - in a real app, this would be more sophisticated
        result = template.copy()
        
        # Replace placeholders in the template
        for key, value in data.items():
            # Look for this key in the template
            if key in result:
                result[key] = value
        
        return result
    
    def _apply_mapping(self, mapping: Dict[str, str], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a mapping to response data
        
        Args:
            mapping: Mapping dict
            data: Input data
            
        Returns:
            Mapped data
        """
        result = {}
        
        for target_key, source_path in mapping.items():
            # Handle simple key mapping
            if '.' not in source_path:
                if source_path in data:
                    result[target_key] = data[source_path]
            else:
                # Handle nested paths (e.g., "data.items.0.id")
                parts = source_path.split('.')
                value = data
                for part in parts:
                    try:
                        # Handle array indices
                        if part.isdigit():
                            part = int(part)
                        
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        elif isinstance(value, list) and isinstance(part, int) and part < len(value):
                            value = value[part]
                        else:
                            value = None
                            break
                    except (KeyError, TypeError, IndexError):
                        value = None
                        break
                
                if value is not None:
                    result[target_key] = value
        
        return result
    
    def _map_function_args(
        self, 
        func_def: FunctionDefinition, 
        function_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map function arguments to API request parameters
        
        Args:
            func_def: Function definition
            function_args: Arguments from function call
            
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
    
    def _log_error(
        self,
        api_config: APIConfiguration,
        endpoint: APIEndpoint,
        request: Dict[str, Any],
        response: Optional[Dict[str, Any]],
        error: str
    ) -> None:
        """
        Log an API error
        
        Args:
            api_config: APIConfiguration object
            endpoint: APIEndpoint object
            request: Request details
            response: Response details
            error: Error message
        """
        try:
            # Create error log
            ErrorLog.objects.create(
                level='error',
                message=f"API Error: {api_config.name} - {endpoint.name}: {error}",
                component='api_connector',
                context={
                    'api_config_id': api_config.id,
                    'endpoint_id': endpoint.id,
                    'request': request,
                    'response': response
                },
                related_object_type='APIEndpoint',
                related_object_id=str(endpoint.id)
            )
        except Exception as e:
            # If we can't log to the database, log to the console
            logger.exception(f"Error logging API error: {str(e)}")
