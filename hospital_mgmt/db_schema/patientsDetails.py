from django.db import connection

def create_patient_details_table():
    with connection.cursor() as cursor:
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

    print("✅ patient_details table created successfully!")


# Run directly
if __name__ == "__main__":
    create_patient_details_table()
