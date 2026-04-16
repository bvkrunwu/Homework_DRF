from django.urls import path
from rest_framework.routers import DefaultRouter

from users.apps import UsersConfig
from users.views import PaymentViewSet, UserProfileView

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("profile/<str:email>/", UserProfileView.as_view(), name="user-profile"),
] + router.urls
