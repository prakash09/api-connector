from django import forms
from message_receiver.models import MessageSource
from api_connector.models import APIConfiguration, APIAuthentication # Import API models
from core.models import SystemConfig # Import SystemConfig

class MessageSourceForm(forms.ModelForm):
    """
    Form for creating and editing MessageSource instances.
    """
    class Meta:
        model = MessageSource
        fields = [
            'name', 
            'source_type', 
            'description', 
            'config', 
            'webhook_url_path', 
            'webhook_secret', 
            'prompt_template', 
            'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'config': forms.Textarea(attrs={'rows': 5}), # Use Textarea for JSON
            'prompt_template': forms.Textarea(attrs={'rows': 5}),
        }
        help_texts = {
            'config': 'Enter JSON configuration specific to the source type.',
            'webhook_url_path': 'Unique path component for the webhook URL (e.g., "sentry-webhook"). Required for webhook type.',
            'prompt_template': 'Jinja2 template for the OpenAI prompt. Use {{ message_content }} for raw data.',
        }

    def clean(self):
        cleaned_data = super().clean()
        source_type = cleaned_data.get("source_type")
        webhook_url_path = cleaned_data.get("webhook_url_path")

        if source_type == 'webhook' and not webhook_url_path:
            self.add_error('webhook_url_path', 'Webhook URL Path is required for Webhook source type.')
            
        # Add more validation as needed based on source_type and config keys
            
        return cleaned_data

class APIAuthenticationForm(forms.ModelForm):
    """
    Form for creating and editing APIAuthentication instances.
    """
    class Meta:
        model = APIAuthentication
        fields = [
            'name', 
            'auth_type', 
            'api_key', 
            'api_key_name', 
            'token', 
            'username', 
            'password', 
            'client_id', 
            'client_secret', 
            'token_url', 
            'refresh_token', 
            # 'access_token', # Usually managed internally
            # 'expires_at',   # Usually managed internally
        ]
        widgets = {
            'password': forms.PasswordInput(render_value=True), # Show existing value for edit
            'client_secret': forms.PasswordInput(render_value=True),
            'api_key': forms.PasswordInput(render_value=True),
            'token': forms.PasswordInput(render_value=True),
            'refresh_token': forms.PasswordInput(render_value=True),
        }
        help_texts = {
            'api_key_name': 'Header name for the API key (e.g., X-API-Key). Required if auth_type is API Key.',
            'token_url': 'URL to obtain OAuth 2.0 tokens. Required if auth_type is OAuth 2.0.',
        }

    # Add clean methods here to validate fields based on auth_type


class APIConfigurationForm(forms.ModelForm):
    """
    Form for creating and editing APIConfiguration instances.
    """
    class Meta:
        model = APIConfiguration
        fields = [
            'name', 
            'description', 
            'base_url', 
            'authentication', 
            'rate_limit_enabled', 
            'rate_limit', 
            'max_retries', 
            'retry_backoff', 
            'default_headers', 
            'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'default_headers': forms.Textarea(attrs={'rows': 5}), # Use Textarea for JSON
        }
        help_texts = {
            'rate_limit': 'Format: number/timeunit (e.g., 100/hour, 5/second).',
            'default_headers': 'Enter default HTTP headers as JSON.',
        }


class SystemConfigForm(forms.ModelForm):
    """
    Form for editing SystemConfig instances.
    """
    class Meta:
        model = SystemConfig
        fields = ['key', 'value', 'description']
        widgets = {
            'value': forms.Textarea(attrs={'rows': 5}), # Use Textarea for JSON
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'value': 'Enter the configuration value in JSON format.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make 'key' read-only if editing an existing instance
        if self.instance and self.instance.pk:
            self.fields['key'].widget.attrs['readonly'] = True
            self.fields['key'].widget.attrs['class'] = 'bg-gray-100' # Optional: visual cue
