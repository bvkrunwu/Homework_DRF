from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

User = get_user_model()


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


@shared_task
def deactivate_inactive_users():
    """
    Фоновая задача для деактивации пользователей,
    которые не заходили в систему более 30 дней.
    """

    inactive_period = timezone.now() - timedelta(days=30)

    inactive_users = User.objects.filter(is_active=True, last_login__lte=inactive_period)

    count = inactive_users.update(is_active=False)

    return f"Деактивировано {count} пользователей"
