from django.db import models
from tinymce.models import HTMLField
from django.conf import settings
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Category(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class BlogEntry(models.Model):
    title = models.CharField(max_length=250)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='blog_entries')
    content = HTMLField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True, default=0.0)
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    video = models.FileField(upload_to='blog_videos/', null=True, blank=True)  # Додано відео
    color = models.CharField(max_length=7, default="#ffffff", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_absolute_url(self):
        return reverse("blog_entry_details", kwargs={"blog_id": self.id})

    def __str__(self):
        return self.title



class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Comment(models.Model):
    blog_entry = models.ForeignKey(
        BlogEntry, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # <-- CustomUser
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField(null=True, blank=True)
    stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog_entry.title}"
    

class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_posts")
    post = models.ForeignKey(BlogEntry, on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)
  
    def __str__(self):
        return f"{self.user.username} -> {self.post.title}"

