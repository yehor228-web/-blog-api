from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import Profile
from .models import BlogEntry, Category, NewsletterSubscriber, Comment
from .forms import BlogEntryForm, NewsletterSubscriptionForm, CommentForm
from django import forms
from .models import Comment
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render
from django.core.mail import send_mail
from .forms import ContactForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from .models import BlogEntry, SavedPost

@login_required
def toggle_save_post(request, blog_id):
    from django.http import JsonResponse
    from core.models import BlogEntry
    from .models import SavedPost
    from django.shortcuts import get_object_or_404

    if request.method == "POST":
        post = get_object_or_404(BlogEntry, id=blog_id)
        saved_post, created = SavedPost.objects.get_or_create(
            user=request.user, post=post
        )

        if not created:
            saved_post.delete()
            is_saved = False
            message = "Post removed from saved!"

        else:
            is_saved = True
            message = "Post saved successfully!"

        return JsonResponse(
            {"isSaved": is_saved, "message": message}
        )

    return JsonResponse({"error": "Invalid method!"}, status=405)



from .models import SavedPost 
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


def delete_saved_post(request, saved_id):
    if request.method == "POST" and request.user.is_authenticated:
        saved = get_object_or_404(SavedPost, id=saved_id, user=request.user)
        saved.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)




def index(request):
    newsletter_form = NewsletterSubscriptionForm()

    if request.method == "POST":
        email = request.POST.get("email")
        print(email)  # для дебага у консолі

        if email:
            user = User.objects.filter(email=email).first()
            if user:
                try:
                    profile = user.profile
                    profile.newsletter_subscription = not profile.newsletter_subscription
                    profile.save()
                    messages.success(request, "Підписка оновлена!")
                    return redirect("home")
                except Exception as e:
                    messages.error(request, f"Помилка: {e}")
                    return redirect("home")
            else:
                messages.warning(request, "Такого користувача нема. Зареєструйтесь!")
                return redirect("register")
        else:
            messages.error(request, "Ви не ввели email!")
            return redirect("home")

    # останні 4 пости
    posts = (
        BlogEntry.objects.select_related("category", "user")
        .order_by("-created_at")[:4]
    )

    # топ 4 пости за рейтингом
    top_rated_posts = (
        BlogEntry.objects.select_related("category", "user")
        .order_by("-rating")[:4]
    )

    return render(
    request,
    "index.html",
    {
        "posts": posts,
        "newsletter_form": newsletter_form,
        "top_rated_posts": top_rated_posts,
    },
)


def all_blog_entries(request):
    category_name = request.GET.get('category')
    posts_query = BlogEntry.objects.select_related("category", "user").order_by("-created_at")

    if category_name:
        posts = posts_query.filter(category__title=category_name)
    else:
        posts = posts_query

    categories = Category.objects.all()

    return render(request, 'blog_entries_list.html', context={"posts": posts, "categories": categories})

@login_required
def blog_entry_details(request, blog_id):
    post = get_object_or_404(BlogEntry.objects.select_related("category", "user"), id=blog_id)
    categories = Category.objects.all()
    from django.db.models import Avg

    comments = Comment.objects.filter(blog_entry=post).select_related("user")
    
    recommended_posts = (
        BlogEntry.objects.select_related("category")
        .filter(category=post.category)
        .exclude(id=post.id)
        .order_by("-created_at")[:4]
    )
    
    if request.method == "POST":
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.blog_entry = post
                comment.save()

                post.raiting =post.comments.aggregate(Avg('stars'))['stars__avg'] 
                post.save()

                return redirect("blog_entry_details", blog_id=post.id)
        else:
            return redirect("login")
    else:
        form = CommentForm()
    is_post_saved = SavedPost.objects.filter(user=request.user, post=post).exists()
    return render(
        request,
        "blog_entry_details.html",
        {
            "post": post,
            "categories": categories,
            "recommended_posts": recommended_posts,
            "form": form,
            "comments": comments,
            "is_post_saved": is_post_saved,
        },
    )

@login_required
def create_blog_entry(request):
    if request.method == "POST":
        form = BlogEntryForm(request.POST, request.FILES)  
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()

            # Розсилка
            subscribers = Profile.objects.filter(newsletter_subscription=True)
            recipient_list = [s.user.email for s in subscribers if s.user.email]

            if recipient_list:
                html_content = render_to_string("emails/new_blog_entry.html", {
                    "entry": entry,
                    "absolute_url": request.build_absolute_uri(entry.get_absolute_url())
                })

                subject = f"📰 Нова стаття: {entry.title}"
                from_email = "yehor.maksymenko@gmail.com"  

                msg = EmailMultiAlternatives(subject, "", from_email, recipient_list)
                msg.attach_alternative(html_content, "text/html")
                msg.send()

            messages.success(request, "Стаття створена і емейл-розсилка відправлена ✅")
            return redirect(entry.get_absolute_url())
        else:
            print('error')
    else:
        form = BlogEntryForm()

    return render(request, "create_blog_entry.html", {"form": form})


@login_required
def about_view(request):
    return render(request, 'about.html')



@login_required
def delete_comment(request, comment_id):
    if request.method == "POST":
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.user == request.user or request.user.is_staff:
            comment.delete()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "No permission"})
    return JsonResponse({"success": False, "error": "Invalid request"})

from django.conf import settings
from django.contrib.auth.decorators import login_required

