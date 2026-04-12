from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

from lms.models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = "__all__"


class CourseDetailSerializer(serializers.ModelSerializer):
    lesson_count = SerializerMethodField()

    class Meta:
        model = Course
        fields = ("id", "title", "description", "lesson_count")

    def get_lesson_count(self, course):
        return course.lessons.count()


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = "__all__"
