from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course, CourseSubscription, Lesson
from lms.serializers import CourseDetailSerializer, CourseSerializer, LessonSerializer
from users.permissions import IsModer, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления курсами.

    Предоставляет полный набор операций CRUD для курсов с разной логикой
    сериализации и разрешений для различных действий.
    """

    queryset = Course.objects.all()

    def get_serializer_class(self):
        """
        Определяет класс сериализатора в зависимости от выполняемого действия.

            Для детального просмотра (retrieve) используется CourseDetailSerializer
            (с дополнительной информацией), для остальных действий — CourseSerializer.

            Returns:
                Serializer class: Класс сериализатора для текущего действия.
        """

        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        """
        Выполняет дополнительные действия при создании курса.

            Устанавливает текущего пользователя в качестве владельца курса
            перед сохранением в базу данных.

            Args:
                serializer (CourseSerializer): Сериализатор с валидированными данными.
        """

        course = serializer.save()
        course.owner = self.request.user
        course.save()

    def get_permissions(self):
        """
        Настраивает классы разрешений в зависимости от выполняемого действия.

            Логика разрешений:
            - create: запрещено модераторам (~IsModer);
            - update/retrieve: разрешено модераторам ИЛИ владельцам (IsModer | IsOwner);
            - destroy: разрешено не‑модераторам ИЛИ владельцам (~IsModer | IsOwner).

            Returns:
                list: Список классов разрешений для текущего действия.
        """

        if self.action == "create":
            self.permission_classes = (~IsModer,)
        elif self.action in ["update", "retrieve"]:
            self.permission_classes = (IsModer | IsOwner,)
        elif self.action == "destroy":
            self.permission_classes = (~IsModer | IsOwner,)
        return super().get_permissions()


class CourseSubscriptionView(APIView):
    """
    API представление для управления подписками пользователя на курсы.

    Позволяет подписаться на курс или отписаться от него одним POST-запросом.
    Требует аутентификации пользователя.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает запрос на подписку или отписку от курса.

            Если пользователь уже подписан на курс, подписка удаляется.
            Если пользователь не подписан, создается новая подписка.

            Ожидает в теле запроса JSON-объект с ключом 'course_id'.

            Возвращает:
                Response: JSON-объект с ключом 'message',
                          содержащим статус выполненного действия.
        """

        user = request.user
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, id=course_id)

        subscription, created = CourseSubscription.objects.get_or_create(user=user, course=course)
        if not created:
            subscription.delete()
            message = "Подписка удалена"
        else:
            message = "Подписка добавлена"

        return Response({"message": message})


class LessonCreateApiView(generics.CreateAPIView):
    """
    API‑представление для создания уроков.

    Позволяет аутентифицированным пользователям создавать новые уроки
    с автоматической установкой владельца.
    """

    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModer]

    def perform_create(self, serializer):
        """
        Выполняет дополнительные действия при создании урока.

            Устанавливает текущего пользователя в качестве владельца урока
            перед сохранением в базу данных.

            Args:
                serializer (LessonSerializer): Сериализатор с валидированными данными.
        """

        lessons = serializer.save()
        lessons.owner = self.request.user
        lessons.save()


class LessonListApiView(generics.ListAPIView):
    """
    API‑представление для получения списка уроков.

    Возвращает все доступные уроки в системе.
    Используется для отображения списка уроков.
    """

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class LessonRetrieveApiView(generics.RetrieveAPIView):
    """
    API‑представление для детального просмотра урока.

    Возвращает подробную информацию об отдельном уроке.
    Доступ ограничен аутентифицированными пользователями,
    модераторами или владельцами урока.
    """

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonUpdateApiView(generics.UpdateAPIView):
    """
    API‑представление для обновления уроков.

    Позволяет изменять существующие уроки.
    Доступ ограничен аутентифицированными пользователями,
    модераторами или владельцами урока.
    """

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonDestroyApiView(generics.DestroyAPIView):
    """
    API‑представление для удаления уроков.

    Позволяет удалять уроки из системы.
    Доступ ограничен аутентифицированными пользователями:
    разрешено не‑модераторам или владельцам урока.
    """

    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, ~IsModer | IsOwner]
