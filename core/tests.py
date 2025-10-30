from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Category, BlogEntry

class BlogEntryModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.user = User.objects.create_user(username='testuser', password='testpassword')
        cls.category = Category.objects.create(title='Test Category')
        cls.blog_entry = BlogEntry.objects.create(
            title='Test Blog Post',
            category=cls.category,
            user=cls.user,
            content='<p>This is test content.</p>'
        )

    def test_get_absolute_url(self):
        # This will also fail if the urlconf is not defined.
        self.assertEqual(self.blog_entry.get_absolute_url(), f'/entries/{self.blog_entry.id}')
