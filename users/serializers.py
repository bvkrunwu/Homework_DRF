from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from users.models import Payment, StripePayment, User


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.

    Преобразует экземпляры модели Payment в JSON‑формат и обратно.
    Используется для операций с платежами: создания, просмотра и обновления.
    """

    class Meta:
        """
        Мета‑опции для PaymentSerializer.

            Определяет модель и поля для сериализации, а также поля, доступные только для чтения.
        """

        model = Payment
        fields = ["id", "user", "payment_date", "course", "lesson", "amount", "payment_method"]
        read_only_fields = ["user", "payment_date"]


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор профиля пользователя с историей платежей.

    Включает основную информацию о пользователе и вложенные данные о его платежах.
    Используется для отображения детальной информации о профиле пользователя.
    """

    payments = PaymentSerializer(read_only=True, many=True)

    class Meta:
        """
        Мета‑опции для UserProfileSerializer.

            Определяет модель и набор полей для представления профиля пользователя,
            включая вложенный сериализатор платежей.
        """

        model = User
        fields = ["email", "phone_number", "country", "avatar", "payments"]


class UserSerializer(ModelSerializer):
    """
    Базовый сериализатор для модели User.

    Используется для операций со списком пользователей и базовыми данными пользователя,
    включая управление правами доступа (is_staff, is_active).
    """

    class Meta:
        """
        Мета‑опции для UserSerializer.

            Определяет модель и полный набор полей для сериализации пользователя,
            включая идентификационные данные, контактную информацию и флаги доступа.
        """

        model = User
        fields = ["id", "email", "password", "phone_number", "country", "avatar", "is_staff", "is_active"]


class StripePaymentSerializer(ModelSerializer):
    """
    Сериализатор для модели StripePayment.

    Преобразует экземпляры модели StripePayment в JSON-формат и обратно.
    Используется для создания и отображения данных о платежах, обрабатываемых через Stripe.
    """

    class Meta:
        """
        Мета-опции для StripePaymentSerializer.
        Определяет модель и набор всех полей для сериализации.
        """

        model = StripePayment
        fields = "__all__"
