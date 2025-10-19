from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from auth_app.decorators import session_login_required
import mysql.connector
from datetime import datetime, date
import math
import json



@session_login_required
def list_appointments(request):
    """List appointments with patient and doctor info (raw SQL)"""
    page = int(request.GET.get("page", 1))
    per_page = 10
    offset = (page - 1) * per_page

    appointments = []
    total_appointments = 0

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="aswin",
            password="Hearzap@123",
            database="hospital_db"
        )
        cursor = conn.cursor(dictionary=True)

        # ✅ Count total appointments
        cursor.execute("SELECT COUNT(*) AS total FROM appointment")
        total_appointments = cursor.fetchone()["total"]

        # ✅ Fetch paginated appointments with patient & doctor info
        cursor.execute("""
            SELECT 
                a.id AS appointment_id,
                a.appointment_date,
                a.appointment_time,
                a.notes,
                a.report,
                s.status_name,
                p.id AS patient_id,
                u1.name AS patient_name,
                p.mobile_number AS patient_mobile,
                d.id AS doctor_id,
                u2.name AS doctor_name,
                d.mobile_number AS doctor_mobile,
                sp.name AS specialization_name
            FROM appointment a
            JOIN patient p ON a.patient_id = p.id
            JOIN users u1 ON p.user_id = u1.id
            JOIN doctor d ON a.doctor_id = d.id
            JOIN users u2 ON d.user_id = u2.id
            LEFT JOIN specialization sp ON d.specialization_id = sp.id
            LEFT JOIN appointment_status s ON a.status_id = s.id
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        appointments = cursor.fetchall()

    except mysql.connector.Error as err:
        messages.error(request, f"Database error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    # ✅ Pagination logic
    total_pages = math.ceil(total_appointments / per_page)
    start_item = offset + 1 if total_appointments > 0 else 0
    end_item = min(offset + per_page, total_appointments)

    context = {
        "appointments": appointments,
        "page": page,
        "total_pages": total_pages,
        "pages": range(1, total_pages + 1),
        "start_item": start_item,
        "end_item": end_item,
        "total_appointments": total_appointments
    }

    print(context, "############## context ################y")
    return render(request, 'appointments_l.html', context)



@session_login_required
def appointment_create(request):
    patients = []
    doctors = []
    time_slots = [
        "10:00 AM To 10:30 AM",
        "10:30 AM To 11:00 AM",
        "11:00 AM To 11:30 AM",
        "11:30 AM To 12:00 PM",
        "12:00 PM To 12:30 PM",
    ]

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="aswin",
            password="Hearzap@123",
            database="hospital_db"
        )
        cursor = conn.cursor(dictionary=True)

        # Fetch Patients
        cursor.execute("""
            SELECT p.id, u.name 
            FROM patient p 
            JOIN users u ON p.user_id = u.id
            ORDER BY u.name ASC
        """)
        patients = cursor.fetchall()

        # Fetch Doctors
        cursor.execute("""
            SELECT d.id, u.name 
            FROM doctor d 
            JOIN users u ON d.user_id = u.id
            ORDER BY u.name ASC
        """)
        doctors = cursor.fetchall()

        # Handle form submission
        if request.method == "POST":
            patient_id = request.POST.get("patient")
            doctor_id = request.POST.get("doctor")
            appointment_date = request.POST.get("selected_date")
            appointment_time = request.POST.get("time")
            notes = request.POST.get("notes")

            print(patient_id,doctor_id, appointment_date, appointment_time, notes, "######### post data #################")

            # Validate inputs
            if not (patient_id and doctor_id and appointment_date and appointment_time):
                messages.error(request, "All fields are required.")
                return redirect("appointment_create")

            # Check if the doctor already has 2 appointments in this slot
            cursor.execute("""
                SELECT COUNT(*) AS count
                FROM appointment
                WHERE doctor_id = %s 
                  AND appointment_date = %s 
                  AND appointment_time = %s
            """, (doctor_id, appointment_date, appointment_time))
            result = cursor.fetchone()
            existing_count = result["count"]

            if existing_count >= 2:
                messages.error(request, "This doctor already has 2 appointments in this time slot.")
                return redirect("appointment_create")

            # Insert appointment
            cursor.execute("""
                INSERT INTO appointment (patient_id, doctor_id, appointment_date, appointment_time, notes)
                VALUES (%s, %s, %s, %s, %s)
            """, (patient_id, doctor_id, appointment_date, appointment_time, notes))
            conn.commit()

            messages.success(request, "Appointment created successfully.")
            return redirect("appointments_list")

    except mysql.connector.Error as err:
        messages.error(request, f"Database error: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    context = {
        "patients": patients,
        "doctors": doctors,
        "time_slots": time_slots,
    }
    return render(request, 'appointments_c.html', context)



@session_login_required
def appointment_detail(request, appointment_id):
    """Fetch appointment details and decide which buttons to show"""
    appointment = None

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="aswin",
            password="Hearzap@123",
            database="hospital_db"
        )
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                a.id AS appointment_id,
                a.appointment_date,
                a.appointment_time,
                a.notes,
                a.report,
                s.status_name,
                p.id AS patient_id,
                u1.name AS patient_name,
                p.mobile_number AS patient_mobile,
                d.id AS doctor_id,
                u2.name AS doctor_name,
                d.mobile_number AS doctor_mobile,
                sp.name AS specialization_name
            FROM appointment a
            JOIN patient p ON a.patient_id = p.id
            JOIN users u1 ON p.user_id = u1.id
            JOIN doctor d ON a.doctor_id = d.id
            JOIN users u2 ON d.user_id = u2.id
            LEFT JOIN specialization sp ON d.specialization_id = sp.id
            LEFT JOIN appointment_status s ON a.status_id = s.id
            WHERE a.id = %s
        """, (appointment_id,))
        appointment = cursor.fetchone()

        if not appointment:
            messages.error(request, "Appointment not found")
            return render(request, "appointment_detail.html", {"appointment": None})

        # Determine which buttons to show
        today_date = date.today()
        app_date = appointment["appointment_date"]
        status = appointment["status_name"].lower() if appointment["status_name"] else "scheduled"

        buttons = {
            "show_mark_as_arrived": False,
            "show_cancel": False,
            "show_no_show": False,
            "show_mark_complete": False
        }

        if status == "scheduled":
            print(status)
            print(app_date)
            print(today_date)
            if app_date >= today_date:
                buttons["show_mark_as_arrived"] = True
                buttons["show_cancel"] = True
            elif app_date < today_date:
                buttons["show_no_show"] = True
        elif status == "in-progress":
            buttons["show_mark_complete"] = True
        elif status == "completed" or status == "cancelled" or status == "no-show":
            pass

        appointment["buttons"] = buttons

    except mysql.connector.Error as err:
        messages.error(request, f"Database error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    print(appointment, "######## data ################")
    return render(request, "appointments_r.html", {"appointment": appointment})



# Map actions to appointment_status names
ACTION_STATUS_MAP = {
    "mark_as_arrived": "In-Progress",
    "mark_complete": "Completed",
    "cancel": "Cancelled",
    "no_show": "No-Show",
}

# Helper for AJAX detection
def is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"

@session_login_required
def update_appointment_status(request, appointment_id, action):
    """
    Update appointment status based on the action.
    For 'mark_complete', optionally accept 'report' from POST body (AJAX or form).
    """
    if action not in ACTION_STATUS_MAP:
        if is_ajax(request):
            return JsonResponse({"success": False, "error": "Invalid action"})
        messages.error(request, "Invalid action.")
        return redirect('appointment_detail', appointment_id=appointment_id)

    status_name = ACTION_STATUS_MAP[action]

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="aswin",
            password="Hearzap@123",
            database="hospital_db"
        )
        cursor = conn.cursor(dictionary=True)

        # Get status_id for the status_name
        cursor.execute("SELECT id FROM appointment_status WHERE status_name = %s", (status_name,))
        status_row = cursor.fetchone()
        if not status_row:
            err_msg = f"Status '{status_name}' not found in the database."
            if is_ajax(request):
                return JsonResponse({"success": False, "error": err_msg})
            messages.error(request, err_msg)
            return redirect('appointment_detail', appointment_id=appointment_id)

        status_id = status_row['id']

        # Fetch the appointment
        cursor.execute("SELECT status_id, appointment_date FROM appointment WHERE id = %s", (appointment_id,))
        appointment = cursor.fetchone()
        if not appointment:
            err_msg = "Appointment not found."
            if is_ajax(request):
                return JsonResponse({"success": False, "error": err_msg})
            messages.error(request, err_msg)
            return redirect('appointment_list')

        # Validation: Cannot mark future appointment as No-Show
        if action == "no_show" and appointment["appointment_date"] >= date.today():
            err_msg = "Cannot mark a future appointment as No-Show."
            if is_ajax(request):
                return JsonResponse({"success": False, "error": err_msg})
            messages.error(request, err_msg)
            return redirect('appointment_detail', appointment_id=appointment_id)

        # Prepare optional report
        report = None
        if action == "mark_complete":
            if request.method == "POST" and request.content_type == "application/json":
                try:
                    data = json.loads(request.body)
                    report = data.get("report", "")
                except json.JSONDecodeError:
                    report = ""
            elif request.method == "POST":
                report = request.POST.get("report", "")

        # Update appointment
        if report is not None:
            cursor.execute("""
                UPDATE appointment
                SET status_id = %s, report = %s, updated_at = NOW()
                WHERE id = %s
            """, (status_id, report, appointment_id))
        else:
            cursor.execute("""
                UPDATE appointment
                SET status_id = %s, updated_at = NOW()
                WHERE id = %s
            """, (status_id, appointment_id))

        conn.commit()

        # Success response
        if is_ajax(request):
            print("############################################# ajax #################################################################################################################################")
            return JsonResponse({"success": True})
        messages.success(request, f"Appointment status updated to '{status_name}'.")

    except mysql.connector.Error as err:
        if is_ajax(request):
            return JsonResponse({"success": False, "error": str(err)})
        messages.error(request, f"Database error: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    # Normal redirect for non-AJAX requests
    return redirect('appointment_detail', appointment_id=appointment_id)