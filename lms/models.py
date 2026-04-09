from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название курса", help_text="Укажите название курса")
    preview = models.ImageField(
        upload_to="courses/previews/",
        blank=True,
        null=True,
        verbose_name="Превью курса",
        help_text="загрузите превью курса",
    )
    description = models.TextField(verbose_name="Описание курса", help_text="Заполните описание курса")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200, verbose_name="Название урока", help_text="Укажите название урока")
    description = models.TextField(verbose_name="Описание урока", help_text="Заполните описание урока")
    preview = models.ImageField(
        upload_to="lessons/previews/",
        blank=True,
        null=True,
        verbose_name="Превью урока",
        help_text="загрузите превью урока",
    )
    video_url = models.URLField(
        blank=True, null=True, verbose_name="Ссылка на видео", help_text="Укажите ссылку на видео"
    )

    def __str__(self):
        return f"{self.title} | Курс: {self.course.title}"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
