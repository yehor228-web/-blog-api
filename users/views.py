
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login,get_user_model
from .forms import RegistrationForm, LoginForm
from django.core.mail import send_mail
from django.conf import settings




def send_email(request, subject, message, html_content, recipient_list):
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings

    msg = EmailMultiAlternatives(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipient_list,
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()


def logout_view(request):
    from django.contrib.auth import logout

    
    logout(request)


    return redirect("home")

def registration(request):

    from django.template.loader import render_to_string
    from .token import account_activation_token
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    from .models import Profile

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()

            profile = Profile.objects.create(user=user)
            profile.save()

            user_token = account_activation_token.make_token(user)
            print("user_token:",user_token) 
            uid=urlsafe_base64_encode(force_bytes(user.pk))
            print("uid:",uid)
            

            # html_message = render_to_string(
            #     "emails/registration_confirm.html",
            #     context={"user": user,"uid":uid,"token":user_token},
            # )

            # send_email(
            #     request,
            #     "BlogApp: Registration Confirm",
            #     "Confirm your registration",
            #     html_message,
            #     [user.email],
            # )
            
            messages.success(request, f"Welcome, {user.username}!")
            return redirect("login")
    else:
        form = RegistrationForm()

    return render(request, "registration.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            login(request, user)

            messages.success(request, f"Welcome, {user.username}!")

            return redirect("home")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})

User = get_user_model()


def activate(request, uid, token):
    from django.utils.http import urlsafe_base64_decode
    from .token import account_activation_token
    from django.utils.encoding import force_str
    from django.shortcuts import get_object_or_404
    from django.contrib.auth.models import User
    from django.contrib import messages

    user_id = force_str(urlsafe_base64_decode(uid))
    user = get_object_or_404(User, pk=user_id)

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Your account successfully activated!")
        return redirect("login")
    else:
        messages.error(request, "Activation link is invalid")
        return redirect("registration")
    

from django.contrib.auth import get_user_model
from django.db.models import Count, Avg

User = get_user_model()


