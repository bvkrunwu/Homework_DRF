from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models

from config import settings
from lms.models import Course, Lesson


class UserCustomManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Поле электронной почты должно быть заполнено.")
        if not password:
            raise ValueError("Пароль должен быть указан.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        if not password:
            raise ValueError("Суперпользователь должен иметь пароль.")

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(unique=True, verbose_name="Почта", help_text="Укажите почту")
    phone_number = models.CharField(
        max_length=35, verbose_name="Номер телефона", blank=True, null=True, help_text="Введите номер телефона"
    )
    country = models.CharField(
        max_length=100, verbose_name="Страна", blank=True, null=True, help_text="Укажите страну"
    )

    avatar = models.ImageField(
        upload_to="users/avatars/", verbose_name="Аватар", blank=True, null=True, help_text="Загрузите аватар"
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserCustomManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счёт"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    course = models.ForeignKey(
        Course, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Оплаченный курс"
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Оплаченный урок"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, verbose_name="Способ оплаты")

    def __str__(self):
        return f"Платеж от {self.user} на сумму {self.amount} ({self.get_payment_method_display()})"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def clean(self):
        if not self.course and not self.lesson:
            raise ValidationError("Должен быть указан либо курс, либо урок.")
        if self.course and self.lesson:
            raise ValidationError("Нельзя оплатить и курс и, урок одновременно.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
