from django import forms
from .models import BlogEntry, NewsletterSubscriber, Comment


class BlogEntryForm(forms.ModelForm):
    class Meta:
        model = BlogEntry
        fields = ["title", "category", "content", "image", "video", "color"]
        widgets = {
            "color": forms.TextInput(attrs={"type": "color"}),
        }


class NewsletterSubscriptionForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email Address',
                'aria-label': 'Email Address for newsletter'
            })
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'stars']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
            'stars': forms.HiddenInput(),
        }

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100, label="Тема")
    message = forms.CharField(widget=forms.Textarea, label="Повідомлення")
    recipient = forms.EmailField(label="Кому")


