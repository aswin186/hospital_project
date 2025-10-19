from django.db import connection

def create_tables():
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

    print("✅ Tables created successfully!")


# Run directly
if __name__ == "__main__":
    create_tables()
