# create_all_tables.py
from django.db import connection

def create_all_tables():
    with connection.cursor() as cursor:
        # ------------------------
        # 1️⃣ Role Table
        # ------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS role (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            );
        """)

        # ------------------------
        # 2️⃣ Users Table
        # ------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(150) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                password VARCHAR(255) NOT NULL,
                email_id VARCHAR(150) UNIQUE NOT NULL,
                role_id INT NOT NULL,
                FOREIGN KEY (role_id) REFERENCES role(id)
                    ON DELETE RESTRICT
                    ON UPDATE CASCADE
            );
        """)

        # ------------------------
        # 3️⃣ Specialization Table
        # ------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS specialization (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT
            );
        """)

        # ------------------------
        # 4️⃣ Doctor Table
        # ------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctor (
                id INT AUTO_INCREMENT PRIMARY KEY,
                specialization_id INT,
                user_id INT UNIQUE,
                mobile_number VARCHAR(20),
                FOREIGN KEY (specialization_id) REFERENCES specialization(id)
                    ON DELETE SET NULL
                    ON UPDATE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        """)

        # ------------------------
        # 5️⃣ Patient Table
        # ------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patient (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT UNIQUE,
                mobile_number VARCHAR(20),
                age INT,
                gender ENUM('Male','Female','Other'),
                address VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        """)

        # ------------------------
        # 6️⃣ Patient Details Table
        # ------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patient_details (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,

                address VARCHAR(255) NOT NULL,
                blood_group VARCHAR(5) NULL,
                allergies TEXT,
                medical_history TEXT,

                emergency_contact_name VARCHAR(100) NOT NULL,
                emergency_contact_relation VARCHAR(50) NOT NULL,
                emergency_contact_number VARCHAR(15) NOT NULL,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

                FOREIGN KEY (patient_id) REFERENCES patient(id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        """)

        # ------------------------
        # 7️⃣ Appointment Status Table
        # ------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointment_status (
                id INT AUTO_INCREMENT PRIMARY KEY,
                status_name VARCHAR(50) NOT NULL UNIQUE
            );
        """)

        # ------------------------
        # 8️⃣ Appointment Table
        # ------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointment (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,
                doctor_id INT NOT NULL,
                appointment_date DATE NOT NULL,
                appointment_time VARCHAR(50) NOT NULL,
                status_id INT DEFAULT 1,
                notes TEXT,
                report TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                FOREIGN KEY (patient_id) REFERENCES patient(id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES doctor(id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                FOREIGN KEY (status_id) REFERENCES appointment_status(id)
                    ON DELETE SET NULL
                    ON UPDATE CASCADE
            );
        """)

    print("✅ All tables created successfully!")


# Run directly
if __name__ == "__main__":
    create_all_tables()
