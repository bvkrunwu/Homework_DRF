from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from users.models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "user", "payment_date", "course", "lesson", "amount", "payment_method"]
        read_only_fields = ["user", "payment_date"]


class UserProfileSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ["email", "phone_number", "country", "avatar", "payments"]


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "phone_number", "country", "avatar", "is_staff", "is_active"]
