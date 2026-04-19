from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import Payment, User
from users.serializers import PaymentSerializer, UserProfileSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями системы.

    Предоставляет полный набор операций CRUD для пользователей.
    Регистрация новых пользователей доступна без аутентификации,
    остальные операции требуют аутентификации.
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        """
        Определяет классы разрешений в зависимости от выполняемого действия.

            Для создания пользователя (action == "create") разрешение AllowAny
            (регистрация доступна всем). Для всех остальных действий требуется
            аутентификация (IsAuthenticated).

            Returns:
                list: Список классов разрешений для текущего действия.
        """

        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Выполняет дополнительные действия при создании пользователя.

            Устанавливает флаг is_active=True и корректно сохраняет пароль
            с хешированием перед сохранением в базу данных.

            Args:
                serializer (UserSerializer): Сериализатор с валидированными данными пользователя.
        """

        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UserProfileView(generics.RetrieveAPIView):
    """
    API‑представление для получения профиля пользователя.

    Позволяет аутентифицированным пользователям просматривать
    свой профиль по email. Включает основную информацию о пользователе
    и историю его платежей.
    """

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "email"
    permission_classes = (IsAuthenticated,)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления платежами пользователей.

    Предоставляет полный набор операций CRUD для платежей с возможностью
    фильтрации и сортировки. Доступ ограничен аутентифицированными пользователями.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ("course", "lesson", "payment_method")
    ordering_fields = ("payment_date",)
    permission_classes = (IsAuthenticated,)
