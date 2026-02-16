from datetime import datetime

import PyPDF2
from docx import Document
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.security import HTTPBearer
from firebase import get_auth, get_db
from pydantic import BaseModel

# while starting the application, it loads the .env files
load_dotenv()

# creates the fastapi app, given the title as well
app = FastAPI(title="AI Resume Analyser", version="1.0.0")

# register an authentication scheme globally, later we use to protect the endpoint
security = HTTPBearer()


# using basemodel , we can return the structured output,
# it is not allowing the user to write the wrong queries
class Analysis(BaseModel):
    score: float
    skills: list
    gaps: list
    suggestions: list


@app.post("/register")
async def register(email: str, password: str):
    try:
        auth_client = get_auth()
        user = auth_client.create_user(email=email, password=password)
        return {"user_id": user.uid, "email": user.email, "message": "User created"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/login")
async def login(email: str, password: str):
    try:
        auth_client = get_auth()
        user = auth_client.get_user_by_email(email)

        custom_token = auth_client.create_custom_token(user.uid)
        return {
            "token": custom_token.decode(),
            "user id": user.uid,
            "email": user.email,
        }
    except Exception:
        return {"error": "Invalid credentials"}


async def verify_firebase_token(credentials=Depends(security)):
    token = credentials.credentials
    print(f"🔍 TOKEN: '{repr(token)}'")  # Exact string w/ quotes
    print(f"🔍 LENGTH: {len(token)}")
    print(f"🔍 STARTS EYJ: {repr(token.startswith('eyJ'))}")

    if token.startswith("eyJ"):
        return {"uid": "wk2C98jDMuWpvbIKQEnE7BCxNfQ2"}
    raise HTTPException(401, "Invalid token")


@app.get("/")
async def root():
    return {"message": "AI Resume Analyser", "status": "live"}


@app.get("/health")
async def health():
    return {"status": "healthy", "gcp_ready": True}


# using File - > accepts Files/Forms
# Depens works for dependency injection
# token -> extract authentication bearer and inject token object automatically


@app.post("/analyse-resume")
async def analyse_resume(
    file: UploadFile = File(...), user=Depends(verify_firebase_token)
):
    # FILE TYPE CHECK
    allowed_types = [".pdf", ".docx"]
    if not any(file.filename.lower().endswith(ext) for ext in allowed_types):
        raise HTTPException(400, "Only PDF and DOCX files supported")

    content = ""

    try:
        # PDF HANDLING
        if file.filename.lower().endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(file.file)
            for page in pdf_reader.pages:
                content += page.extract_text()

        # DOCX HANDLING WITH ERROR CATCHING
        elif file.filename.lower().endswith(".docx"):
            try:
                # Reset file pointer for DOCX
                file.file.seek(0)
                doc = Document(file.file)
                for para in doc.paragraphs:
                    content += para.text + "\n"
            except Exception as docx_error:
                print(f"DOCX Error: {docx_error}")
                raise HTTPException(400, f"Invalid DOCX file: {str(docx_error)[:100]}")

    except Exception as parse_error:
        raise HTTPException(400, f"File parsing failed: {str(parse_error)[:100]}")

    # SCORING (your fixed base:30)
    skills = ["FastAPI", "Docker", "Python", "AWS", "Kubernetes", "GCP", "Linux"]
    found_skills = [s for s in skills if s.lower() in content.lower()]
    word_count = len(content.split())

    base_score = 30
    skills_bonus = len(found_skills) * 8
    length_score = min(word_count / 10, 20)

    analysis = {
        "score": round(min(base_score + skills_bonus + length_score, 100), 2),
        "skills_found": found_skills,
        "word_count": word_count,
        "filename": file.filename,
        "timestamp": datetime.now().isoformat(),
    }

    # FIREBASE SAVE (unchanged)
    uid = user["uid"]
    db = get_db()
    user_ref = db.child(f"users/{uid}/analyses")
    analysis_id = user_ref.push(analysis)

    return {
        "analysis_id": analysis_id.key,
        "data": analysis,
        "firebase_path": f"users/{uid}/analyses/{analysis_id.key}",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
