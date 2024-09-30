from django.urls import path
from .views import register, login_view, logout_view, vote, success, home

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('vote/', vote, name='vote'),
    path('success/', success, name='success'),
]
