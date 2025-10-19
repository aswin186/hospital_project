from django.urls import path
from . import views

urlpatterns = [
    path('appointments/', views.list_appointments, name='appointments_list'),
    path('appointment/create/', views.appointment_create, name='appointment_create'),
    path('appointment/detail/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointment/<int:appointment_id>/update/<str:action>/', views.update_appointment_status, name='update_appointment_status'),
]