from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

from lms.models import Course, Lesson
from users.models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseDetailSerializer(serializers.ModelSerializer):
    lesson_count = SerializerMethodField()
    lessons = LessonSerializer(many=True)

    class Meta:
        model = Course
        fields = ("id", "title", "description", "lesson_count", "lessons")

    def get_lesson_count(self, course):
        return course.lessons.count()
