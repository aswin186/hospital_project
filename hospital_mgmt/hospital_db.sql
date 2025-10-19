CREATE DATABASE hospital_db;
USE hospital_db;

-- 1️⃣ Role Table (replaces department)
CREATE TABLE role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL  -- e.g., 'admin', 'doctor', 'staff', 'patient'
);

-- 2️⃣ Users Table (auth_app)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,  -- e.g., "USR001-John"
    name VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email_id VARCHAR(150) UNIQUE NOT NULL,
    role_id INT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES role(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- 3️⃣ Specialization Table
CREATE TABLE specialization (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- 4️⃣ Doctor Table
CREATE TABLE doctor (
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

-- 5️⃣ Patient Table
CREATE TABLE patient (
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


CREATE TABLE patient_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,  -- links to 'patient' table

    address VARCHAR(255) NOT NULL,
    blood_group VARCHAR(5) NULL,
    allergies TEXT,
    medical_history TEXT,

    emergency_contact_name VARCHAR(100) NOT NULL,
    emergency_contact_relation VARCHAR(50) NOT NULL,
    emergency_contact_number VARCHAR(15) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_patient_details_patient
        FOREIGN KEY (patient_id) REFERENCES patient(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


CREATE TABLE appointment_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    status_name VARCHAR(50) NOT NULL UNIQUE  -- e.g., Scheduled, Completed, Cancelled, No-Show
);


CREATE TABLE appointment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time VARCHAR(50) NOT NULL,
    status_id INT DEFAULT 1,  -- Default to 'Scheduled'
    notes TEXT,
    report TEXT,  -- path to report file if uploaded
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
