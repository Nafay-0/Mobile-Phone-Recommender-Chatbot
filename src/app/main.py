from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .Database import crud, models
from .Database.database import engine, SessionLocal
from dotenv import load_dotenv
from .service import chat_response

models.Base.metadata.create_all(bind=engine)  # Create tables

app = FastAPI()

load_dotenv()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
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
