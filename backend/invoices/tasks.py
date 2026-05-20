from celery import shared_task

@shared_task
def email_check():
    print("Checking for emails...")
