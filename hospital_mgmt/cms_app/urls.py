from django.urls import path
from . import views

urlpatterns = [
    path('patients/', views.list_patients, name='patients_list'),
    path('patients/create/', views.patient_create_edit, name='patient_create'),
    path('patients/edit/<int:user_id>/', views.patient_create_edit, name='patient_edit'),
    path('patients/save/', views.save_patient, name='save_patient'),
    path('patient/detail/<int:user_id>/', views.patient_profile, name='patient_detail'),
    # path('patients/delete/<int:patient_id>/', views.patient_delete, name='patient_delete'),

    path('doctors/', views.list_doctors, name='doctors_list'),
    path('doctor/detail/<int:user_id>/', views.doctor_profile, name='doctors_detail'),
]