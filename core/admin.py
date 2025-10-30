from django.contrib import admin
from .models import BlogEntry, Category, NewsletterSubscriber

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=["title", "created_at"]
    readonly_fields = ["created_at",]
    search_fields = ["title",]
    list_filter = ["created_at",]
    

@admin.register(BlogEntry)
class BlogEntryAdmin(admin.ModelAdmin):
    list_display = ["view_id", "title", "created_at", "updated_at"]  
    readonly_fields = ["created_at", "updated_at"]                    
    search_fields = ["title", "id"]
    list_filter = ["created_at", "updated_at"]                      
    empty_value_display = "null"

    @admin.display(description="Entry id")
    def view_id(self, obj):
        return f"Entry obj {obj.id}"
    

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    readonly_fields = ('subscribed_at',)
    search_fields = ('email',)
    list_filter = ('subscribed_at',)
