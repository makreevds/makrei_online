from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    """Пост в блоге."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор",
        null=True,
        blank=True
    )
    title = models.CharField("Заголовок", max_length=200)
    content = models.TextField("Текст поста")
    created_at = models.DateTimeField("Дата и время создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата и время обновления", auto_now=True)

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self) -> str:
        return self.title
