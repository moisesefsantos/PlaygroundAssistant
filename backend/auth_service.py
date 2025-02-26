import firebase_admin
from firebase_admin import auth
from firebase_admin import auth, credentials
from google.oauth2 import id_token
from google.auth.transport import requests
from firebase_setup import FIREBASE_CREDENTIALS
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIREBASE_CREDENTIALS = os.path.join(BASE_DIR, "firebase_config.json")

GOOGLE_CLIENT_ID = "393765807798-rorn1ikvlutbdhbq2crh0bfqvhpr2oh2.apps.googleusercontent.com"


if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)
    print("Firebase initialized inside auth_service.py")

def create_user(email, password):
    if not email.endswith("@gmail.com"):
        return {"error": "Only Gmail emails are allowed!"}

    try:
        user = auth.create_user(email=email, password=password)
        return {"success": f" User successfully created! UID: {user.uid}"}
    except Exception as e:
        return {"error": f" Error creating user: {str(e)}"}

def verify_user(email):
    try:
        user = auth.get_user_by_email(email)
        return {"success": f" User found: {user.display_name}, UID: {user.uid}"}
    except Exception:
        return {"error": " User not found."}

def list_users():
    try:
        users = []
        for user in auth.list_users().iterate_all():
            users.append({"uid": user.uid, "email": user.email})
        return {"users": users}
    except Exception as e:
        return {"error": f" Error listing users: {str(e)}"}


def update_user(uid, email=None, password=None, display_name=None):
    try:
        update_data = {}

        if email:
            update_data["email"] = email
        if password:
            update_data["password"] = password
        if display_name:
            update_data["display_name"] = display_name

        if not update_data:
            return {"error": " No data provided to update!"}

        user = auth.update_user(uid, **update_data)
        return {
            "success": f" User {user.uid} updated successfully!",
            "updated_fields": update_data
        }
    except auth.UserNotFoundError:
        return {"error": "User not found!"}
    except Exception as e:
        return {"error": f" Error updating user: {str(e)}"}


def delete_user(uid):
    try:
        auth.delete_user(uid)
        return {"success": f" User with UID {uid} deleted successfully!"}
    except Exception as e:
        return {"error": f" Error deleting user: {str(e)}"}



def google_sign_in(received_id_token):
    try:
        decoded_token = id_token.verify_oauth2_token(
            received_id_token, requests.Request(), GOOGLE_CLIENT_ID
        )

        if decoded_token['aud'] != GOOGLE_CLIENT_ID:
            return {"error": " Token is not for this app"}

        email = decoded_token["email"]

        return {
            "success": "Login successful!",
            "email": email
        }
    except Exception as e:
        return {"error": f" Error verifying token: {str(e)}"}


def generate_custom_token(uid):
    try:
        custom_token = auth.create_custom_token(uid)  
        return {"token": custom_token.decode("utf-8")}
    except Exception as e:
        return {"error": f"Error generating token: {str(e)}"}
