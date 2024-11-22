from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from datetime import timedelta
from .models import BorrowRecord
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def setup_periodic_tasks(sender, **kwargs):
    setup_periodic_tasks(sender, **kwargs)

@shared_task
def send_due_date_notifications():
    # Set the target date (3 days before the due date)
    target_date = now().date() + timedelta(days=3)
    
    # Filter BorrowRecords for books due within the next 3 days
    records = BorrowRecord.objects.filter(return_date__lte=target_date, return_date__gte=now().date())
    
    print(f"Found {len(records)} records to notify.")
    
    # Loop through each record and send an email
    for record in records:
        subject = "Library Book Due Soon!"
        message = f"Dear {record.borrower.username},\n\nThe book '{record.book.title}' is due for return on {record.return_date}. Please make sure to return it on time."
        recipient = [record.borrower.email]
        
        print(f"Sending email to: {record.borrower.email}")
        send_mail(subject, message, 'noreply@library.com', recipient)
    
    print(f"{len(records)} notifications sent.")
    
    
def setup_periodic_tasks(sender, **kwargs):
    # Create an interval schedule to run every day
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=1,  # Interval of 1 day
        period=IntervalSchedule.MINUTES,  # Daily frequency
    )

    task_name = "Send Due Date Reminders"
    
    # Create or update the periodic task
    task, created = PeriodicTask.objects.get_or_create(
        name=task_name,
        defaults={
            'task': 'library.tasks.send_due_date_notifications',  # Full path to the task
            'interval': schedule,
        }
    )

    if not created:
        # If the task exists, just update the schedule
        task.interval = schedule
        task.save()
