from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models

from config import settings


class UserCustomManager(BaseUserManager):
    """
    Кастомный менеджер для модели User.

    Предоставляет методы для создания обычных пользователей и суперпользователей
    с валидацией обязательных полей.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Создаёт и сохраняет пользователя с email и паролем.

            Выполняет валидацию обязательных полей, нормализует email,
            устанавливает пароль и сохраняет пользователя в базе данных.

            Args:
                email (str): Адрес электронной почты пользователя.
                password (str, optional): Пароль пользователя. По умолчанию None.
                **extra_fields: Дополнительные поля для модели пользователя.

            Raises:
                ValueError: Если email или пароль не указаны.

            Returns:
                User: Созданный экземпляр пользователя.
        """

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
        """
        Создаёт суперпользователя с повышенными правами.

            Устанавливает обязательные флаги для суперпользователя (is_staff, is_superuser, is_active)
            и вызывает create_user для фактического создания записи.

            Args:
                email (str): Адрес электронной почты суперпользователя.
                password (str): Пароль суперпользователя.
                **extra_fields: Дополнительные поля для модели суперпользователя.

            Raises:
                ValueError: Если пароль не указан или если флаги is_staff/is_superuser
                    не установлены в True.

            Returns:
                User: Созданный экземпляр суперпользователя.
        """

        if not password:
            raise ValueError("Суперпользователь должен иметь пароль.")

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя.

    Использует email в качестве основного идентификатора вместо username.
    Включает поля для контактной информации, аватара и флагов доступа.
    """

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
        """
        Мета‑опции для модели User.

            Задаёт человеко‑читаемые названия модели в единственном
            и множественном числе для отображения в админ‑панели.
        """

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        """
        Возвращает строковое представление пользователя.

            Используется в админке Django и других интерфейсах для отображения объекта.

            Returns:
                str: Адрес электронной почты пользователя.
        """

        return self.email


class Payment(models.Model):
    """
    Модель платежа за курс или урок.

    Хранит информацию о платежах пользователей, включая сумму, дату, способ оплаты
    и связь с курсом или уроком. Содержит валидацию взаимоисключающих условий.
    """

    PAYMENT_METHOD_CHOICES = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счёт"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    course = models.ForeignKey(
        "lms.Course", on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Оплаченный курс"
    )
    lesson = models.ForeignKey(
        "lms.Lesson", on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Оплаченный урок"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, verbose_name="Способ оплаты")

    def __str__(self):
        """
        Возвращает строковое представление платежа.

            Используется для отображения в админке и других интерфейсах.

            Returns:
                str: Форматированная строка с информацией о платеже.
        """

        return f"Платеж от {self.user} на сумму {self.amount} ({self.get_payment_method_display()})"

    class Meta:
        """
        Мета‑опции для модели Payment.

            Задаёт человеко‑читаемые названия модели в единственном
            и множественном числе для отображения в админ‑панели.
        """

        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def clean(self):
        """
        Выполняет дополнительную валидацию перед сохранением платежа.

            Проверяет, что:
            - указан либо курс, либо урок (не оба одновременно);
            - хотя бы один из них указан.

            Raises:
                ValidationError: Если условия валидации не выполнены.
        """

        if not self.course and not self.lesson:
            raise ValidationError("Должен быть указан либо курс, либо урок.")
        if self.course and self.lesson:
            raise ValidationError("Нельзя оплатить и курс и, урок одновременно.")

    def save(self, *args, **kwargs):
        """
        Сохраняет платёж в базе данных с предварительной валидацией.

            Вызывает full_clean() для запуска всех проверок валидации перед сохранением.

            Args:
                *args: Позиционные аргументы для метода save.
                **kwargs: Именованные аргументы для метода save.
        """

        self.full_clean()
        super().save(*args, **kwargs)


class StripePayment(models.Model):
    """
    Модель для хранения данных об оплате курсов через Stripe.

    Связывает пользователя, курс и данные транзакции от платежной системы.
    Используется для отслеживания статуса оплаты и предоставления доступа к контенту.
    """

    course = models.ForeignKey("lms.Course", on_delete=models.CASCADE, verbose_name="Курс")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Пользователь",
        help_text="Укажите пользователя",
    )
    amount = models.PositiveIntegerField(verbose_name="сумма платежа", help_text="Укажите сумму платежа")
    session_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="id сессии", help_text="Укажите id сессии"
    )
    link = models.URLField(
        max_length=600, blank=True, null=True, verbose_name="Ссылка на оплату", help_text="Укажите ссылку на оплату"
    )
    status = models.CharField(max_length=20, default="pending")

    class Meta:
        """
        Мета‑опции для модели StripePayment.

            Задаёт человеко‑читаемые названия модели в единственном
            и множественном числе для отображения в админ‑панели.
        """

        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        """
        Возвращает строковое представление платежа.

            Создаёт читаемую строку для отображения объекта в списках,
            админ-панели и отладочной информации.

            Returns:
                str: Форматированная строка с номером и суммой платежа.
        """

        return f"Платёж № {self.id} на {self.amount} руб."
