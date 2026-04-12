from django.urls import path
from rest_framework.routers import DefaultRouter

from lms.apps import LmsConfig
from lms.views import (
    CourseViewSet,
    LessonCreateApiView,
    LessonDestroyApiView,
    LessonListApiView,
    LessonRetrieveApiView,
    LessonUpdateApiView,
    PaymentViewSet,
)

app_name = LmsConfig.name


router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("lessons/create/", LessonCreateApiView.as_view(), name="lesson-create"),
    path("lessons/", LessonListApiView.as_view(), name="lesson-list"),
    path("lessons/<int:pk>/", LessonRetrieveApiView.as_view(), name="lesson-detail"),
    path("lessons/update/<int:pk>/", LessonUpdateApiView.as_view(), name="lesson-update"),
    path("lessons/delete/<int:pk>/", LessonDestroyApiView.as_view(), name="lesson-delete"),
] + router.urls
