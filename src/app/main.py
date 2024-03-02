import os
import time
import requests
import shutil
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from Database import crud, models
from Database.database import engine, SessionLocal
from dotenv import load_dotenv
from service import chat_response
from starlette.templating import Jinja2Templates

models.Base.metadata.create_all(bind=engine)  # Create tables

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

AUDIO_FOLDER = 'Temp_Audio'
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# Serving static files
app.mount("/static", StaticFiles(directory="build/static"), name="static")

# Template rendering
templates = Jinja2Templates(directory="build")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_unique_filename(prefix, extension):
    """Generate a unique filename with a timestamp."""
    timestamp = int(time.time() * 1000)  # Current time in milliseconds
    return f"{prefix}_{timestamp}.{extension}"

def generate_response(question: str):
    time.sleep(2)
    return f"Dummy Response for {question}"

def generate_transcript(filepath: str):

    url = "https://api.deepgram.com/v1/listen?nova-2-general"

    file = open(filepath,"rb")
    payload = file
    headers = {
        "Content-Type": "audio/*",
        "Accept": "application/json",
        "Authorization": f"token {DEEPGRAM_API_KEY}",
    }

    response = requests.post(url, data=payload, headers=headers)

    file.close()
    os.remove(filepath)

    text = response.json()["results"]["channels"][0]['alternatives'][0]["transcript"]

    return text

@app.post("/text-query")
async def query_text(question: str):
    if not question:
        raise HTTPException(status_code=400, detail="No data provided")
    
    answer = generate_response(question)
    return {"answer": answer}

@app.post("/audio-query")
async def query_audio(audio: UploadFile = File(...)):
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No selected file")

    filename = generate_unique_filename('temp_recording', 'mp3')
    filepath = os.path.join(AUDIO_FOLDER, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    answer = generate_transcript(filepath)

    return {"answer": answer}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health-check")
async def Health_Check():
    """
     Health Check Function
    """
    return {'detail': 'Health Check'}


@app.post("/chat")
async def chat(message: str, sessionId: str, db: Session = Depends(get_db)):
    """
    Chat Function
    """
    return await chat_response(message, sessionId, db)
