# utils/api.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from chatbot import chat
from main import index

app = FastAPI(
    title="Chatbot Événements",
    description="API de recommandation d'événements avec Mistral + Faiss",
    version="1.0.0"
)

@app.get("/")
def accueil():
    return {"message": "Bienvenue sur l'API du chatbot ! 🎉"}

@app.get("/chat")
def poser_question(question: str):
    réponse = chat(question)
    return {
        "question": question,
        "réponse": réponse
    }
@app.post("/index")
def Lancer_réindexation(department: str, year: str):
    # réponse = index(department,year)
    # return {"message": "Lancement de l'indexation pour le département : {department} pour l'année : {year}"}
    try: 
        return index(department, year)
    except Exception:
        raise HTTPException(status_code=422, detail="Erreur de syntaxe")