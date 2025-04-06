from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import MessageSource, Message, ProcessedMessage

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ('external_id', 'status', 'received_at', 'processed_at')
    readonly_fields = ('external_id', 'status', 'received_at', 'processed_at')
    can_delete = False
    max_num = 10
    show_change_link = True

class ProcessedMessageInline(admin.StackedInline):
    model = ProcessedMessage
    extra = 0
    fields = ('prompt', 'function_name', 'function_arguments', 'processing_time')
    readonly_fields = ('prompt', 'function_name', 'function_arguments', 'processing_time')
    can_delete = False
    max_num = 1
    show_change_link = True

@admin.register(MessageSource)
class MessageSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'webhook_url_path', 'is_active')
    list_filter = ('source_type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'webhook_url_path')
    inlines = [MessageInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'source_type', 'description', 'is_active')
        }),
        (_('Configuration'), {
            'fields': ('config',),
            'classes': ('collapse',),
        }),
        (_('Webhook Configuration'), {
            'fields': ('webhook_url_path', 'webhook_secret'),
            'classes': ('collapse',),
        }),
        (_('Processing Configuration'), {
            'fields': ('prompt_template',),
            'classes': ('collapse',),
        }),
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'external_id', 'status', 'received_at', 'processed_at')
    list_filter = ('status', 'source', 'received_at')
    search_fields = ('external_id', 'content_text')
    readonly_fields = ('received_at',)
    inlines = [ProcessedMessageInline]
    fieldsets = (
        (None, {
            'fields': ('source', 'external_id', 'status', 'status_message')
        }),
        (_('Content'), {
            'fields': ('content', 'content_text'),
        }),
        (_('Processing'), {
            'fields': ('priority', 'received_at', 'processed_at'),
        }),
    )
    
    def has_add_permission(self, request):
        # Messages should be created through the API, not manually
        return False

@admin.register(ProcessedMessage)
class ProcessedMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'function_name', 'processing_time', 'created_at')
    list_filter = ('created_at', 'function_name')
    search_fields = ('function_name', 'function_arguments')
    readonly_fields = ('message', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('message', 'created_at')
        }),
        (_('OpenAI Processing'), {
            'fields': ('prompt', 'openai_response', 'token_usage'),
        }),
        (_('Function Calling'), {
            'fields': ('function_name', 'function_arguments'),
        }),
        (_('API Call'), {
            'fields': ('api_request', 'api_response'),
        }),
        (_('Performance'), {
            'fields': ('processing_time',),
        }),
    )
    
    def has_add_permission(self, request):
        # ProcessedMessages should be created by the system, not manually
        return False