@login_required
def send_email_view(request):
    user = request.user  # беремо поточного юзера

    # Генеруємо активаційне посилання
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = request.build_absolute_uri(
        reverse("activate", kwargs={"uidb64": uid, "token": token})
    )

    subject = "Підтвердження акаунту"
    message = f"Привіт, {user.username}!\nНатисни на посилання для активації:\n{activation_link}"

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        messages.success(request, "Лист із підтвердженням відправлено на вашу пошту.")
    except Exception as e:
        messages.error(request, f"Помилка при відправці листа: {e}")

    return render(request,)

from django.shortcuts import render
from .models import BlogEntry  

@login_required
def popular(request):
    # сортуємо за кількістю зірочок (raiting)
    popular_posts = BlogEntry.objects.order_by('-raiting')[0:10]

    return render(request, 'blog_entry_details.html', {
        'popular_posts': popular_posts
    })


from django.contrib.auth import get_user_model
from django.db.models import Count, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required



User = get_user_model()

def search_user(request):
    """Пошук користувача за username"""
    query = request.GET.get("q")
    if query:
        user = User.objects.filter(username__iexact=query).first()
        if user:
            return redirect("profile_detail", username=user.username)
        else:
            messages.error(request, f'Користувача "{query}" не знайдено.')
    return redirect("home")

@login_required
def update_profile(request):
    import json
    from django.http import JsonResponse
    from django.core.validators import validate_email
    user = request.user
   


    if request.method == "POST":
        try:
            user = request.user
            data =json.loads(request.body)
            print("Update profile data:", data)
            new_username=data.get("username","").strip()

            if len(new_username) < 3:
                return JsonResponse(
                    {
                    "sucess":False,
                    "eror":"Invalid username.Username must be bigger than 3 characters!",
                    },
                    status=400
                )
            if User.objects.filter(username=new_username).exclude(id=user.id).exists():
                return JsonResponse(
                    {
                        "success": False,
                        "error": "This username is already taken!",
                    },
                    status=400,
                )
        # Validate_email
            new_email = data.get("email", "").strip()
            if not new_email:
                return JsonResponse(
                    {"success": False, "error": "Email не може бути порожнім."},
                    status=400,
                )
            try:
                validate_email(new_email)
            except ValueError:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Invalid email adress format!",
                    },
                    status=400,
                )
          
            
            first_name = data.get("firstName", "").strip()
            last_name = data.get("lastName", "").strip()


            if len(first_name) < 2:
                return JsonResponse(
                    {"success": False, "error": "First name must be at least 2 characters."},
                    status=400,
            )
            if len(last_name) < 2:
                return JsonResponse(
                    {"success": False, "error": "Last name must be at least 2 characters."},
                    status=400,
                )
            bio = data.get("bioField", "").strip()
            if len(bio) > 500:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Bio cannot exceed 500 characters.",
                    },
                    status=400,
                )
           
            user.username = new_username
            user.email = new_email
            user.first_name = first_name
            user.last_name = last_name

            profile = user.profile
            profile.bio = bio

            user.save()
            profile.save()
           

            return JsonResponse(
                {
                    "success": True,
                    "message": "Profile updated successfully!",
                    "user": {
                        "username": user.username,
                        "email": user.email,
                        "firstName": user.first_name,
                        "lastName": user.last_name,
                        "bio": profile.bio,
                    },
                }
            )
        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Invalid JSON data!",
                },
                status=400,
            )
        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "error": f"An error: {str(e)}",
                },
                status=500,
            )



@login_required
def profile_detail(request, username):
    """Відображення профілю користувача"""
    profile_user = get_object_or_404(User, username=username)

    
    is_own_profile = request.user == profile_user

  
    blogs = (
        profile_user.blog_entries.all()
        .annotate(comments_count=Count("comments"))
        .select_related("user", "category")  
    )

    
    blog_forms = {blog.id: BlogEntryForm(instance=blog) for blog in blogs} if is_own_profile else {}


    saved_posts = request.user.saved_posts.all() if is_own_profile else []

  
    stats = {
        "total_posts": blogs.count(),
        "avg_post_rating": blogs.aggregate(avg=Avg("rating"))["avg"] or 0,
        "total_comments": profile_user.comments.count(),
        "avg_comment_stars": profile_user.comments.aggregate(avg=Avg("stars"))["avg"] or 0,
        "total_saved_posts": SavedPost.objects.filter(user=profile_user).count(),
    }

    return render(request, "blog/profile_detail.html", {
        "profile_user": profile_user,
        "blogs": blogs,
        "blog_forms": blog_forms,
        "stats": stats,
        "saved_posts": saved_posts,
        "is_own_profile": is_own_profile,
})

@login_required
def delete_post(request, blog_id):
    blog_entry = get_object_or_404(BlogEntry, id=blog_id)

    if request.user == blog_entry.user:
        blog_entry.delete()
        messages.success(request, "Пост успішно видалено!")
    else:
        messages.error(request, "У вас немає прав для видалення цього поста.")

    return redirect("profile_detail", username=request.user.username)


@login_required
def edit_blog_entry(request, blog_id):
   
    blog = get_object_or_404(BlogEntry, id=blog_id)
    
    
    if request.user != blog.user:
        messages.error(request, "Ви не можете редагувати цей пост.")
        return redirect('all_blog_entries')

    if request.method == 'POST':
        form = BlogEntryForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, "Пост успішно відредаговано!")
            return redirect(blog.get_absolute_url())
        else:
            messages.error(request, "Помилка! Перевірте правильність заповнення форми.")
    else:
        form = BlogEntryForm(instance=blog)

    return render(request, 'blog/edit_blog_entry.html', {'form': form, 'blog': blog})

