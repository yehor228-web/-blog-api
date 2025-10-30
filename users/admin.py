from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile


class ProfileInline(admin.StackedInline):
    """
    Defines an inline admin descriptor for Profile model,
    which acts a bit like a singleton.
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

   
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "get_newsletter")
    list_select_related = ("profile",)

    def get_newsletter(self, instance):
        return instance.profile.newsletter_subscription
    get_newsletter.short_description = "Підписка"
    get_newsletter.boolean = True  

from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "newsletter_subscription"]
    readonly_fields = []
    search_fields = ["user__username", "user__email", "bio"]
    list_filter = [
        "newsletter_subscription",
    ]
    empty_value_display = "null"



admin.site.unregister(User)

admin.site.register(User, UserAdmin)
