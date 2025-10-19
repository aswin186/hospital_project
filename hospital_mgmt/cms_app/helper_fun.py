
import mysql.connector


def get_patient_data(user_id):
    """Fetch full patient data for edit mode using user_id with JOINs"""
    if not user_id:
        return None

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host="localhost", user="aswin", password="Hearzap@123", database="hospital_db"
        )
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                u.id AS user_id,
                u.name,
                u.email_id,
                p.id AS patient_id,
                p.age,
                p.gender,
                p.mobile_number,
                p.address AS patient_address,
                pd.address AS details_address,
                pd.blood_group,
                pd.allergies,
                pd.medical_history,
                pd.emergency_contact_name,
                pd.emergency_contact_relation,
                pd.emergency_contact_number
            FROM users u
            LEFT JOIN patient p ON u.id = p.user_id
            LEFT JOIN patient_details pd ON p.id = pd.patient_id
            WHERE u.id = %s
        """

        cursor.execute(query, (user_id,))
        patient = cursor.fetchone()
        return patient

    except mysql.connector.Error as err:
        print("Database error:", err)
        return None
    except Exception as e:
        print("Unexpected error:", e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



def get_patient_info_by_user(user_id):
    """Fetch patient + patient_details + appointments using user_id"""
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host="localhost", user="aswin", password="Hearzap@123", database="hospital_db"
        )
        cursor = conn.cursor(dictionary=True)

        # 🩺 Fetch patient + details
        cursor.execute("""
            SELECT 
                u.id AS user_id,
                u.name AS user_name,
                u.email_id,
                p.id AS patient_id,
                p.age,
                p.gender,
                p.mobile_number,
                p.address AS patient_address,
                pd.blood_group,
                pd.allergies,
                pd.medical_history,
                pd.emergency_contact_name,
                pd.emergency_contact_relation,
                pd.emergency_contact_number
            FROM users u
            JOIN patient p ON p.user_id = u.id
            LEFT JOIN patient_details pd ON pd.patient_id = p.id
            WHERE u.id = %s
        """, (user_id,))
        patient = cursor.fetchone()

        print(patient, "######## patient ################")

        if not patient:
            return None

        # 🧩 Process comma-separated fields
        allergies = patient.get("allergies") or ""
        medical_history = patient.get("medical_history") or ""
        patient["allergies_list"] = [x.strip() for x in allergies.split(",") if x.strip()]
        patient["medical_history_list"] = [x.strip() for x in medical_history.split(",") if x.strip()]

        # 📅 Fetch appointments for this patient (Newest first)
        cursor.execute("""
            SELECT 
                a.id AS appointment_id,
                a.appointment_date,
                a.appointment_time,
                u.name AS doctor_name,
                s.status_name
            FROM appointment a
            JOIN doctor d ON a.doctor_id = d.id
            JOIN users u ON d.user_id = u.id
            JOIN appointment_status s ON a.status_id = s.id
            WHERE a.patient_id = %s
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """, (patient["patient_id"],))

        appointments = cursor.fetchall()

        # Add to patient dict
        patient["appointments"] = appointments

        print(patient, "############ data final ####################")

        return patient

    except mysql.connector.Error as err:
        print("Database error:", err)
        return None
    except Exception as e:
        print("Unexpected error:", e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_doctor_info_by_user(user_id):
    """Fetch doctor info (with specialization) and today's appointments using user_id"""
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="aswin",
            password="Hearzap@123",
            database="hospital_db"
        )
        cursor = conn.cursor(dictionary=True)

        # 1️⃣ Fetch doctor info
        cursor.execute("""
            SELECT 
                u.id AS user_id,
                u.name AS doctor_name,
                u.email_id,
                u.username,
                d.id AS doctor_id,
                d.mobile_number,
                s.name AS specialization_name
            FROM users u
            JOIN doctor d ON d.user_id = u.id
            LEFT JOIN specialization s ON d.specialization_id = s.id
            WHERE u.id = %s
        """, (user_id,))
        doctor = cursor.fetchone()
        if not doctor:
            return None

        # 2️⃣ Fetch all appointments for this doctor (newest first)
        cursor.execute("""
            SELECT 
                a.id AS appointment_id,
                a.patient_id,
                u.name AS patient_name,
                a.appointment_date,
                a.appointment_time,
                s.status_name,
                a.notes,
                a.report
            FROM appointment a
            JOIN patient p ON a.patient_id = p.id
            JOIN users u ON p.user_id = u.id
            JOIN appointment_status s ON a.status_id = s.id
            WHERE a.doctor_id = %s
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """, (doctor["doctor_id"],))
        appointments = cursor.fetchall()

        doctor["appointments"] = appointments

        print(doctor, "############# data final doc ##################")

        return doctor

    except mysql.connector.Error as err:
        print("Database error:", err)
        return None
    except Exception as e:
        print("Unexpected error:", e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
