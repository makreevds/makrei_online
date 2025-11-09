from django.db import models

class Post(models.Model):
    """Пост в блоге."""
    title = models.CharField("Заголовок", max_length=200)
    content = models.TextField("Текст поста")
    created_at = models.DateTimeField("Дата и время создания", auto_now_add=True)

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
