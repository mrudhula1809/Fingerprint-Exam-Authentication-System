import streamlit as st
from database import create_connection
from datetime import datetime

st.title("🔐 Examination Authentication")

st.write("Authenticate the student before entering the examination.")

# -----------------------------------
# Connect to database
# -----------------------------------
connection = create_connection()

if not connection:
    st.error("❌ Could not connect to database.")
    st.stop()

cursor = connection.cursor(dictionary=True)

# -----------------------------------
# Get available exams
# -----------------------------------
cursor.execute("""
    SELECT exam_id, exam_name, subject, exam_date, start_time
    FROM examinations
    ORDER BY exam_date, start_time
""")

exams = cursor.fetchall()

# -----------------------------------
# Exam selection
# -----------------------------------
if not exams:
    st.warning("⚠️ No examinations have been created yet.")
    cursor.close()
    connection.close()
    st.stop()

exam_options = {}

for exam in exams:
    label = (
        f"{exam['exam_name']} - "
        f"{exam['subject']} - "
        f"{exam['exam_date']}"
    )
    exam_options[label] = exam["exam_id"]

selected_exam = st.selectbox(
    "Select Examination",
    list(exam_options.keys())
)

exam_id = exam_options[selected_exam]

st.divider()

# -----------------------------------
# Student ID
# -----------------------------------
student_id = st.text_input(
    "Student ID",
    placeholder="Example: TEST001"
)

st.divider()

# -----------------------------------
# Fingerprint
# -----------------------------------
st.subheader("👆 Fingerprint Authentication")

st.info(
    "For now, enter the registered Fingerprint ID for testing. "
    "The real fingerprint scanner will be connected later."
)

fingerprint_id = st.text_input(
    "Fingerprint ID",
    placeholder="Example: FP001"
)

# -----------------------------------
# Authenticate
# -----------------------------------
if st.button("Authenticate", type="primary"):

    if not student_id or not fingerprint_id:
        st.warning(
            "Please enter Student ID and Fingerprint ID."
        )

    else:

        # -----------------------------------
        # Find student
        # -----------------------------------
        cursor.execute("""
            SELECT
                student_id,
                name,
                department,
                year,
                fingerprint_id
            FROM students
            WHERE student_id = %s
        """, (student_id,))

        student = cursor.fetchone()

        if student is None:

            st.error("❌ Student not found.")

            # Save failed authentication
            cursor.execute("""
                INSERT INTO authentication_logs
                (student_id, exam_id, authentication_time, result)
                VALUES (%s, %s, %s, %s)
            """, (
                student_id,
                exam_id,
                datetime.now(),
                "FAILED"
            ))

            connection.commit()

        # -----------------------------------
        # Check fingerprint
        # -----------------------------------
        elif student["fingerprint_id"] != fingerprint_id:

            st.error("❌ Fingerprint authentication failed.")

            cursor.execute("""
                INSERT INTO authentication_logs
                (student_id, exam_id, authentication_time, result)
                VALUES (%s, %s, %s, %s)
            """, (
                student_id,
                exam_id,
                datetime.now(),
                "FAILED"
            ))

            connection.commit()

        else:

            # -----------------------------------
            # Fingerprint successful
            # -----------------------------------
            st.success(
                "✅ Fingerprint authentication successful!"
            )

            # -----------------------------------
            # Check exam registration
            # -----------------------------------
            cursor.execute("""
                SELECT registration_id, status
                FROM exam_registrations
                WHERE student_id = %s
                AND exam_id = %s
                AND status = 'Registered'
            """, (
                student_id,
                exam_id
            ))

            registration = cursor.fetchone()

            if registration is None:

                st.error(
                    "❌ Student is not registered for this examination."
                )

                # Save authentication result
                cursor.execute("""
                    INSERT INTO authentication_logs
                    (student_id, exam_id, authentication_time, result)
                    VALUES (%s, %s, %s, %s)
                """, (
                    student_id,
                    exam_id,
                    datetime.now(),
                    "NOT_REGISTERED"
                ))

                connection.commit()

            else:

                # -----------------------------------
                # Save successful authentication
                # -----------------------------------
                cursor.execute("""
                    INSERT INTO authentication_logs
                    (student_id, exam_id, authentication_time, result)
                    VALUES (%s, %s, %s, %s)
                """, (
                    student_id,
                    exam_id,
                    datetime.now(),
                    "SUCCESS"
                ))

                # -----------------------------------
                # Check existing attendance
                # -----------------------------------
                cursor.execute("""
                    SELECT attendance_id
                    FROM attendance
                    WHERE student_id = %s
                    AND exam_id = %s
                """, (
                    student_id,
                    exam_id
                ))

                existing_attendance = cursor.fetchone()

                if existing_attendance:

                    st.warning(
                        "⚠️ Attendance has already been marked "
                        "for this examination."
                    )

                else:

                    # -----------------------------------
                    # Mark attendance
                    # -----------------------------------
                    now = datetime.now()

                    cursor.execute("""
                        INSERT INTO attendance
                        (
                            student_id,
                            exam_id,
                            attendance_date,
                            attendance_time,
                            status
                        )
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        student_id,
                        exam_id,
                        now.date(),
                        now.time(),
                        "Present"
                    ))

                    st.success(
                        "🎉 Authentication successful!"
                    )

                    st.success(
                        "✅ Attendance marked as PRESENT."
                    )

                    st.write(
                        f"**Student Name:** {student['name']}"
                    )

                    st.write(
                        f"**Student ID:** {student['student_id']}"
                    )

                    st.write(
                        f"**Exam:** {selected_exam}"
                    )

                connection.commit()

# -----------------------------------
# Close database connection
# -----------------------------------
cursor.close()
connection.close()