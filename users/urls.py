from django.urls import path
from .views import registration
from .views import login_view  
from . views import activate
from . views import logout_view



urlpatterns = [
    path("registration/", registration, name='registration'),
    path('login/', login_view, name='login'), 
    path("activate/<uid>/<token>/", activate, name="activate"),
    path("logout/", logout_view, name="logout")

]