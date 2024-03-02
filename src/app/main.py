import base64
import os
import time
import requests
import shutil
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Depends, Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from Database import crud, models
from Database.database import engine, SessionLocal
from dotenv import load_dotenv
from service import chat_response
from starlette.templating import Jinja2Templates
from pydantic import BaseModel

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

class TextQuery(BaseModel):
    question: str
    sessionID: str
    response: str




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


def generate_transcript(filepath: str):
    url = "https://api.deepgram.com/v1/listen?nova-2-general"

    file = open(filepath, "rb")
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

def generateSpeech(text):

    # Define the API endpoint
    url = "https://api.deepgram.com/v1/speak?model=aura-arcas-en"

    # Define the headers
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }

    # Define the payload
    payload = {
        "text": text
    }

    # Make the POST request
    response = requests.post(url, headers=headers, json=payload)

    filename = generate_unique_filename('temp_speech','mp3')
    filepath = os.path.join(AUDIO_FOLDER, filename)
    # Check if the request was successful
    if response.status_code == 200:
        # Save the response content to a file
        with open(filepath, "wb") as f:
            f.write(response.content)
        
        print("File saved successfully.")
        return filepath
    else:
        print(f"Error: {response.status_code} - {response.text}")


@app.post("/text-query")
async def query_text(textQuery: TextQuery, db: Session = Depends(get_db)):

    question = textQuery.question
    session_id = textQuery.sessionID
    responseType = textQuery.response

    print(f'Session: {session_id} and Query: {question}')
    if not question:
        raise HTTPException(status_code=400, detail="No data provided")


    answer = await chat_response(question, session_id, db)

    if responseType == 'text':
        return answer
    
    elif responseType == 'audio':
        audio_response = generateSpeech(answer['answer'])
        with open(audio_response, "rb") as file:
            encoded_file = base64.b64encode(file.read()).decode('utf-8')
        return {'audio': encoded_file}

@app.post("/audio-query")
async def query_audio(sessionID: str = Form(...), response: str = Form(...), audio: UploadFile = File(...), db: Session = Depends(get_db)):

    if not audio.filename:
        raise HTTPException(status_code=400, detail="No selected file")

    filename = generate_unique_filename('temp_recording', 'mp3')
    filepath = os.path.join(AUDIO_FOLDER, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    transcript = generate_transcript(filepath)
    answer = await chat_response(transcript, sessionID, db)

    if response == 'text':
        answer['transcript'] = transcript
        return answer
    
    elif response == 'audio':
        audio_response = generateSpeech(answer['answer'])
        with open(audio_response, "rb") as file:
            encoded_file = base64.b64encode(file.read()).decode('utf-8')
        answer['audio'] = encoded_file
        return {'transcript': transcript, 'audio': encoded_file}


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

@app.post("/upload-files/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    """
    Upload Files Function
    """
    return await create_upload_files(files)

