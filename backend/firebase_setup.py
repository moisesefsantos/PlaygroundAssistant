import firebase_admin
from firebase_admin import credentials
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIREBASE_CREDENTIALS = os.path.join(BASE_DIR, "firebase_config.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)
    print(" Firebase initialized successfully!")
else:
    print("Firebase was already initialized.")
