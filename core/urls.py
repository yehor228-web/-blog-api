from django.urls import path
from .views import *


urlpatterns = [ 
    path("", index,name='home'), 
    path("entries/create", create_blog_entry, name='create_blog_entry'),
    path("entries",all_blog_entries,name="all_blog_entries"),
    path('about/', about_view, name='about'),
    path("entries/<int:blog_id>", blog_entry_details, name="blog_entry_details"),
    path("comment/delete/<int:comment_id>/",delete_comment, name="delete_comment"),
    path('send-email/', send_email_view, name='send_email'),
    path('popular/',popular, name='popular'),
    path("post/<int:blog_id>/delete/",delete_post, name="delete_post"),
    path('blog/<int:blog_id>/edit/',edit_blog_entry, name='edit_blog_entry'),
    path("post/<int:blog_id>/save/",toggle_save_post, name="save_post"),  
    path("saved/delete/<int:saved_id>/", delete_saved_post, name="delete_saved_post"),
    path("u/<str:username>/", profile_detail, name="profile_detail"),
    path('search_user/', search_user, name='search_user'),
    path("profile/user/update/", update_profile, name="update_profile"),

]

    