from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import AccountApplication, ApplicationStatus, ApplicationLog

@shared_task
def delete_old_pending_applications():
    """
    Delete applications that are pending for more than 20 days
    Runs daily via Celery Beat
    """
    threshold_date = timezone.now() - timedelta(days=20)
    
    old_applications = AccountApplication.objects.filter(
        status=ApplicationStatus.PENDING,
        application_date__lt=threshold_date
    )
    
    count = old_applications.count()
    
    # Log before deletion
    for app in old_applications:
        ApplicationLog.objects.create(
            application=app,
            action='APPLICATION_AUTO_DELETED',
            details=f'Deleted automatically after 20 days of pending status'
        )
    
    # Delete applications
    old_applications.delete()
    
    return f'Deleted {count} old pending applications'