CREATE DATABASE IF NOT EXISTS fingerprint_exam;

USE fingerprint_exam;

CREATE TABLE students (
    student_id VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) DEFAULT NULL,
    year INT DEFAULT NULL,
    fingerprint_id VARCHAR(50) DEFAULT NULL,
    password_hash VARCHAR(255) DEFAULT NULL,
    webauthn_credential_id TEXT,
    webauthn_public_key TEXT,
    webauthn_sign_count INT DEFAULT 0,
    PRIMARY KEY (student_id)
);

CREATE TABLE examinations (
    exam_id INT NOT NULL AUTO_INCREMENT,
    exam_name VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    exam_date DATE NOT NULL,
    start_time TIME NOT NULL,
    PRIMARY KEY (exam_id)
);

CREATE TABLE exam_registrations (
    registration_id INT NOT NULL AUTO_INCREMENT,
    student_id VARCHAR(20) DEFAULT NULL,
    exam_id INT DEFAULT NULL,
    registration_date DATE DEFAULT NULL,
    status VARCHAR(20) DEFAULT 'Registered',
    PRIMARY KEY (registration_id)
);

CREATE TABLE attendance (
    attendance_id INT NOT NULL AUTO_INCREMENT,
    student_id VARCHAR(20) DEFAULT NULL,
    exam_id INT DEFAULT NULL,
    attendance_date DATE DEFAULT NULL,
    attendance_time TIME DEFAULT NULL,
    status VARCHAR(20) DEFAULT 'Present',
    PRIMARY KEY (attendance_id)
);

CREATE TABLE authentication_logs (
    log_id INT NOT NULL AUTO_INCREMENT,
    student_id VARCHAR(20) DEFAULT NULL,
    exam_id INT DEFAULT NULL,
    authentication_time DATETIME DEFAULT NULL,
    result VARCHAR(20) DEFAULT NULL,
    PRIMARY KEY (log_id)
);