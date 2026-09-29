import streamlit as st
from database import create_connection

st.title("📊 Examination Dashboard")

st.write("Overview of students, examinations, attendance and authentication.")

connection = create_connection()

if not connection:
    st.error("❌ Could not connect to database.")
    st.stop()

cursor = connection.cursor(dictionary=True)

# ---------------------------------------
# Dashboard Statistics
# ---------------------------------------

# Total students
cursor.execute("SELECT COUNT(*) AS total FROM students")
total_students = cursor.fetchone()["total"]

# Total examinations
cursor.execute("SELECT COUNT(*) AS total FROM examinations")
total_exams = cursor.fetchone()["total"]

# Total present
cursor.execute("""
    SELECT COUNT(*) AS total
    FROM attendance
    WHERE status = 'Present'
""")
total_present = cursor.fetchone()["total"]

# Successful authentications
cursor.execute("""
    SELECT COUNT(*) AS total
    FROM authentication_logs
    WHERE result = 'SUCCESS'
""")
successful_auth = cursor.fetchone()["total"]

# Failed authentications
cursor.execute("""
    SELECT COUNT(*) AS total
    FROM authentication_logs
    WHERE result = 'FAILED'
""")
failed_auth = cursor.fetchone()["total"]


# ---------------------------------------
# Display Statistics
# ---------------------------------------

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("👨‍🎓 Students", total_students)

with col2:
    st.metric("📝 Examinations", total_exams)

with col3:
    st.metric("✅ Present", total_present)

with col4:
    st.metric("🔐 Successful Auth", successful_auth)

with col5:
    st.metric("❌ Failed Auth", failed_auth)


st.divider()


# ---------------------------------------
# Recent Attendance
# ---------------------------------------

st.subheader("📋 Recent Attendance")

cursor.execute("""
    SELECT
        a.attendance_id,
        a.student_id,
        s.name,
        e.exam_name,
        e.subject,
        a.attendance_date,
        a.attendance_time,
        a.status
    FROM attendance a
    LEFT JOIN students s
        ON a.student_id = s.student_id
    LEFT JOIN examinations e
        ON a.exam_id = e.exam_id
    ORDER BY a.attendance_id DESC
    LIMIT 10
""")

attendance_records = cursor.fetchall()

if attendance_records:
    st.dataframe(
        attendance_records,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No attendance records available.")


st.divider()


# ---------------------------------------
# Authentication Logs
# ---------------------------------------

st.subheader("🔐 Recent Authentication Logs")

cursor.execute("""
    SELECT
        al.log_id,
        al.student_id,
        s.name,
        e.exam_name,
        e.subject,
        al.authentication_time,
        al.result
    FROM authentication_logs al
    LEFT JOIN students s
        ON al.student_id = s.student_id
    LEFT JOIN examinations e
        ON al.exam_id = e.exam_id
    ORDER BY al.log_id DESC
    LIMIT 10
""")

authentication_records = cursor.fetchall()

if authentication_records:
    st.dataframe(
        authentication_records,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No authentication records available.")


st.divider()


# ---------------------------------------
# Examination List
# ---------------------------------------

st.subheader("📝 Examinations")

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

exam_records = cursor.fetchall()

if exam_records:
    st.dataframe(
        exam_records,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No examinations available.")


cursor.close()
connection.close()