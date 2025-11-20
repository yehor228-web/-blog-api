from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email:")
    first_name = forms.CharField(required=True, max_length=50, label="First name:")
    last_name = forms.CharField(required=True, max_length=100, label="Last name:")

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()

        return user
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    # 📧 Перевірка унікальності email
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
class LoginForm(forms.Form):
    identifier = forms.CharField(label="Username or Email:", required=True)
    password = forms.CharField(
        label="Password:",
        widget=forms.PasswordInput(attrs={"placeholder": "Password"}),
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get("identifier")
        password = cleaned_data.get("password")

        if identifier and password:
            user = User.objects.filter(username=identifier).first()
            if not user:
                user = User.objects.filter(email=identifier).first()

            if not user:
                raise forms.ValidationError("Invalid username/email or password.")

            if not user.check_password(password):
                raise forms.ValidationError("Invalid username/email or password.")

            if not user.is_active:
                raise forms.ValidationError("Email not confirmed. Check your inbox.")

            cleaned_data["user"] = user
        return cleaned_data

        


       