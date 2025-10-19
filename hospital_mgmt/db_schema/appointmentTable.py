from django.db import connection

def create_appointments_details_table():
    with connection.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointment_status (
            id INT AUTO_INCREMENT PRIMARY KEY,
            status_name VARCHAR(50) NOT NULL UNIQUE
        )
        """)
        print("✅ appointment_status table created successfully")


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
        )
        """)
        print("✅ appointment table created successfully")


# Run directly
if __name__ == "__main__":
    create_appointments_details_table()
