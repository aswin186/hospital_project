from django.contrib import admin
from .models import Role, User, Specialization, Doctor, Patient, PatientDetails, Appointment, AppointmentStatus

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'name', 'email_id', 'role']
    list_filter = ['role']
    search_fields = ['username', 'name', 'email_id']


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    search_fields = ['name']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'specialization', 'mobile_number']
    search_fields = ['user__username', 'user__name', 'mobile_number']
    list_filter = ['specialization']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'mobile_number', 'age', 'gender', 'address']
    search_fields = ['user__username', 'user__name', 'mobile_number', 'address']
    list_filter = ['gender']


@admin.register(PatientDetails)
class PatientDetailsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'patient',
        'address',
        'allergies',
        'medical_history',
        'blood_group',  # New field added
        'emergency_contact_name',
        'emergency_contact_relation',
        'emergency_contact_number',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'patient__user__name',
        'emergency_contact_name',
        'emergency_contact_number',
        'address',
        'allergies',
        'medical_history',
        'blood_group',  # Search by blood group
    )
    list_filter = ('blood_group', 'emergency_contact_relation')
    ordering = ('-created_at',)


@admin.register(AppointmentStatus)
class AppointmentStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "status_name")
    search_fields = ("status_name",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "doctor",
        "appointment_date",
        "appointment_time",
        "status",
        "created_at",
    )
    list_filter = ("status", "appointment_date")
    search_fields = ("patient__name", "doctor__user__name", "notes")
    ordering = ("-appointment_date", "-appointment_time")