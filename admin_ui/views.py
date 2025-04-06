from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
from django.contrib import messages as django_messages # Renamed to avoid conflict

from core.models import ErrorLog, SystemConfig
from message_receiver.models import MessageSource, Message
from api_connector.models import APIConfiguration, APIEndpoint
from openai_processor.models import PromptTemplate, FunctionCallLog
from openai_processor.forms import PromptTemplateForm # Import the form


class AdminUILoginView(LoginView):
    """Custom login view for the admin UI"""
    template_name = 'admin_ui/login.html'


@login_required
def dashboard(request):
    """Dashboard view showing overview of the system"""
    # Get counts for dashboard cards
    message_sources_count = MessageSource.objects.count()
    api_connections_count = APIConfiguration.objects.count()
    
    # Get counts for last 24 hours
    last_24h = timezone.now() - timedelta(hours=24)
    messages_count_24h = Message.objects.filter(received_at__gte=last_24h).count()
    errors_count_24h = ErrorLog.objects.filter(created_at__gte=last_24h).count()
    
    # Get recent messages
    recent_messages = Message.objects.select_related('source').order_by('-received_at')[:10]
    
    # Get recent function calls
    recent_function_calls = FunctionCallLog.objects.order_by('-created_at')[:10]
    
    context = {
        'message_sources_count': message_sources_count,
        'api_connections_count': api_connections_count,
        'messages_count_24h': messages_count_24h,
        'errors_count_24h': errors_count_24h,
        'recent_messages': recent_messages,
        'recent_function_calls': recent_function_calls,
    }
    
    return render(request, 'admin_ui/dashboard/index.html', context)


@login_required
def system_status(request):
    """System status view showing system health and configuration"""
    # Get system configurations
    system_configs = SystemConfig.objects.all()
    
    # Get error counts by level
    error_counts = ErrorLog.objects.values('level').annotate(count=Count('level'))
    
    # Get message counts by status
    message_counts = Message.objects.values('status').annotate(count=Count('status'))
    
    # Get API endpoint counts by API configuration
    api_endpoint_counts = APIEndpoint.objects.values('api_config__name').annotate(count=Count('api_config'))
    
    context = {
        'system_configs': system_configs,
        'error_counts': error_counts,
        'message_counts': message_counts,
        'api_endpoint_counts': api_endpoint_counts,
    }
    
    return render(request, 'admin_ui/dashboard/system_status.html', context)


@login_required
def message_sources(request):
    """List all message sources"""
    sources = MessageSource.objects.all()
    
    context = {
        'sources': sources,
    }
    
    return render(request, 'admin_ui/message_sources/index.html', context)


@login_required
def message_source_detail(request, source_id):
    """Detail view for a message source"""
    source = get_object_or_404(MessageSource, id=source_id)
    
    # Get recent messages for this source
    recent_messages = Message.objects.filter(source=source).order_by('-received_at')[:20]
    
    context = {
        'source': source,
        'recent_messages': recent_messages,
    }
    
    return render(request, 'admin_ui/message_sources/detail.html', context)


@login_required
def message_source_create(request):
    """Create a new message source"""
    # This is a placeholder for now
    # In a real implementation, this would handle form submission
    return render(request, 'admin_ui/message_sources/create.html')


@login_required
def api_connections(request):
    """List all API connections"""
    connections = APIConfiguration.objects.all()
    
    context = {
        'connections': connections,
    }
    
    return render(request, 'admin_ui/api_connections/index.html', context)


@login_required
def api_connection_detail(request, connection_id):
    """Detail view for an API connection"""
    connection = get_object_or_404(APIConfiguration, id=connection_id)
    
    # Get endpoints for this connection
    endpoints = APIEndpoint.objects.filter(api_config=connection)
    
    context = {
        'connection': connection,
        'endpoints': endpoints,
    }
    
    return render(request, 'admin_ui/api_connections/detail.html', context)


