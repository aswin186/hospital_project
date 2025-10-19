from django.urls import path
from . import views

urlpatterns = [
    path('auth-login/', views.login_user, name='auth_login'),
    path('auth-register/', views.register_user, name='auth_register'),
    path('auth-logout/', views.logout_user, name='auth_logout'),
]