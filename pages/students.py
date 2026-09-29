import streamlit as st
import pandas as pd
import hashlib

from database import create_connection


# -----------------------------
# Password Hashing
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# -----------------------------
# Page
# -----------------------------
st.title("👨‍🎓 Student Management")
st.write("Register and manage students")


# =====================================================
# REGISTER STUDENT
# =====================================================

st.header("➕ Register New Student")

col1, col2 = st.columns(2)

with col1:
    student_id = st.text_input("Student ID")
    name = st.text_input("Student Name")
    department = st.text_input("Department")

with col2:
    year = st.number_input(
        "Year",
        min_value=1,
        max_value=4,
        value=3
    )

    password = st.text_input(
        "Create Password",
        type="password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password"
    )


if st.button("Register Student", type="primary"):

    # Check fields
    if not student_id or not name or not department or not password:

        st.warning("Please fill in all required fields.")

    elif password != confirm_password:

        st.error("Passwords do not match.")

    else:

        connection = create_connection()

        if connection:

            try:
                cursor = connection.cursor()

                # Check whether student already exists
                check_query = """
                SELECT student_id
                FROM students
                WHERE student_id = %s
                """

                cursor.execute(check_query, (student_id,))

                existing_student = cursor.fetchone()

                if existing_student:

                    st.error("Student ID already exists.")

                else:

                    # Create password hash
                    password_hash = hash_password(password)

                    # Fingerprint ID will be added later
                    fingerprint_id = None

                    insert_query = """
                    INSERT INTO students
                    (
                        student_id,
                        name,
                        department,
                        year,
                        fingerprint_id,
                        password_hash
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """

                    values = (
                        student_id,
                        name,
                        department,
                        year,
                        fingerprint_id,
                        password_hash
                    )

                    cursor.execute(insert_query, values)

                    connection.commit()

                    st.success(
                        "Student registered successfully! 🎉"
                    )

                    st.info(
                        "Fingerprint enrollment will be completed later."
                    )

                cursor.close()
                connection.close()

            except mysql.connector.Error as error:

                st.error(
                    f"Error registering student: {error}"
                )


# =====================================================
# VIEW STUDENTS
# =====================================================

st.divider()

st.header("📋 Registered Students")

connection = create_connection()

if connection:

    query = """
    SELECT
        student_id,
        name,
        department,
        year,
        fingerprint_id
    FROM students
    ORDER BY student_id
    """

    students = pd.read_sql(query, connection)

    connection.close()

    if students.empty:

        st.info("No students registered yet.")

    else:

        st.dataframe(
            students,
            use_container_width=True,
            hide_index=True
        )