@login_required
def api_connection_create(request):
    """Create a new API connection"""
    # This is a placeholder for now
    # In a real implementation, this would handle form submission
    return render(request, 'admin_ui/api_connections/create.html')


@login_required
def prompt_templates(request):
    """List all prompt templates"""
    templates = PromptTemplate.objects.all()
    
    context = {
        'templates': templates,
    }
    
    return render(request, 'admin_ui/prompt_templates/index.html', context)


@login_required
def prompt_template_detail(request, template_id):
    """Detail view for a prompt template"""
    template = get_object_or_404(PromptTemplate, id=template_id)
    
    context = {
        'template': template,
    }
    
    return render(request, 'admin_ui/prompt_templates/detail.html', context)


@login_required
def prompt_template_create(request):
    """Create a new prompt template"""
    if request.method == 'POST':
        form = PromptTemplateForm(request.POST)
        if form.is_valid():
            template = form.save()
            django_messages.success(request, f"Prompt template '{template.name}' created successfully.")
            return redirect('admin_ui:prompt_template_detail', template_id=template.id)
    else:
        form = PromptTemplateForm()
    
    context = {
        'form': form,
        'form_title': 'Create New Prompt Template'
    }
    return render(request, 'admin_ui/prompt_templates/form.html', context) # Use a generic form template


@login_required
def prompt_template_edit(request, template_id):
    """Edit an existing prompt template"""
    template = get_object_or_404(PromptTemplate, id=template_id)
    
    if request.method == 'POST':
        form = PromptTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            django_messages.success(request, f"Prompt template '{template.name}' updated successfully.")
            return redirect('admin_ui:prompt_template_detail', template_id=template.id)
    else:
        form = PromptTemplateForm(instance=template)
        
    context = {
        'form': form,
        'template': template,
        'form_title': f'Edit Prompt Template: {template.name}'
    }
    return render(request, 'admin_ui/prompt_templates/form.html', context) # Reuse the generic form template


@login_required
def messages(request):
    """List all messages"""
    messages_list = Message.objects.select_related('source').order_by('-received_at')[:100]
    
    context = {
        'messages': messages_list,
    }
    
    return render(request, 'admin_ui/messages/index.html', context)


@login_required
def message_detail(request, message_id):
    """Detail view for a message"""
    message = get_object_or_404(Message, id=message_id)
    
    # Try to get the processed result
    try:
        processed_result = message.processed_result
    except:
        processed_result = None
    
    # Get function calls for this message
    function_calls = FunctionCallLog.objects.filter(message=message)
    
    context = {
        'message': message,
        'processed_result': processed_result,
        'function_calls': function_calls,
    }
    
    return render(request, 'admin_ui/messages/detail.html', context)


@login_required
def function_calls(request):
    """List all function calls"""
    calls = FunctionCallLog.objects.select_related('message').order_by('-created_at')[:100]
    
    context = {
        'function_calls': calls,
    }
    
    return render(request, 'admin_ui/function_calls/index.html', context)


@login_required
def function_call_detail(request, call_id):
    """Detail view for a function call"""
    call = get_object_or_404(FunctionCallLog, id=call_id)
    
    context = {
        'call': call,
    }
    
    return render(request, 'admin_ui/function_calls/detail.html', context)


@login_required
def error_logs(request):
    """List all error logs"""
    logs = ErrorLog.objects.order_by('-created_at')[:100]
    
    context = {
        'logs': logs,
    }
    
    return render(request, 'admin_ui/error_logs/index.html', context)


@login_required
def error_log_detail(request, log_id):
    """Detail view for an error log"""
    log = get_object_or_404(ErrorLog, id=log_id)
    
    context = {
        'log': log,
    }
    
    return render(request, 'admin_ui/error_logs/detail.html', context)


@login_required
def system_config(request):
    """View and edit system configuration"""
    configs = SystemConfig.objects.all()
    
    context = {
        'configs': configs,
    }
    
    return render(request, 'admin_ui/system_config/index.html', context)
