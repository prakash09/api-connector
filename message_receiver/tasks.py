import logging
from celery import shared_task

from django.db import transaction
from django.utils import timezone

from .models import Message
from .services import MessageReceiverService

logger = logging.getLogger('api_hub.message_receiver.tasks')

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
    acks_late=True
)
def process_message_task(self, message_id):
    """
    Process a message asynchronously
    
    Args:
        message_id: ID of the message to process
    """
    logger.info(f"Processing message {message_id}")
    
    try:
        # Get the message
        message = Message.objects.get(id=message_id)
        
        # Skip if already processed or processing
        if message.status in ('processed', 'processing'):
            logger.info(f"Message {message_id} already processed or processing, skipping")
            return
        
        # Process the message
        service = MessageReceiverService()
        service.process_message(message)
        
        logger.info(f"Successfully processed message {message_id}")
        
    except Message.DoesNotExist:
        logger.error(f"Message {message_id} not found")
        raise
        
    except Exception as e:
        logger.exception(f"Error processing message {message_id}: {str(e)}")
        
        # Update message status if it exists
        try:
            message = Message.objects.get(id=message_id)
            with transaction.atomic():
                message.status = 'failed'
                message.status_message = str(e)
                message.save(update_fields=['status', 'status_message'])
        except (Message.DoesNotExist, Exception) as inner_e:
            logger.exception(f"Error updating message status: {str(inner_e)}")
        
        # Re-raise for retry
        raise


@shared_task
def process_pending_messages():
    """
    Process all pending messages
    """
    logger.info("Processing pending messages")
    
    # Get pending messages, ordered by priority (higher first) and then by received time
    pending_messages = Message.objects.filter(
        status='received'
    ).order_by('-priority', 'received_at')
    
    count = pending_messages.count()
    logger.info(f"Found {count} pending messages")
    
    # Process each message
    for message in pending_messages:
        process_message_task.delay(message.id)
    
    return f"Queued {count} messages for processing"


@shared_task
def retry_failed_messages(max_age_hours=24):
    """
    Retry failed messages
    
    Args:
        max_age_hours: Maximum age of messages to retry in hours
    """
    logger.info(f"Retrying failed messages (max age: {max_age_hours} hours)")
    
    # Calculate cutoff time
    cutoff_time = timezone.now() - timezone.timedelta(hours=max_age_hours)
    
    # Get failed messages that are not too old
    failed_messages = Message.objects.filter(
        status='failed',
        received_at__gte=cutoff_time
    ).order_by('-priority', 'received_at')
    
    count = failed_messages.count()
    logger.info(f"Found {count} failed messages to retry")
    
    # Reset status and queue for processing
    for message in failed_messages:
        with transaction.atomic():
            message.status = 'received'
            message.status_message = f"Retrying after failure: {message.status_message}"
            message.save(update_fields=['status', 'status_message'])
        
        process_message_task.delay(message.id)
    
    return f"Queued {count} failed messages for retry"
