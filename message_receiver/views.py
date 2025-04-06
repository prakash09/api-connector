import json
import logging
from typing import Dict, Any

from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from .models import MessageSource, Message
from .services import MessageReceiverService

logger = logging.getLogger('api_hub.message_receiver.views')

@csrf_exempt
@require_http_methods(["POST"])
def webhook_receiver(request: HttpRequest, path: str) -> HttpResponse:
    """
    Generic webhook receiver for all webhook-based message sources
    
    Args:
        request: HTTP request
        path: Webhook path
        
    Returns:
        HTTP response
    """
    try:
        # Get request body
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            body = request.body.decode('utf-8')
        
        # Get request headers
        headers = {key: value for key, value in request.headers.items()}
        
        # Process the webhook
        service = MessageReceiverService()
        message = service.process_webhook(path, body, headers)
        
        if message:
            return JsonResponse({
                'status': 'success',
                'message': f"Webhook received and processed",
                'message_id': str(message.id)
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': f"No message source found for webhook path: {path}"
            }, status=404)
            
    except Exception as e:
        logger.exception(f"Error processing webhook: {str(e)}")
        
        return JsonResponse({
            'status': 'error',
            'message': f"Error processing webhook: {str(e)}"
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_message_receiver(request: Request) -> Response:
    """
    API endpoint for receiving messages
    
    Args:
        request: REST framework request
        
    Returns:
        REST framework response
    """
    try:
        # Validate request data
        source_id = request.data.get('source_id')
        content = request.data.get('content')
        external_id = request.data.get('external_id')
        priority = request.data.get('priority', 0)
        
        if not source_id:
            return Response({
                'status': 'error',
                'message': "Missing required field: source_id"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if not content:
            return Response({
                'status': 'error',
                'message': "Missing required field: content"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the message source
        try:
            source = MessageSource.objects.get(id=source_id, is_active=True)
        except MessageSource.DoesNotExist:
            return Response({
                'status': 'error',
                'message': f"Message source not found: {source_id}"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Process the message
        service = MessageReceiverService()
        message = service.receive_message(source, content, external_id, priority)
        
        # Process the message asynchronously if Celery is configured
        if hasattr(settings, 'CELERY_BROKER_URL') and settings.CELERY_BROKER_URL:
            from .tasks import process_message_task
            process_message_task.delay(message.id)
        else:
            # Process synchronously
            processed = service.process_message(message)
            
            return Response({
                'status': 'success',
                'message': "Message received and processed",
                'message_id': str(message.id),
                'processed': {
                    'function_name': processed.function_name,
                    'processing_time': processed.processing_time
                }
            })
        
        return Response({
            'status': 'success',
            'message': "Message received and queued for processing",
            'message_id': str(message.id)
        })
            
    except Exception as e:
        logger.exception(f"Error receiving message: {str(e)}")
        
        return Response({
            'status': 'error',
            'message': f"Error receiving message: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def message_status(request: Request, message_id: str) -> Response:
    """
    Get the status of a message
    
    Args:
        request: REST framework request
        message_id: Message ID
        
    Returns:
        REST framework response
    """
    try:
        # Get the message
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return Response({
                'status': 'error',
                'message': f"Message not found: {message_id}"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get processed result if available
        processed_data = None
        try:
            processed = message.processed_result
            if processed:
                processed_data = {
                    'function_name': processed.function_name,
                    'function_arguments': processed.function_arguments,
                    'processing_time': processed.processing_time,
                    'created_at': processed.created_at.isoformat()
                }
        except Exception:
            pass
        
        # Return message status
        return Response({
            'status': 'success',
            'message': {
                'id': str(message.id),
                'source': {
                    'id': str(message.source.id),
                    'name': message.source.name,
                    'type': message.source.source_type
                },
                'external_id': message.external_id,
                'status': message.status,
                'status_message': message.status_message,
                'received_at': message.received_at.isoformat(),
                'processed_at': message.processed_at.isoformat() if message.processed_at else None,
                'processed_result': processed_data
            }
        })
            
    except Exception as e:
        logger.exception(f"Error getting message status: {str(e)}")
        
        return Response({
            'status': 'error',
            'message': f"Error getting message status: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
