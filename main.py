from utils.data_loader import load_events, recup_api
from utils.indexer import construire_index_langchain
from utils.indexer import rechercher_langchain
from utils.indexer import verifier_indexation
from utils.chatbot import chat

import os
from pathlib import Path
from dotenv import load_dotenv
import re

api_key = recup_api()

def index(department,year):
   
    # indexation
        # 1. Pipeline
        df = load_events(department=department, year=year)

        # 2. Indexation
        construire_index_langchain(df, api_key)

        return {"message": f"Index construit pour le département {department}, année {year}"}


def recherche(query):
# recherche dans index
    resultats = rechercher_langchain(query,
        api_key,
        k=5,
        avec_score=True
    )

    for doc, score in resultats:
        print("Score :", score)
        print("UID :", doc.metadata.get("uid"))
        print("Titre :", doc.metadata.get("title"))
        print("Ville :", doc.metadata.get("city"))
        print("Date :", doc.metadata.get("date"))
        print("Description :", doc.metadata.get("description"))
        print("Texte :", doc.page_content[:300])
        print("-" * 50)



if __name__ == "__main__":

# recherche
    # recherche("sortie vélo familiale")
# indexation
    index("Eure", "2026")
# verification     
    # df = load_events(department="Eure", year="2026")
    # verifier_indexation(df)

# # Chat
#   chat("sortie a velo")

    