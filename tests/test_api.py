from fastapi.testclient import TestClient
from utils.api import app
import os
from pathlib import Path
from dotenv import load_dotenv


base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / ".env"

# Chargement forcé du fichier .env
load_dotenv(dotenv_path=env_path, override=True)

USER = os.getenv("LOGIN")
MDP = os.getenv("MDP")

# Le TestClient simule des requêtes HTTP sans lancer un vrai serveur
client = TestClient(app)


def test_accueil():
    # 1. On envoie une requête GET sur "/"
    response = client.get("/")

    # 2. On vérifie le code de statut HTTP (200 = OK)
    assert response.status_code == 200

    # 3. On vérifie le contenu de la réponse JSON
    assert response.json() == {"message": "Bienvenue sur l'API du chatbot ! 🎉"}

def test_login_reussi():
    # On envoie de VRAIS identifiants valides
    response = client.post(
        "/token",
        data={"username": USER, "password": MDP}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_echoue():
    # On envoie de MAUVAIS identifiants
    response = client.post(
        "/token",
        data={"username": "faux", "password": "faux"}
    )
    assert response.status_code == 401
