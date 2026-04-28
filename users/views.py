import stripe
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import Payment, StripePayment, User
from users.serializers import PaymentSerializer, StripePaymentSerializer, UserProfileSerializer, UserSerializer
from users.services import create_stripe_price, create_stripe_session


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


class StripePaymentCreateApiView(CreateAPIView):
    """
    API View для создания платежа через Stripe.

        Обрабатывает запрос на создание платежа, взаимодействует с API Stripe
        для создания продукта, цены и сессии оплаты, а затем сохраняет
        ссылку на оплату в базу данных.
    """

    serializer_class = StripePaymentSerializer
    queryset = StripePayment.objects.all()

    def perform_create(self, serializer):
        """
        Создаёт платёж и инициирует процесс оплаты через Stripe.

            Этот метод вызывается при успешной валидации данных. Он создаёт
            продукт и цену в Stripe, затем создаёт Checkout Session для
            получения ссылки на оплату. После этого сохраняет все данные,
            включая ссылку, в базу данных.

            Args:
                serializer (StripePaymentSerializer): Сериализатор с валидированными данными.

            Логика метода:
                1. Извлекает данные о курсе и сумме из сериализатора.
                2. Создаёт продукт в Stripe на основе названия курса.
                3. Создаёт цену для продукта, используя сумму из запроса.
                4. Создаёт Checkout Session, получая ID сессии и ссылку на оплату.
                5. Сохраняет объект StripePayment с полученными данными.
        """

        validated_data = serializer.validated_data
        amount = validated_data.get("amount")
        course = validated_data.get("course")

        # 1. Создаём продукт в Stripe
        product = stripe.Product.create(name=course.title)

        # 2. Создаём цену для этого продукта
        price = create_stripe_price(amount, product.id)

        # 3. Создаём сессию оплаты
        session_id, payment_link = create_stripe_session(price)

        # 4. Сохраняем платёж в нашу базу данных
        serializer.save(user=self.request.user, session_id=session_id, link=payment_link, status="pending")
