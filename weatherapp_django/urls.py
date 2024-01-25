from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('users', views.view_users, name='users'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('register', views.register, name='register'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('mpesa', views.mpesa_payment, name='mpesa_payment'),
]