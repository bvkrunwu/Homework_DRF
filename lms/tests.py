from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, CourseSubscription, Lesson
from users.models import User


class LessonTestCase(APITestCase):
    """
    Набор тестов для проверки функциональности уроков (Lesson).
    """

    def setUp(self):
        """
        Настройка тестовой среды перед каждым тестом.
        Создает пользователя, курс и урок, а также выполняет аутентификацию.
        """

        # 1. Создаем пользователя для аутентификации
        self.user = User.objects.create(email="test_user@mail.ru")

        # 2. Создаем курс
        self.course = Course.objects.create(
            title="Test Course for Lesson", description="Course for testing lesson creation"
        )

        # 3. Создаем урок, привязывая его к созданному курсу
        self.lesson = Lesson.objects.create(
            title="Test Lesson", description="Test Lesson description", course=self.course
        )

        # Устанавливаем владельца урока на текущего пользователя
        self.lesson.owner = self.user
        self.lesson.save()

        # Аутентифицируем клиента для тестов, требующих авторизации
        self.client.force_authenticate(user=self.user)

    def test_lesson_creation(self):
        """
        Тестирует создание нового урока через API.
        Проверяет, что урок создается с корректными данными.
        """

        url = reverse("lms:lesson-create")
        data = {
            "title": "New Lesson via API",
            "description": "Created through POST request",
            "course": self.course.id,
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_list(self):
        """
        Тестирует получение списка всех уроков.
        Проверяет, что ответ имеет статус 200 OK и содержит корректные данные.
        """

        url = reverse("lms:lesson-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertGreater(len(data), 0)
        self.assertIn("results", data)

    def test_lesson_retrieval(self):
        """
        Тестирует получение детальной информации об уроке по его ID.
        Проверяет, что ответ имеет статус 200 OK.
        """

        self.lesson.owner = self.user
        self.lesson.save()

        url = reverse("lms:lesson-detail", args=[self.lesson.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["title"], "Test Lesson")

    def test_lesson_update(self):
        """
        Тестирует обновление урока через API.
        Проверяет, что урок обновляется с новыми данными.
        """

        url = reverse("lms:lesson-update", args=[self.lesson.pk])
        new_data = {
            "title": "Updated Lesson Title",
            "description": "Updated Lesson Description",
            "course": self.course.id,
            "video_url": "https://www.youtube.com/watch?v=new_video_id",
        }

        response = self.client.put(url, new_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_lesson = Lesson.objects.get(pk=self.lesson.pk)
        self.assertEqual(updated_lesson.title, new_data["title"])
        self.assertEqual(updated_lesson.description, new_data["description"])

    def test_lesson_delete(self):
        """
        Тестирует удаление урока через API.
        Проверяет, что урок удаляется успешно.
        """

        url = reverse("lms:lesson-delete", args=[self.lesson.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertRaises(Lesson.DoesNotExist, Lesson.objects.get, pk=self.lesson.pk)


class CourseSubscriptionTestCase(APITestCase):
    """
    Набор тестов для проверки функциональности подписки на обновления курса.
    """

    def setUp(self):
        """
        Настройка тестовой среды перед каждым тестом.
        Создает пользователя, курс и подписку, а также выполняет аутентификацию.
        """
        # 1. Создаем пользователя для аутентификации
        self.user = User.objects.create(email="test_user@mail.ru")

        # 2. Создаем курс
        self.course = Course.objects.create(
            title="Test Course for Subscription", description="Course for testing subscriptions"
        )

        # 3. Создаем подписку на курс
        self.subscription = CourseSubscription.objects.create(user=self.user, course=self.course)

        # Аутентифицируем клиента для тестов, требующих авторизации
        self.client.force_authenticate(user=self.user)

    def test_subscription_creation(self):
        """
        Тестирует создание новой подписки на курс через API.
        Проверяет, что подписка добавляется корректно.
        """
        # Создаем новый курс для подписки
        new_course = Course.objects.create(
            title="Another Test Course", description="Course for testing another subscription"
        )

        url = reverse("lms:course-subscription")
        data = {"course_id": new_course.id}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "Подписка добавлена")

        # Проверяем, что подписка создана
        self.assertTrue(CourseSubscription.objects.filter(user=self.user, course=new_course).exists())

    def test_subscription_deletion(self):
        """
        Тестирует отмену подписки на курс через API.
        Проверяет, что подписка удаляется корректно.
        """
        url = reverse("lms:course-subscription")
        data = {"course_id": self.course.id}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "Подписка удалена")

        # Проверяем, что подписка удалена
        self.assertFalse(CourseSubscription.objects.filter(user=self.user, course=self.course).exists())
