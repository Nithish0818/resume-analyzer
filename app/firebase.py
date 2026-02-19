import os

import firebase_admin
from firebase_admin import auth, credentials, db

_firebase_app = None


def init_firebase():
    global _firebase_app

    if _firebase_app is None:
        # multi paths for local + docker + render
        paths = [
            "empire-resume-ai-firebase-adminsdk-fbsvc-4a1502b176.json",
            "app/empire-resume-ai-firebase-adminsdk-fbsvc-4a1502b176.json",
            "/app/empire-resume-ai-firebase-adminsdk-fbsvc-4a1502b176.json",
        ]

        cred_path = None
        for path in paths:
            if os.path.exists(path):
                cred_path = path
                print(f"Firebase found: {cred_path}")
                break

        if not cred_path:
            print("🚫 NO SERVICE ACCOUNT FOUND")
            raise FileNotFoundError("Service account missing - check Dockerfile")

        cred = credentials.Certificate(cred_path)
        _firebase_app = firebase_admin.initialize_app(
            cred,
            {
                "databaseURL": "https://empire-resume-ai-default-rtdb.asia-southeast1.firebasedatabase.app/"
            },
        )

        print("Firebase is Live")
        return _firebase_app


def get_db():
    init_firebase()
    return db.reference()


def get_auth():
    init_firebase()
    return auth
