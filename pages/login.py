import streamlit as st
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
st.title("🔑 Student Login")

st.write("Login using your Student ID and password.")


student_id = st.text_input("Student ID")

password = st.text_input(
    "Password",
    type="password"
)


if st.button("Login", type="primary"):

    if not student_id or not password:

        st.warning("Please enter Student ID and password.")

    else:

        connection = create_connection()

        if connection:

            try:

                cursor = connection.cursor(dictionary=True)

                query = """
                SELECT
                    student_id,
                    name,
                    department,
                    year,
                    password_hash
                FROM students
                WHERE student_id = %s
                """

                cursor.execute(query, (student_id,))

                student = cursor.fetchone()

                cursor.close()
                connection.close()

                if student is None:

                    st.error("Student ID not found.")

                else:

                    entered_password_hash = hash_password(password)

                    if entered_password_hash == student["password_hash"]:

                        st.success(
                            f"Welcome, {student['name']}! 🎉"
                        )

                        st.session_state["logged_in"] = True
                        st.session_state["student_id"] = student["student_id"]
                        st.session_state["student_name"] = student["name"]

                        st.info(
                            "Student login successful."
                        )

                    else:

                        st.error("Incorrect password.")

            except mysql.connector.Error as error:

                st.error(
                    f"Login error: {error}"
                )