import mysql.connector
from datetime import date, datetime
from django.shortcuts import render
from django.db import connection
from auth_app.decorators import session_login_required


@session_login_required
def dashboard_view(request):
    today = date.today()

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="aswin",
            password="Hearzap@123",
            database="hospital_db"
        )
        cursor = conn.cursor(dictionary=True)

        # 1️⃣ Today's Bookings
        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM appointment
            WHERE appointment_date = %s
        """, (today,))
        todays_bookings = cursor.fetchone()['count']

        # 2️⃣ Total Doctors Count
        cursor.execute("SELECT COUNT(*) AS count FROM doctor")
        total_doctors = cursor.fetchone()['count']

        # 3️⃣ Upcoming Appointments (Scheduled and in the future)
        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM appointment a
            JOIN appointment_status s ON a.status_id = s.id
            WHERE appointment_date >= %s AND s.status_name = 'Scheduled'
        """, (today,))
        upcoming_appointments = cursor.fetchone()['count']

        # 4️⃣ Today’s Scheduled Appointments (for “Recent Activity”)
        cursor.execute("""
            SELECT 
                a.id,
                up.name AS patient_name,
                ud.name AS doctor_name,
                a.appointment_time,
                s.status_name
            FROM appointment a
            JOIN patient p ON a.patient_id = p.id
            JOIN users up ON p.user_id = up.id
            JOIN doctor d ON a.doctor_id = d.id
            JOIN users ud ON d.user_id = ud.id
            JOIN appointment_status s ON a.status_id = s.id
            WHERE a.appointment_date = %s 
            AND s.status_name = 'Scheduled'
            ORDER BY a.appointment_time ASC
            LIMIT 5
        """, (today,))
        todays_scheduled = cursor.fetchall()


        # 5️⃣ Doctor Availability: Doctor name + today’s appointment count
        cursor.execute("""
            SELECT 
                d.id AS doctor_id,
                u.name AS doctor_name,
                sp.name AS specialization_name,
                COUNT(a.id) AS today_appointments
            FROM doctor d
            JOIN users u ON d.user_id = u.id
            LEFT JOIN specialization sp ON d.specialization_id = sp.id
            LEFT JOIN appointment a 
                ON a.doctor_id = d.id 
                AND a.appointment_date = %s
            GROUP BY d.id, u.name, sp.name
            ORDER BY u.name
        """, (today,))
        doctor_availability = cursor.fetchall()


        # Mark doctors “Available” if less than 10 appointments (example limit)
        for doc in doctor_availability:
            doc['status'] = "Available" if doc['today_appointments'] < 10 else "Busy"

    finally:
        cursor.close()
        conn.close()

    # Pass data to template
    context = {
        'todays_bookings': todays_bookings,
        'total_doctors': total_doctors,
        'upcoming_appointments': upcoming_appointments,
        'todays_scheduled': todays_scheduled,
        'doctor_availability': doctor_availability,
        'today': today,
    }

    print(context, "########### data #############")
    return render(request, 'dashboard.html', context)
