import streamlit as st
import pandas as pd

from database import create_connection


# -----------------------------
# Page
# -----------------------------
st.title("📝 Examination Management")
st.write("Create and manage examinations")


# =====================================================
# CREATE EXAM
# =====================================================

st.header("➕ Create New Examination")

col1, col2 = st.columns(2)

with col1:

    exam_name = st.text_input("Exam Name")

    subject = st.text_input("Subject")


with col2:

    exam_date = st.date_input("Exam Date")

    start_time = st.time_input("Start Time")


if st.button("Create Examination", type="primary"):

    if not exam_name or not subject:

        st.warning("Please enter Exam Name and Subject.")

    else:

        connection = create_connection()

        if connection:

            try:

                cursor = connection.cursor()

                query = """
                INSERT INTO examinations
                (exam_name, subject, exam_date, start_time)
                VALUES (%s, %s, %s, %s)
                """

                values = (
                    exam_name,
                    subject,
                    exam_date,
                    start_time
                )

                cursor.execute(query, values)

                connection.commit()

                cursor.close()
                connection.close()

                st.success(
                    "Examination created successfully! 🎉"
                )

            except mysql.connector.Error as error:

                st.error(
                    f"Error creating examination: {error}"
                )


# =====================================================
# VIEW EXAMINATIONS
# =====================================================

st.divider()

st.header("📋 Available Examinations")

connection = create_connection()

if connection:

    query = """
    SELECT
        exam_id,
        exam_name,
        subject,
        exam_date,
        start_time
    FROM examinations
    ORDER BY exam_date, start_time
    """

    exams = pd.read_sql(query, connection)

    connection.close()

    if exams.empty:

        st.info("No examinations created yet.")

    else:

        st.dataframe(
            exams,
            use_container_width=True, 
            hide_index=True
        )
# =====================================================
# STUDENT EXAM REGISTRATION
# =====================================================

st.divider()

st.header("🎓 Student Exam Registration")


# Check whether a student is logged in
if not st.session_state.get("logged_in", False):

    st.warning("Please login as a student to register for an examination.")

else:

    student_id = st.session_state.get("student_id")
    student_name = st.session_state.get("student_name")

    st.write(f"Welcome, **{student_name}**!")
    st.write(f"Student ID: **{student_id}**")


    connection = create_connection()

    if connection:

        try:

            cursor = connection.cursor(dictionary=True)

            # Get available examinations
            query = """
            SELECT
                exam_id,
                exam_name,
                subject,
                exam_date,
                start_time
            FROM examinations
            ORDER BY exam_date, start_time
            """

            cursor.execute(query)

            exams = cursor.fetchall()

            if not exams:

                st.info("No examinations are currently available.")

            else:

                exam_options = {
                    f"{exam['exam_name']} - {exam['subject']} - "
                    f"{exam['exam_date']}": exam['exam_id']
                    for exam in exams
                }

                selected_exam = st.selectbox(
                    "Select an examination",
                    list(exam_options.keys())
                )

                selected_exam_id = exam_options[selected_exam]


                if st.button("Register for Examination"):

                    # Check whether already registered
                    check_query = """
                    SELECT registration_id
                    FROM exam_registrations
                    WHERE student_id = %s
                    AND exam_id = %s
                    """

                    cursor.execute(
                        check_query,
                        (student_id, selected_exam_id)
                    )

                    existing_registration = cursor.fetchone()


                    if existing_registration:

                        st.warning(
                            "You are already registered for this examination."
                        )

                    else:

                        insert_query = """
                        INSERT INTO exam_registrations
                        (
                            student_id,
                            exam_id,
                            registration_date,
                            status
                        )
                        VALUES (%s, %s, CURDATE(), 'Registered')
                        """

                        cursor.execute(
                            insert_query,
                            (student_id, selected_exam_id)
                        )

                        connection.commit()

                        st.success(
                            "Successfully registered for the examination! 🎉"
                        )


            cursor.close()
            connection.close()

        except mysql.connector.Error as error:

            st.error(
                f"Exam registration error: {error}"
            )