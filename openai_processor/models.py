from django.db import models
from django.utils.translation import gettext_lazy as _

class AIModelConfiguration(models.Model):
    """
    Model to store configurations for AI models (OpenAI and compatible)
    """
    MODEL_TYPE_CHOICES = [
        ('openai', _('OpenAI')),
        ('azure', _('Azure OpenAI')),
        ('anthropic', _('Anthropic')),
        ('custom', _('Custom OpenAI-compatible')),
    ]
    
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    model_type = models.CharField(_('Model Type'), max_length=20, choices=MODEL_TYPE_CHOICES, default='openai')
    
    # API Configuration
    base_url = models.URLField(_('Base URL'), blank=True, 
                             help_text=_('Base URL for the API (leave empty for default OpenAI URL)'))
    api_key = models.CharField(_('API Key'), max_length=255)
    organization_id = models.CharField(_('Organization ID'), max_length=255, blank=True,
                                     help_text=_('OpenAI organization ID (if applicable)'))
    
    # Default model parameters
    default_model = models.CharField(_('Default Model'), max_length=50, default='gpt-4o',
                                   help_text=_('Default model to use (e.g., gpt-4o, claude-3-opus)'))
    default_temperature = models.FloatField(_('Default Temperature'), default=0.7)
    default_max_tokens = models.PositiveIntegerField(_('Default Max Tokens'), default=1000)
    
    # Status
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('AI Model Configuration')
        verbose_name_plural = _('AI Model Configurations')
    
    def __str__(self):
        return f"{self.name} ({self.get_model_type_display()})"


class PromptTemplate(models.Model):
    """
    Model to store templates for OpenAI prompts
    """
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    
    # Template content
    system_prompt = models.TextField(_('System Prompt'), 
                                   help_text=_('System prompt for setting the context'))
    user_prompt_template = models.TextField(_('User Prompt Template'), 
                                         help_text=_('Template for user prompt with placeholders'))
    
    # Configuration
    ai_model_config = models.ForeignKey(
        AIModelConfiguration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prompt_templates',
        verbose_name=_('AI Model Configuration'),
        help_text=_('AI model configuration to use (leave empty to use system default)')
    )
    model = models.CharField(_('Model'), max_length=50, default='gpt-4o',
                           help_text=_('Model name (overrides the default model from AI Model Configuration if specified)'))
    temperature = models.FloatField(_('Temperature'), default=0.7)
    max_tokens = models.PositiveIntegerField(_('Max Tokens'), default=1000)
    
    # Function calling
    function_calling_enabled = models.BooleanField(_('Function Calling Enabled'), default=True)
    
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Prompt Template')
        verbose_name_plural = _('Prompt Templates')
    
    def __str__(self):
        return self.name


class FunctionCallLog(models.Model):
    """
    Model to log function calls made by OpenAI
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('success', _('Success')),
        ('failed', _('Failed')),
    ]
    
    # Function details
    function_name = models.CharField(_('Function Name'), max_length=100)
    function_arguments = models.JSONField(_('Function Arguments'))
    
    # Call details
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.JSONField(_('Result'), blank=True, null=True)
    error_message = models.TextField(_('Error Message'), blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    execution_time = models.FloatField(_('Execution Time (s)'), blank=True, null=True)
    
    # Related models
    message = models.ForeignKey(
        'message_receiver.Message',
        on_delete=models.CASCADE,
        related_name='function_calls',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('Function Call Log')
        verbose_name_plural = _('Function Call Logs')
        indexes = [
            models.Index(fields=['function_name']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.function_name} ({self.status})"
