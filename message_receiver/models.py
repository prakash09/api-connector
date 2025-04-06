from django.db import models
from django.utils.translation import gettext_lazy as _

class MessageSource(models.Model):
    """
    Model to define different sources of messages (Sentry, WhatsApp, etc.)
    """
    SOURCE_TYPE_CHOICES = [
        ('webhook', _('Webhook')),
        ('api', _('API')),
        ('email', _('Email')),
        ('sentry', _('Sentry')),
        ('whatsapp', _('WhatsApp')),
        ('custom', _('Custom')),
    ]
    
    name = models.CharField(_('Name'), max_length=100)
    source_type = models.CharField(_('Source Type'), max_length=20, choices=SOURCE_TYPE_CHOICES)
    description = models.TextField(_('Description'), blank=True)
    
    # Configuration
    config = models.JSONField(_('Configuration'), default=dict, blank=True,
                            help_text=_('Source-specific configuration'))
    
    # Webhook specific
    webhook_url_path = models.CharField(_('Webhook URL Path'), max_length=100, blank=True, null=True,
                                      help_text=_('Path for the webhook endpoint (e.g., sentry-webhook)'))
    webhook_secret = models.CharField(_('Webhook Secret'), max_length=255, blank=True, null=True)
    
    # Processing configuration
    prompt_template = models.TextField(_('Prompt Template'), blank=True,
                                     help_text=_('Template for OpenAI prompt with placeholders'))
    
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Message Source')
        verbose_name_plural = _('Message Sources')
    
    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class Message(models.Model):
    """
    Model to store received messages
    """
    STATUS_CHOICES = [
        ('received', _('Received')),
        ('processing', _('Processing')),
        ('processed', _('Processed')),
        ('failed', _('Failed')),
        ('ignored', _('Ignored')),
    ]
    
    source = models.ForeignKey(
        MessageSource, 
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    # Message content
    content = models.JSONField(_('Content'), 
                             help_text=_('Raw message content'))
    content_text = models.TextField(_('Content Text'), blank=True, null=True,
                                  help_text=_('Extracted text content for processing'))
    
    # Message metadata
    external_id = models.CharField(_('External ID'), max_length=255, blank=True, null=True,
                                 help_text=_('ID from the external system'))
    received_at = models.DateTimeField(_('Received At'), auto_now_add=True)
    
    # Processing status
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='received')
    status_message = models.TextField(_('Status Message'), blank=True, null=True)
    
    # Processing metadata
    priority = models.PositiveSmallIntegerField(_('Priority'), default=0,
                                              help_text=_('Higher number means higher priority'))
    processed_at = models.DateTimeField(_('Processed At'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        indexes = [
            models.Index(fields=['source', 'status']),
            models.Index(fields=['external_id']),
            models.Index(fields=['received_at']),
        ]
    
    def __str__(self):
        return f"Message {self.id} from {self.source.name} ({self.status})"


class ProcessedMessage(models.Model):
    """
    Model to store processed messages and their results
    """
    message = models.OneToOneField(
        Message,
        on_delete=models.CASCADE,
        related_name='processed_result'
    )
    
    # OpenAI processing
    prompt = models.TextField(_('Prompt'), blank=True, null=True)
    openai_response = models.JSONField(_('OpenAI Response'), blank=True, null=True)
    
    # Function calling
    function_name = models.CharField(_('Function Name'), max_length=100, blank=True, null=True)
    function_arguments = models.JSONField(_('Function Arguments'), blank=True, null=True)
    
    # API call results
    api_request = models.JSONField(_('API Request'), blank=True, null=True)
    api_response = models.JSONField(_('API Response'), blank=True, null=True)
    
    # Processing metadata
    processing_time = models.FloatField(_('Processing Time (s)'), blank=True, null=True)
    token_usage = models.JSONField(_('Token Usage'), blank=True, null=True)
    
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Processed Message')
        verbose_name_plural = _('Processed Messages')
    
    def __str__(self):
        return f"Result for Message {self.message.id}"
