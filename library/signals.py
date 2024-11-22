from django_celery_beat.models import PeriodicTask, IntervalSchedule
from datetime import timedelta

def setup_periodic_tasks(sender, **kwargs):
    # Check if the periodic task exists, otherwise create it
    task_name = "Send Due Date Reminders"  # Use the name of the task
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=1,  # Change the frequency as needed
        period=IntervalSchedule.MINUTES,
    )

    task, created = PeriodicTask.objects.get_or_create(
        name=task_name,
        defaults={
            'task': 'library.tasks.send_due_date_notifications',  # Replace with the path to your task
            'interval': schedule,
        }
    )

    if not created:
        # If the task already exists, update it if necessary
        task.interval = schedule
        task.save()

# Connect the signal to ensure periodic tasks are set up
from django.db.models.signals import post_migrate
post_migrate.connect(setup_periodic_tasks)





##from django.db.models.signals import post_migrate
##from django.dispatch import receiver
##from django_celery_beat.models import CrontabSchedule, PeriodicTask
##
##@receiver(post_migrate)
##def setup_periodic_tasks(sender, **kwargs):
##    # Create a crontab schedule to run daily at 12:01 PM
##    schedule, created = CrontabSchedule.objects.get_or_create(
##        minute='30',
##        hour='16',
##        day_of_week='*',  # Every day
##        day_of_month='*',
##        month_of_year='*',
##        timezone='Asia/Kolkata',  # Use the appropriate timezone
##    )
##
##    # Create the periodic task if it doesn't exist
##    PeriodicTask.objects.get_or_create(
##        crontab=schedule,  # Use crontab schedule instead of interval
##        name="Send Due Date Notifications",
##        task="library.tasks.send_due_date_notifications",  # Full path to the task
##    )
##