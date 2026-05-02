from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_course_update_notification(subject, message, recipient_list):
    """
    Отправляет уведомление об обновлении курса подписчикам.
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=True,
    )
