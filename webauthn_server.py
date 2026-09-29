from flask import Flask, request, jsonify, session, render_template
import mysql.connector
import base64

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)

from webauthn.helpers import options_to_json
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    ResidentKeyRequirement,
    PublicKeyCredentialDescriptor,
)

app = Flask(__name__)

app.secret_key = "fingerprint_exam_secret_key"

RP_ID = "localhost"
RP_NAME = "Fingerprint Examination System"
ORIGIN = "http://localhost:5001"


# -----------------------------------------
# MySQL connection
# -----------------------------------------

def create_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Amr@2006",
        database="fingerprint_exam"
    )


# -----------------------------------------
# Fingerprint registration page
# -----------------------------------------

@app.route("/")
def home():

    return render_template("webauthn_register.html")


# -----------------------------------------
# Start registration
# -----------------------------------------

@app.route("/register/start", methods=["POST"])
def register_start():

    data = request.get_json()

    student_id = data.get("student_id")

    if not student_id:

        return jsonify({
            "error": "Student ID is required"
        }), 400


    connection = create_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT student_id, name
        FROM students
        WHERE student_id = %s
    """, (student_id,))

    student = cursor.fetchone()

    cursor.close()
    connection.close()


    if not student:

        return jsonify({
            "error": "Student not found"
        }), 404


    options = generate_registration_options(

        rp_id=RP_ID,

        rp_name=RP_NAME,

        user_id=student_id.encode("utf-8"),

        user_name=student_id,

        user_display_name=student["name"],

        authenticator_selection=
            AuthenticatorSelectionCriteria(

                resident_key=
                    ResidentKeyRequirement.PREFERRED,

                user_verification=
                    UserVerificationRequirement.REQUIRED
            )
    )


    session["student_id"] = student_id

    session["registration_challenge"] = (
        base64.urlsafe_b64encode(
            options.challenge
        ).decode("utf-8")
    )


    return options_to_json(options)


# -----------------------------------------
# Finish registration
# -----------------------------------------

@app.route("/register/finish", methods=["POST"])
def register_finish():

    credential = request.get_json()

    student_id = session.get("student_id")

    challenge_b64 = session.get(
        "registration_challenge"
    )


    if not student_id or not challenge_b64:

        return jsonify({
            "error": "Registration session expired"
        }), 400


    challenge = base64.urlsafe_b64decode(
        challenge_b64
    )


    try:

        verification = verify_registration_response(

            credential=credential,

            expected_challenge=challenge,

            expected_origin=ORIGIN,

            expected_rp_id=RP_ID
        )

    except Exception as error:

        return jsonify({
            "verified": False,
            "error": str(error)
        }), 400

    credential_id = base64.urlsafe_b64encode(
        verification.credential_id
    ).decode("utf-8")


    public_key = base64.urlsafe_b64encode(
        verification.credential_public_key
    ).decode("utf-8")


    sign_count = verification.sign_count


    connection = create_connection()

    cursor = connection.cursor()


    cursor.execute("""
        UPDATE students

        SET
            webauthn_credential_id = %s,
            webauthn_public_key = %s,
            webauthn_sign_count = %s

        WHERE student_id = %s

    """, (
        credential_id,
        public_key,
        sign_count,
        student_id
    ))


    connection.commit()

    cursor.close()
    connection.close()


    session.pop("student_id", None)

    session.pop(
        "registration_challenge",
        None
    )


    return jsonify({

        "verified": True,

        "message":
            "Fingerprint registered successfully!"
    })
@app.route("/authenticate")
def authenticate_page():
    return render_template("webauthn_authenticate.html")


@app.route("/authenticate/start", methods=["POST"])
def authenticate_start():

    data = request.get_json()

    student_id = data.get("student_id")

    if not student_id:
        return jsonify({
            "error": "Student ID is required"
        }), 400

    connection = create_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            student_id,
            webauthn_credential_id
        FROM students
        WHERE student_id = %s
    """, (student_id,))

    student = cursor.fetchone()

    cursor.close()
    connection.close()

    if not student:
        return jsonify({
            "error": "Student not found"
        }), 404

    if not student["webauthn_credential_id"]:
        return jsonify({
            "error": "Fingerprint is not registered for this student."
        }), 400

    credential_id = base64.urlsafe_b64decode(
        student["webauthn_credential_id"]
    )

    options = generate_authentication_options(
        rp_id=RP_ID,
        allow_credentials=[
            PublicKeyCredentialDescriptor(
                id=credential_id
            )
        ],
        user_verification=
            UserVerificationRequirement.REQUIRED
    )

    session["authentication_student_id"] = student_id

    session["authentication_challenge"] = (
        base64.urlsafe_b64encode(
            options.challenge
        ).decode("utf-8")
    )

    return options_to_json(options)


@app.route("/authenticate/finish", methods=["POST"])
def authenticate_finish():

    credential = request.get_json()

    student_id = session.get(
        "authentication_student_id"
    )

    challenge_b64 = session.get(
        "authentication_challenge"
    )

    if not student_id or not challenge_b64:

        return jsonify({
            "verified": False,
            "error": "Authentication session expired."
        }), 400

    challenge = base64.urlsafe_b64decode(
        challenge_b64
    )

    connection = create_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            webauthn_credential_id,
            webauthn_public_key,
            webauthn_sign_count
        FROM students
        WHERE student_id = %s
    """, (student_id,))

    student = cursor.fetchone()

    cursor.close()
    connection.close()

    if not student:

        return jsonify({
            "verified": False,
            "error": "Student not found."
        }), 404

    public_key = base64.urlsafe_b64decode(
        student["webauthn_public_key"]
    )

    try:

        verification = verify_authentication_response(

            credential=credential,

            expected_challenge=challenge,

            expected_rp_id=RP_ID,

            expected_origin=ORIGIN,

            credential_public_key=public_key,

            credential_current_sign_count=
                student["webauthn_sign_count"],

            require_user_verification=True
        )

    except Exception as error:

        return jsonify({
            "verified": False,
            "error": str(error)
        }), 400

    if not verification.user_verified:

        return jsonify({
            "verified": False,
            "error": "User verification failed."
        }), 400

    connection = create_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE students
        SET webauthn_sign_count = %s
        WHERE student_id = %s
    """, (
        verification.new_sign_count,
        student_id
    ))

    connection.commit()

    cursor.close()
    connection.close()

    session.pop(
        "authentication_student_id",
        None
    )

    session.pop(
        "authentication_challenge",
        None
    )

    return jsonify({
        "verified": True,
        "student_id": student_id,
        "message":
            "Fingerprint authentication successful!"
    })


# -----------------------------------------
# Start Flask
# -----------------------------------------

if __name__ == "__main__":

    app.run(
        host="localhost",
        port=5001,
        debug=True
    )