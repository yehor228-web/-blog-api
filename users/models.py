from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to="avatars",
        default="avatars/defult_avatar.jpg",
        blank=True,
        null=True
    )
    newsletter_subscription = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Профіль {self.user.username}"