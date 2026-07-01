# utils/api.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from chatbot import chat
from main import index

from utils.auth import (
    Token,
    User,
    authenticate_user,
    create_access_token,
    get_current_user,
)

app = FastAPI(
    title="Chatbot Événements",
    description="**API de recommandation d'événements avec Mistral + Faiss. Important, lancer l'indexation avant d'utiliser le chat.**",
    version="1.0.0"
)

@app.get("/")
def accueil():
    return {"message": "Bienvenue sur l'API du chatbot ! 🎉"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/index")
def lancer_reindexation(
    department: str,
    year: str,
    current_user: User = Depends(get_current_user)
):
    try:
        return index(department, year)
    except Exception:
        raise HTTPException(status_code=422, detail="Erreur de syntaxe")

@app.get("/chat")
def poser_question(question: str, current_user: User = Depends(get_current_user)):
    réponse = chat(question)
    return {
        "question": question,
        "réponse": réponse
    }


