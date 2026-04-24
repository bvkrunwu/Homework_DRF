from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

from lms.models import Course, CourseSubscription, Lesson
from lms.validators import validate_youtube_url


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Course.

    Преобразует экземпляры модели Course в JSON‑формат и обратно.
    Используется для операций со списком курсов и базовыми данными курса.
    """

    class Meta:
        """
        Мета‑опции для CourseSerializer.

        Определяет модель, с которой работает сериализатор,
            и поля для сериализации (все поля модели).
        """

        model = Course
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Lesson.

    Преобразует экземпляры модели Lesson в JSON-формат и обратно.
    Используется для операций с отдельными уроками и списками уроков.
    """

    class Meta:
        """
        Мета-опции для LessonSerializer.

        Определяет модель, с которой работает сериализатор,
        и поля для сериализации. В данном случае сериализуются все поля модели.
        """

        model = Lesson
        fields = "__all__"
        extra_kwargs = {
            "video_url": {
                "validators": [validate_youtube_url],
                "help_text": "Укажите ссылку на видео с YouTube. Ссылки на другие ресурсы запрещены.",
            }
        }


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Детальный сериализатор для модели Course с дополнительной информацией.

    Включает количество уроков и вложенные данные об уроках и признак подписки текущего пользователя на данный курс.
    Используется для представления подробной информации о курсе.
    """

    lesson_count = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = SerializerMethodField()

    class Meta:
        """
        Мета-опции для CourseDetailSerializer.

           Указывает, что данный сериализатор работает с моделью Course и определяет
           набор полей, которые будут включены в сериализованное представление.
           В отличие от базового сериализатора, здесь выводится расширенный набор данных.
        """

        model = Course
        fields = ("id", "title", "description", "lesson_count", "lessons", "is_subscribed")

    def get_lesson_count(self, course):
        """
        Вычисляет количество уроков в курсе.

        Используется как метод для SerializerMethodField для получения
        количества связанных уроков через отношение lessons.

            Args:
                course (Course): Экземпляр модели Course.

            Returns:
                int: Количество уроков в курсе (целое число).
        """

        return course.lessons.count()

    def get_is_subscribed(self, course):
        """
        Проверяет, подписан ли текущий пользователь на данный курс.

            Args:
                course (Course): Экземпляр курса, для которого проверяется подписка.

            Returns:
                bool: True, если пользователь подписан, иначе False.
        """

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return course.course_subscriptions.filter(user=request.user).exists()
        return False


class CourseSubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели CourseSubscription.

    Преобразует экземпляры модели подписки в JSON-формат и обратно.
    Используется для управления данными о подписках через API.
    """

    class Meta:
        """
        Мета-опции для CourseSubscriptionSerializer.

             Связывает сериализатор с моделью CourseSubscription и определяет
             набор полей, включаемых в сериализованное представление.
        """

        model = CourseSubscription
        fields = ("id", "user", "course", "created_at")
