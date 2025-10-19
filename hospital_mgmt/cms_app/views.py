import math
import mysql.connector
from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from auth_app.decorators import session_login_required
import time

from .helper_fun import get_patient_data, get_patient_info_by_user, get_doctor_info_by_user


@session_login_required
def list_patients(request):
    page = int(request.GET.get("page", 1))  # current page
    per_page = 2
    offset = (page - 1) * per_page

    patients = []
    total_patients = 0

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="aswin",
            password="Hearzap@123",
            database="hospital_db"
        )
        cursor = conn.cursor(dictionary=True)

        # Count total patients
        cursor.execute("SELECT COUNT(*) AS total FROM patient")
        total_patients = cursor.fetchone()["total"]

        # Fetch paginated patient list with user info (newest first)
        cursor.execute("""
            SELECT 
                u.id AS patient_id,
                u.name AS patient_name,
                u.email_id,
                p.mobile_number,
                p.age,
                p.gender,
                p.address
            FROM patient p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.id DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        patients = cursor.fetchall()

    except mysql.connector.Error as err:
        messages.error(request, f"Database error: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    # Pagination logic
    total_pages = math.ceil(total_patients / per_page)
    start_item = offset + 1 if total_patients > 0 else 0
    end_item = min(offset + per_page, total_patients)

    context = {
        "patients": patients,
        "page": page,
        "total_pages": total_pages,
        "pages": range(1, total_pages + 1),
        "start_item": start_item,
        "end_item": end_item,
        "total_patients": total_patients
    }

    return render(request, "patients_l.html", context)


GENDER_CHOICES = ['Male', 'Female', 'Other']
BLOOD_GROUP_CHOICES = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']


@session_login_required
def patient_create_edit(request, user_id=None):
    """Render create/edit patient form with merged patient data"""
    patient = get_patient_data(user_id) if user_id else None

    print(patient, "#######data ########")

    context = {
        "patient": patient,
        "gender_choices": GENDER_CHOICES,
        "blood_group_choices": BLOOD_GROUP_CHOICES,
    }
    return render(request, "patients_cu.html", context)



@csrf_exempt
@session_login_required
def save_patient(request):
    """Handle create/update POST request including users table"""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"})

    data = request.POST
    patient_id = data.get("patient_id")  # hidden input for edit mode

    name = data.get("full_name")
    email = data.get("email")
    age = data.get("age")
    gender = data.get("gender")
    mobile = data.get("mobile_number")
    address = data.get("address")
    blood_group = data.get("blood_group")
    allergies = data.get("allergies")
    medical_history = data.get("medical_history")
    emergency_name = data.get("emergency_name")
    emergency_relation = data.get("emergency_relation")
    emergency_mobile = data.get("emergency_mobile")

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host="localhost", user="aswin", password="Hearzap@123", database="hospital_db"
        )
        cursor = conn.cursor()

        # 1️⃣ Get role_id for patient
        cursor.execute("SELECT id FROM role WHERE name=%s", ("patient",))
        role = cursor.fetchone()
        if not role:
            return JsonResponse({"success": False, "message": "Patient role not found"})
        role_id = role[0]

        if patient_id:  # here patient_id is actually user_id
            # Get patient.id for this user
            cursor.execute("SELECT id FROM patient WHERE user_id=%s", (patient_id,))
            row = cursor.fetchone()
            if row:
                actual_patient_id = row[0]
            else:
                return JsonResponse({"success": False, "message": "Patient not found"})

            # 1️⃣ Update users table
            cursor.execute("""
                UPDATE users
                SET name=%s, email_id=%s
                WHERE id=%s
            """, (name, email, patient_id))  # patient_id is user.id

            # 2️⃣ Update patient table
            cursor.execute("""
                UPDATE patient
                SET age=%s, gender=%s, mobile_number=%s, address=%s
                WHERE id=%s
            """, (age, gender, mobile, address, actual_patient_id))

            # 3️⃣ Update patient_details table
            cursor.execute("""
                UPDATE patient_details
                SET blood_group=%s, allergies=%s, medical_history=%s,
                    emergency_contact_name=%s, emergency_contact_relation=%s, emergency_contact_number=%s
                WHERE patient_id=%s
            """, (blood_group, allergies, medical_history, emergency_name, emergency_relation,
                emergency_mobile, actual_patient_id))

            message = "Patient updated successfully!"


        else:
            # ---------- CREATE MODE ----------
            # 1️⃣ Insert into users table
            username = name.replace(" ", "").lower() + str(int(time.time()))
            cursor.execute("""
                INSERT INTO users (username, name, password, email_id, role_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, name, "default_password", email, role_id))  # You can hash password
            new_user_id = cursor.lastrowid

            # 2️⃣ Insert into patient table
            cursor.execute("""
                INSERT INTO patient (user_id, age, gender, mobile_number, address)
                VALUES (%s, %s, %s, %s, %s)
            """, (new_user_id, age, gender, mobile, address))
            new_patient_id = cursor.lastrowid

            # 3️⃣ Insert into patient_details table
            cursor.execute("""
                INSERT INTO patient_details
                (patient_id, address, blood_group, allergies, medical_history,
                 emergency_contact_name, emergency_contact_relation, emergency_contact_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (new_patient_id, address, blood_group, allergies, medical_history,
                  emergency_name, emergency_relation, emergency_mobile))

            message = "Patient created successfully!"

        conn.commit()
        return JsonResponse({"success": True, "message": message})

    except mysql.connector.Error as err:
        print("Database error:", err)
        return JsonResponse({"success": False, "message": f"Database error: {err}"})
    except Exception as e:
        print("Unexpected error:", e)
        return JsonResponse({"success": False, "message": f"Unexpected error: {e}"})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@session_login_required
def patient_profile(request, user_id):
    patient = get_patient_info_by_user(user_id)
    if not patient:
        return JsonResponse({"success": False, "message": "Patient not found"})

    context = {"patient": patient}
    print(patient,"###########Data#########################3")
    return render(request, "patients_r.html", context)


@session_login_required
def list_doctors(request):
    """List doctors with pagination"""
    page = int(request.GET.get("page", 1))
    per_page = 1  # You can adjust this
    offset = (page - 1) * per_page

    doctors = []
    total_doctors = 0

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="aswin",
            password="Hearzap@123",
            database="hospital_db"
        )
        cursor = conn.cursor(dictionary=True)

        # ✅ Count total doctors
        cursor.execute("SELECT COUNT(*) AS total FROM doctor")
        total_doctors = cursor.fetchone()["total"]

        # ✅ Fetch paginated doctor list with specialization and user info
        cursor.execute("""
            SELECT 
                d.id AS doctor_id,
                u.name AS doctor_name,
                u.id AS doctor_user_id,
                u.email_id,
                u.username,
                d.mobile_number,
                s.name AS specialization_name
            FROM doctor d
            JOIN users u ON d.user_id = u.id
            LEFT JOIN specialization s ON d.specialization_id = s.id
            ORDER BY d.id DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        doctors = cursor.fetchall()

    except mysql.connector.Error as err:
        messages.error(request, f"Database error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    # ✅ Pagination logic
    total_pages = math.ceil(total_doctors / per_page)
    start_item = offset + 1 if total_doctors > 0 else 0
    end_item = min(offset + per_page, total_doctors)

    context = {
        "doctors": doctors,
        "page": page,
        "total_pages": total_pages,
        "pages": range(1, total_pages + 1),
        "start_item": start_item,
        "end_item": end_item,
        "total_doctors": total_doctors
    }

    return render(request, "doctors_l.html", context)



@session_login_required
def doctor_profile(request, user_id):
    doctor = get_doctor_info_by_user(user_id)
    if not doctor:
        return JsonResponse({"success": False, "message": "Doctor not found"})

    context = {"doctor": doctor}
    print(doctor,"###########Data#########################3")
    return render(request, "doctors_r.html", context)