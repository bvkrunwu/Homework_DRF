from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

from lms.models import Course, Lesson


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

    Преобразует экземпляры модели Lesson в JSON‑формат и обратно.
    Используется для операций с отдельными уроками и списками уроков.
    """

    class Meta:
        """
        Мета‑опции для LessonSerializer.

        Определяет модель, с которой работает сериализатор,
            и поля для сериализации (все поля модели).
        """

        model = Lesson
        fields = "__all__"


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Детальный сериализатор для модели Course с дополнительной информацией.

    Включает количество уроков и вложенные данные об уроках.
    Используется для представления подробной информации о курсе.
    """

    lesson_count = SerializerMethodField()
    lessons = LessonSerializer(many=True)

    class Meta:
        """
        Детальный сериализатор для модели Course с дополнительной информацией.

        Включает количество уроков и вложенные данные об уроках.
        Используется для представления подробной информации о курсе.
        """

        model = Course
        fields = ("id", "title", "description", "lesson_count", "lessons")

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
