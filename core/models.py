from django.db import models
from django.utils.translation import gettext_lazy as _

class RateLimitLog(models.Model):
    """
    Model to track API rate limiting
    """
    # Target details
    target_type = models.CharField(_('Target Type'), max_length=50,
                                 help_text=_('Type of rate-limited target (e.g., openai, api_endpoint)'))
    target_id = models.CharField(_('Target ID'), max_length=255,
                               help_text=_('Identifier for the rate-limited target'))
    
    # Rate limit details
    request_count = models.PositiveIntegerField(_('Request Count'), default=1)
    window_start = models.DateTimeField(_('Window Start'))
    window_end = models.DateTimeField(_('Window End'))
    limit = models.PositiveIntegerField(_('Limit'))
    
    # Request details
    last_request_at = models.DateTimeField(_('Last Request At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Rate Limit Log')
        verbose_name_plural = _('Rate Limit Logs')
        indexes = [
            models.Index(fields=['target_type', 'target_id']),
            models.Index(fields=['window_start', 'window_end']),
        ]
        unique_together = ('target_type', 'target_id', 'window_start')
    
    def __str__(self):
        return f"{self.target_type}:{self.target_id} - {self.request_count}/{self.limit}"


class SystemConfig(models.Model):
    """
    Model to store system-wide configuration
    """
    key = models.CharField(_('Key'), max_length=100, unique=True)
    value = models.JSONField(_('Value'))
    description = models.TextField(_('Description'), blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('System Configuration')
        verbose_name_plural = _('System Configurations')
    
    def __str__(self):
        return self.key


class ErrorLog(models.Model):
    """
    Model to log errors and exceptions
    """
    ERROR_LEVEL_CHOICES = [
        ('info', _('Info')),
        ('warning', _('Warning')),
        ('error', _('Error')),
        ('critical', _('Critical')),
    ]
    
    # Error details
    level = models.CharField(_('Level'), max_length=20, choices=ERROR_LEVEL_CHOICES, default='error')
    message = models.TextField(_('Message'))
    traceback = models.TextField(_('Traceback'), blank=True, null=True)
    
    # Context
    component = models.CharField(_('Component'), max_length=100, blank=True, null=True,
                               help_text=_('System component where the error occurred'))
    context = models.JSONField(_('Context'), blank=True, null=True,
                             help_text=_('Additional context for the error'))
    
    # Related objects
    related_object_type = models.CharField(_('Related Object Type'), max_length=100, blank=True, null=True)
    related_object_id = models.CharField(_('Related Object ID'), max_length=255, blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    resolved = models.BooleanField(_('Resolved'), default=False)
    resolved_at = models.DateTimeField(_('Resolved At'), blank=True, null=True)
    resolution_notes = models.TextField(_('Resolution Notes'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Error Log')
        verbose_name_plural = _('Error Logs')
        indexes = [
            models.Index(fields=['level']),
            models.Index(fields=['component']),
            models.Index(fields=['created_at']),
            models.Index(fields=['resolved']),
        ]
    
    def __str__(self):
        return f"{self.level}: {self.message[:50]}..."
