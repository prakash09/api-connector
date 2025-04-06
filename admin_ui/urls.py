from django.urls import path
from . import views

app_name = 'admin_ui'

urlpatterns = [
    # Authentication
    path('login/', views.AdminUILoginView.as_view(), name='login'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('system-status/', views.system_status, name='system_status'),
    
    # Message Sources
    path('message-sources/', views.message_sources, name='message_sources'),
    path('message-sources/<int:source_id>/', views.message_source_detail, name='message_source_detail'),
    path('message-sources/create/', views.message_source_create, name='message_source_create'),
    
    # API Connections
    path('api-connections/', views.api_connections, name='api_connections'),
    path('api-connections/<int:connection_id>/', views.api_connection_detail, name='api_connection_detail'),
    path('api-connections/create/', views.api_connection_create, name='api_connection_create'),
    
    # Prompt Templates
    path('prompt-templates/', views.prompt_templates, name='prompt_templates'),
    path('prompt-templates/<int:template_id>/', views.prompt_template_detail, name='prompt_template_detail'),
    path('prompt-templates/create/', views.prompt_template_create, name='prompt_template_create'),
    path('prompt-templates/<int:template_id>/edit/', views.prompt_template_edit, name='prompt_template_edit'), # Added edit URL
    
    # Messages
    path('messages/', views.messages, name='messages'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    
    # Function Calls
    path('function-calls/', views.function_calls, name='function_calls'),
    path('function-calls/<int:call_id>/', views.function_call_detail, name='function_call_detail'),
    
    # Error Logs
    path('error-logs/', views.error_logs, name='error_logs'),
    path('error-logs/<int:log_id>/', views.error_log_detail, name='error_log_detail'),
    
    # System Config
    path('system-config/', views.system_config, name='system_config'),
]
