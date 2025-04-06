from django import forms
from .models import PromptTemplate, AIModelConfiguration

class AIModelConfigurationForm(forms.ModelForm):
    """Form for creating and editing AIModelConfiguration instances."""
    class Meta:
        model = AIModelConfiguration
        fields = [
            'name', 'description', 'model_type', 'base_url', 'api_key', 'organization_id',
            'default_model', 'default_temperature', 'default_max_tokens', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'input'}),
            'model_type': forms.Select(attrs={'class': 'input'}),
            'base_url': forms.URLInput(attrs={'class': 'input'}),
            'api_key': forms.PasswordInput(attrs={'class': 'input', 'autocomplete': 'new-password'}),
            'organization_id': forms.TextInput(attrs={'class': 'input'}),
            'default_model': forms.TextInput(attrs={'class': 'input'}),
            'default_temperature': forms.NumberInput(attrs={'step': '0.1', 'class': 'input'}),
            'default_max_tokens': forms.NumberInput(attrs={'class': 'input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'}),
        }
        labels = {
            'model_type': 'Model Type',
            'base_url': 'Base URL',
            'api_key': 'API Key',
            'organization_id': 'Organization ID',
            'default_model': 'Default Model',
            'default_temperature': 'Default Temperature',
            'default_max_tokens': 'Default Max Tokens',
            'is_active': 'Active',
        }
        help_texts = {
            'name': 'A unique name for this AI model configuration.',
            'description': 'A brief description of what this configuration is used for.',
            'model_type': 'The type of AI model.',
            'base_url': 'The base URL for the API (leave empty for default OpenAI URL).',
            'api_key': 'The API key for the model.',
            'organization_id': 'The organization ID (if applicable).',
            'default_model': 'The default model to use (e.g., gpt-4o, claude-3-opus).',
            'default_temperature': 'Controls randomness (0.0 to 2.0). Lower values are more deterministic.',
            'default_max_tokens': 'Maximum number of tokens to generate.',
            'is_active': 'Only active configurations can be used.',
        }


class PromptTemplateForm(forms.ModelForm):
    """Form for creating and editing PromptTemplate instances."""
    class Meta:
        model = PromptTemplate
        fields = [
            'name', 'description', 'system_prompt', 'user_prompt_template', 
            'ai_model_config', 'model', 'temperature', 'max_tokens', 'function_calling_enabled', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'input'}),
            'system_prompt': forms.Textarea(attrs={'rows': 5, 'class': 'input font-mono'}),
            'user_prompt_template': forms.Textarea(attrs={'rows': 10, 'class': 'input font-mono'}),
            'model': forms.TextInput(attrs={'class': 'input'}),
            'temperature': forms.NumberInput(attrs={'step': '0.1', 'class': 'input'}),
            'max_tokens': forms.NumberInput(attrs={'class': 'input'}),
            'function_calling_enabled': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'}),
        }
        labels = {
            'user_prompt_template': 'User Prompt Template',
            'function_calling_enabled': 'Enable Function Calling',
            'is_active': 'Active',
        }
        help_texts = {
            'name': 'A unique name for this template.',
            'description': 'A brief description of what this template is used for.',
            'system_prompt': 'System prompt for setting the context (e.g., "You are a helpful assistant.")',
            'user_prompt_template': 'Template for the user prompt. Use {{ variable_name }} for placeholders.',
            'ai_model_config': 'AI model configuration to use (leave empty to use system default).',
            'model': 'The model to use (overrides the default model from AI Model Configuration if specified).',
            'temperature': 'Controls randomness (0.0 to 2.0). Lower values are more deterministic.',
            'max_tokens': 'Maximum number of tokens to generate.',
            'function_calling_enabled': 'Allow the model to suggest function calls.',
            'is_active': 'Only active templates can be used.',
        }
