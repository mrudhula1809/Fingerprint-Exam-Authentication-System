import streamlit as st
import pandas as pd
from datetime import datetime

from database import create_connection


# -----------------------------
# Page
# -----------------------------
st.title("🕒 Examination Attendance")
st.write("Mark and manage examination attendance")


# =====================================================
# MARK ATTENDANCE
# =====================================================

st.header("➕ Mark Student Attendance")

connection = create_connection()

if connection:

    try:
        cursor = connection.cursor(dictionary=True)

        # Get available examinations
        cursor.execute("""
            SELECT
                exam_id,
                exam_name,
                subject,
                exam_date,
                start_time
            FROM examinations
            ORDER BY exam_date, start_time
        """)

        exams = cursor.fetchall()

        if not exams:

            st.info("No examinations are available.")

        else:

            # Examination selection
            exam_options = {
                f"{exam['exam_name']} - {exam['subject']} - {exam['exam_date']}":
                exam['exam_id']
                for exam in exams
            }

            selected_exam = st.selectbox(
                "Select Examination",
                list(exam_options.keys())
            )

            selected_exam_id = exam_options[selected_exam]

            # Student ID
            student_id = st.text_input(
                "Student ID",
                placeholder="Enter Student ID"
            )

            # Mark attendance
            if st.button("Mark Attendance", type="primary"):

                if not student_id:

                    st.warning("Please enter Student ID.")

                else:

                    # Check whether student exists
                    cursor.execute("""
                        SELECT student_id, name
                        FROM students
                        WHERE student_id = %s
                    """, (student_id,))

                    student = cursor.fetchone()

                    if not student:

                        st.error("Student not found.")

                    else:

                        # Check exam registration
                        cursor.execute("""
                            SELECT registration_id
                            FROM exam_registrations
                            WHERE student_id = %s
                            AND exam_id = %s
                            AND status = 'Registered'
                        """, (student_id, selected_exam_id))

                        registration = cursor.fetchone()

                        if not registration:

                            st.error(
                                "Student is not registered for this examination."
                            )

                        else:

                            # Check duplicate attendance
                            cursor.execute("""
                                SELECT attendance_id
                                FROM attendance
                                WHERE student_id = %s
                                AND exam_id = %s
                            """, (student_id, selected_exam_id))

                            existing_attendance = cursor.fetchone()

                            if existing_attendance:

                                st.warning(
                                    "Attendance has already been marked for this student."
                                )

                            else:

                                # Current date and time
                                current_datetime = datetime.now()

                                attendance_date = current_datetime.date()
                                attendance_time = current_datetime.time()

                                # Insert attendance
                                cursor.execute("""
                                    INSERT INTO attendance
                                    (
                                        student_id,
                                        exam_id,
                                        attendance_date,
                                        attendance_time,
                                        status
                                    )
                                    VALUES (%s, %s, %s, %s, 'Present')
                                """, (
                                    student_id,
                                    selected_exam_id,
                                    attendance_date,
                                    attendance_time
                                ))

                                connection.commit()

                                st.success(
                                    f"Attendance marked successfully for "
                                    f"{student['name']}! ✅"
                                )

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:

        st.error(
            f"Attendance error: {error}"
        )


# =====================================================
# VIEW ATTENDANCE
# =====================================================

st.divider()

st.header("📋 Attendance Records")

connection = create_connection()

if connection:

    try:

        query = """
            SELECT
                a.attendance_id,
                a.student_id,
                s.name AS student_name,
                e.exam_name,
                e.subject,
                a.attendance_date,
                a.attendance_time,
                a.status
            FROM attendance a
            JOIN students s
                ON a.student_id = s.student_id
            JOIN examinations e
                ON a.exam_id = e.exam_id
            ORDER BY
                a.attendance_date DESC,
                a.attendance_time DESC
        """

        attendance = pd.read_sql(query, connection)

        connection.close()

        if attendance.empty:

            st.info("No attendance records yet.")

        else:

            st.dataframe(
                attendance,
                use_container_width=True,
                hide_index=True
            )

    except mysql.connector.Error as error:

        st.error(
            f"Error loading attendance records: {error}"
        )