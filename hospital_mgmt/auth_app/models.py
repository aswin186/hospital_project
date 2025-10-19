from django.db import models

# ------------------------
# Role Table
# ------------------------
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'role'
        managed = False  # Do not let Django manage the table

    def __str__(self):
        return self.name


# ------------------------
# User Table
# ------------------------
class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    email_id = models.CharField(max_length=150, unique=True)
    role = models.ForeignKey(Role, on_delete=models.RESTRICT, db_column='role_id')

    class Meta:
        db_table = 'users'
        managed = False

    def __str__(self):
        return f"{self.username} ({self.role.name})"


# ------------------------
# Specialization Table
# ------------------------
class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'specialization'
        managed = False

    def __str__(self):
        return self.name


# ------------------------
# Doctor Table
# ------------------------
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user_id')
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True, db_column='specialization_id')
    mobile_number = models.CharField(max_length=20)

    class Meta:
        db_table = 'doctor'
        managed = False

    def __str__(self):
        return f"{self.user.name} - {self.specialization.name if self.specialization else 'No Spec'}"


# ------------------------
# Patient Table
# ------------------------
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user_id')
    mobile_number = models.CharField(max_length=20)
    age = models.IntegerField()
    gender_choices = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = models.CharField(max_length=6, choices=gender_choices)
    address = models.CharField(max_length=255)

    class Meta:
        db_table = 'patient'
        managed = False

    def __str__(self):
        return f"{self.user.name} - {self.gender}"


class PatientDetails(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='details')

    address = models.CharField(max_length=255)
    blood_group = models.CharField(max_length=5, null=True, blank=True)
    allergies = models.TextField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)

    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_relation = models.CharField(max_length=50)
    emergency_contact_number = models.CharField(max_length=15)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patient_details'
        managed = False

    def __str__(self):
        return f"Details for {self.patient.user.name}"
    


class AppointmentStatus(models.Model):
    id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=50, unique=True)

    class Meta:
        managed = False  # Django won't try to create or modify this table
        db_table = "appointment_status"

    def __str__(self):
        return self.status_name


class Appointment(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, db_column="patient_id"
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, db_column="doctor_id"
    )
    appointment_date = models.DateField()
    appointment_time = models.CharField(max_length=50)
    status = models.ForeignKey(
        AppointmentStatus,
        on_delete=models.SET_NULL,
        null=True,
        default=1,
        db_column="status_id",
    )
    notes = models.TextField(blank=True, null=True)
    report = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False  # prevents Django from creating the table
        db_table = "appointment"

    def __str__(self):
        return f"Appointment #{self.id} ({self.appointment_date} - {self.appointment_time})"
