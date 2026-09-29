import streamlit as st
import pandas as pd
from database import create_connection

st.title("📊 Examination Reports")

st.write("View attendance and authentication reports.")

connection = create_connection()

if not connection:
    st.error("❌ Could not connect to database.")
    st.stop()

# --------------------------------------------------
# Select Report
# --------------------------------------------------

report_type = st.selectbox(
    "Select Report",
    [
        "Attendance Report",
        "Authentication Report",
        "Student Attendance Summary"
    ]
)

st.divider()

# ==================================================
# ATTENDANCE REPORT
# ==================================================

if report_type == "Attendance Report":

    st.subheader("📋 Attendance Report")

    query = """
        SELECT
            er.registration_id AS ID,
            er.student_id AS `Student ID`,
            s.name AS `Student Name`,
            s.department AS Department,
            e.exam_name AS Examination,
            e.subject AS Subject,
            e.exam_date AS `Exam Date`,
            CASE
                WHEN a.attendance_id IS NOT NULL
                     AND a.status = 'Present'
                THEN 'Present'
                ELSE 'Absent'
            END AS Status,
            a.attendance_time AS `Attendance Time`
        FROM exam_registrations er

        LEFT JOIN students s
            ON er.student_id = s.student_id

        LEFT JOIN examinations e
            ON er.exam_id = e.exam_id

        LEFT JOIN attendance a
            ON er.student_id = a.student_id
            AND er.exam_id = a.exam_id

        WHERE er.status = 'Registered'

        ORDER BY e.exam_date DESC, s.student_id
    """

    df = pd.read_sql(query, connection)

    if not df.empty:

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Download Attendance Report",
            csv,
            "attendance_report.csv",
            "text/csv"
        )

    else:
        st.info("No registered students found.")


# ==================================================
# AUTHENTICATION REPORT
# ==================================================

elif report_type == "Authentication Report":

    st.subheader("🔐 Authentication Report")

    query = """
        SELECT
            al.log_id AS ID,
            al.student_id AS `Student ID`,
            s.name AS `Student Name`,
            e.exam_name AS Examination,
            e.subject AS Subject,
            al.authentication_time AS `Authentication Time`,
            al.result AS Result

        FROM authentication_logs al

        LEFT JOIN students s
            ON al.student_id = s.student_id

        LEFT JOIN examinations e
            ON al.exam_id = e.exam_id

        ORDER BY al.authentication_time DESC
    """

    df = pd.read_sql(query, connection)

    if not df.empty:

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Download Authentication Report",
            csv,
            "authentication_report.csv",
            "text/csv"
        )

    else:
        st.info("No authentication records found.")


# ==================================================
# STUDENT ATTENDANCE SUMMARY
# ==================================================

else:

    st.subheader("👨‍🎓 Student Attendance Summary")

    query = """
        SELECT
            er.student_id AS `Student ID`,
            s.name AS `Student Name`,
            s.department AS Department,

            COUNT(DISTINCT er.exam_id) AS `Total Exams`,

            COUNT(
                DISTINCT CASE
                    WHEN a.attendance_id IS NOT NULL
                         AND a.status = 'Present'
                    THEN er.exam_id
                END
            ) AS Present,

            COUNT(DISTINCT er.exam_id)
            -
            COUNT(
                DISTINCT CASE
                    WHEN a.attendance_id IS NOT NULL
                         AND a.status = 'Present'
                    THEN er.exam_id
                END
            ) AS Absent

        FROM exam_registrations er

        LEFT JOIN students s
            ON er.student_id = s.student_id

        LEFT JOIN attendance a
            ON er.student_id = a.student_id
            AND er.exam_id = a.exam_id

        WHERE er.status = 'Registered'

        GROUP BY
            er.student_id,
            s.name,
            s.department

        ORDER BY er.student_id
    """

    df = pd.read_sql(query, connection)

    if not df.empty:

        # Calculate attendance percentage
        df["Attendance %"] = (
            df["Present"] /
            df["Total Exams"] *
            100
        ).round(2)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Download Student Summary",
            csv,
            "student_attendance_summary.csv",
            "text/csv"
        )

    else:
        st.info("No registered students found.")


connection.close()