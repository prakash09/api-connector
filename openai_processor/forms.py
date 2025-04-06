from django import forms
from .models import PromptTemplate

class PromptTemplateForm(forms.ModelForm):
    """Form for creating and editing PromptTemplate instances."""
    class Meta:
        model = PromptTemplate
        fields = [
            'name', 'description', 'system_prompt', 'user_prompt_template', 
            'model', 'temperature', 'max_tokens', 'function_calling_enabled', 'is_active'
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
            'model': 'The OpenAI model to use (e.g., gpt-4o, gpt-3.5-turbo).',
            'temperature': 'Controls randomness (0.0 to 2.0). Lower values are more deterministic.',
            'max_tokens': 'Maximum number of tokens to generate.',
            'function_calling_enabled': 'Allow the model to suggest function calls.',
            'is_active': 'Only active templates can be used.',
        }
