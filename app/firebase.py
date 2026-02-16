import firebase_admin
from firebase_admin import auth, credentials, db

_firebase_app = None


def init_firebase():
    global _firebase_app
    if _firebase_app is None:
        cred = credentials.Certificate(
            "empire-resume-ai-firebase-adminsdk-fbsvc-21a4f63b06.json"
        )
        _firebase_app = firebase_admin.initialize_app(
            cred,
            {
                "databaseURL": "https://empire-resume-ai-default-rtdb.asia-southeast1.firebasedatabase.app/"
            },
        )
    return _firebase_app


def get_db():
    init_firebase()
    return db.reference()


def get_auth():
    init_firebase()
    return auth
