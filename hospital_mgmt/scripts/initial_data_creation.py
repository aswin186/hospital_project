import mysql.connector
import os
import sys

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_mgmt.settings')

import django
django.setup()

from django.contrib.auth.hashers import make_password

def insert_sample_data():
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="aswin",                # your DB username
            password="Hearzap@123",      # your DB password
            database="hospital_db"
        )
        cursor = conn.cursor()

        # ------------------------
        # 1️⃣ Insert Roles
        # ------------------------
        roles = [('staff',), ('doctor',), ('patient',)]
        cursor.executemany("INSERT INTO role (name) VALUES (%s) ON DUPLICATE KEY UPDATE name=name;", roles)

        # Fetch role IDs dynamically
        cursor.execute("SELECT id, name FROM role")
        role_map = {name: role_id for role_id, name in cursor.fetchall()}

        # ------------------------
        # 2️⃣ Insert Staff Users
        # ------------------------
        staff_data = [
            ('staff1', 'John Staff', make_password('staff123'), 'johnstaff@example.com', role_map['staff']),
            ('staff2', 'Mary Staff', make_password('staff456'), 'marystaff@example.com', role_map['staff'])
        ]
        cursor.executemany("""
            INSERT INTO users (username, name, password, email_id, role_id)
            VALUES (%s, %s, %s, %s, %s)
        """, staff_data)

        # ------------------------
        # 3️⃣ Insert Doctors (as Users)
        # ------------------------
        doctor_data = [
            ('doc1', 'Dr. Ravi', make_password('doc123'), 'ravi@example.com', role_map['doctor']),
            ('doc2', 'Dr. Priya', make_password('doc456'), 'priya@example.com', role_map['doctor'])
        ]
        cursor.executemany("""
            INSERT INTO users (username, name, password, email_id, role_id)
            VALUES (%s, %s, %s, %s, %s)
        """, doctor_data)

        # ------------------------
        # 4️⃣ Insert Specializations
        # ------------------------
        specializations = [
            ('Cardiologist', 'Specialist in heart-related diseases'),
            ('Neurologist', 'Specialist in brain and nerve disorders'),
            ('Orthopedic Surgeon', 'Specialist in bones and muscles')
        ]
        cursor.executemany("""
            INSERT INTO specialization (name, description)
            VALUES (%s, %s)
        """, specializations)

        # ------------------------
        # 5️⃣ Insert Doctors into doctor table
        # ------------------------
        # Fetch specialization IDs
        cursor.execute("SELECT id, name FROM specialization")
        spec_map = {name: spec_id for spec_id, name in cursor.fetchall()}

        # Fetch doctor user IDs
        cursor.execute("SELECT id, username FROM users WHERE role_id=%s", (role_map['doctor'],))
        doctor_map = {username: user_id for user_id, username in cursor.fetchall()}

        doctor_table_data = [
            (spec_map['Cardiologist'], doctor_map['doc1'], '9876543210'),
            (spec_map['Neurologist'], doctor_map['doc2'], '9123456780')
        ]
        cursor.executemany("""
            INSERT INTO doctor (specialization_id, user_id, mobile_number)
            VALUES (%s, %s, %s)
        """, doctor_table_data)

        # ------------------------
        # 6️⃣ Insert Patient Users
        # ------------------------
        patient_users = [
            ('puser1', 'Arun Kumar', make_password('pass123'), 'arun@example.com', role_map['patient']),
            ('puser2', 'Meena Devi', make_password('pass456'), 'meena@example.com', role_map['patient']),
            ('puser3', 'Vijay Kumar', make_password('pass789'), 'vijay@example.com', role_map['patient']),
            ('puser4', 'Lakshmi Nair', make_password('pass321'), 'lakshmi@example.com', role_map['patient']),
            ('puser5', 'Kiran Raj', make_password('pass654'), 'kiran@example.com', role_map['patient'])
        ]
        cursor.executemany("""
            INSERT INTO users (username, name, password, email_id, role_id)
            VALUES (%s, %s, %s, %s, %s)
        """, patient_users)

        # Fetch patient user IDs
        cursor.execute("SELECT id, username FROM users WHERE username LIKE 'puser%' ORDER BY id ASC")
        patient_map = {username: user_id for user_id, username in cursor.fetchall()}

        patient_table_data = [
            (patient_map['puser1'], '9988776655', 30, 'Male', 'Chennai'),
            (patient_map['puser2'], '9876501234', 28, 'Female', 'Bangalore'),
            (patient_map['puser3'], '9123456700', 35, 'Male', 'Hyderabad'),
            (patient_map['puser4'], '9234567890', 40, 'Female', 'Kochi'),
            (patient_map['puser5'], '9345678901', 25, 'Male', 'Coimbatore')
        ]
        cursor.executemany("""
            INSERT INTO patient (user_id, mobile_number, age, gender, address)
            VALUES (%s, %s, %s, %s, %s)
        """, patient_table_data)

        conn.commit()
        print("✅ Sample data inserted successfully!")

    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# Run directly
if __name__ == "__main__":
    insert_sample_data()
