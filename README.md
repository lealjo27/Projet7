---
title: Projet 7 Chatbot Événements
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 8501
python_version: "3.11"
---

# 🤖 Chatbot de Recommandation d'Événements

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.138-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41-red)
![Mistral](https://img.shields.io/badge/Mistral-AI-orange)
![Docker](https://img.shields.io/badge/Docker-✓-blue)
![FAISS](https://img.shields.io/badge/FAISS-vectorstore-purple)

Un chatbot de recommandation d'événements locaux basé sur une architecture **RAG**
(Retrieval-Augmented Generation), construit avec **Mistral AI**, **FAISS**, **LangChain**,
une API **FastAPI** sécurisée par **JWT** et une interface **Streamlit**.

---

## 📋 Table des matières

- [🎯 Aperçu](#-aperçu)
- [✨ Fonctionnalités](#-fonctionnalités)
- [🏗️ Architecture](#️-architecture)
- [📦 Installation locale](#-installation-locale)
- [⚙️ Configuration](#️-configuration)
- [📡 API Endpoints](#-api-endpoints)
- [🧪 Tests](#-tests)
- [🐳 Docker](#-docker)
- [💻 Utilisation](#-utilisation)
- [📊 Évaluation RAGAS](#-évaluation-ragas)
- [🔐 Sécurité](#-sécurité)
- [📚 Structure du projet](#-structure-du-projet)
- [🛠️ Technologies utilisées](#️-technologies-utilisées)
- [👤 Auteur](#-auteur)

---

## 🎯 Aperçu

Ce projet permet à un utilisateur de poser des questions en **langage naturel**
pour obtenir des recommandations d'événements locaux.

Les événements sont récupérés via une API publique, vectorisés avec **Sentence Transformers**,
indexés dans **FAISS**, puis interrogés via le LLM **Mistral AI** pour générer
des réponses contextuelles pertinentes.

### 🎓 Cas d'usage

- 🚴 Trouver une sortie vélo familiale dans un département
- 🎭 Découvrir des événements culturels proches
- 🏃 Rechercher des activités sportives par ville ou date
- 🎉 Explorer les événements d'une région pour une année donnée

---

## ✨ Fonctionnalités

- ✅ Recherche sémantique d'événements en langage naturel
- ✅ Architecture RAG avec FAISS + Mistral AI
- ✅ Indexation dynamique par département et année
- ✅ Authentification sécurisée par JWT
- ✅ API REST documentée automatiquement (Swagger/OpenAPI)
- ✅ Interface conversationnelle avec Streamlit
- ✅ Évaluation de la qualité RAG avec RAGAS
- ✅ Tests unitaires avec pytest
- ✅ Conteneurisation avec Docker

---

## 🏗️ Architecture

```
Livrables/
├── app.py                          # Interface Streamlit (frontend)
├── main.py                         # Pipeline principal (indexation & recherche)
├── Dockerfile                      # Image Docker
├── faiss_index/                    # Index vectoriel FAISS
│   ├── index.faiss
│   └── index.pkl
├── utils/
│   ├── api.py                      # API FastAPI (backend)
│   ├── auth.py                     # Authentification JWT
│   ├── chatbot.py                  # Logique RAG + Mistral
│   ├── data_loader.py              # Chargement des événements
│   ├── embedder.py                 # Génération des embeddings
│   ├── indexer.py                  # Construction de l'index FAISS
│   └── evaluate.py                 # Évaluation RAGAS
├── tests/
│   └── test_api.py                 # Tests unitaires
├── pyproject.toml                  # Dépendances (uv)
└── README.md                       # Documentation
```

### Stack technique

| Composant        | Technologie                         |
|------------------|-------------------------------------|
| LLM              | Mistral AI                          |
| Embeddings       | Sentence Transformers (HuggingFace) |
| Vector Store     | FAISS                               |
| Orchestration    | LangChain                           |
| Backend API      | FastAPI                             |
| Authentification | JWT                                 |
| Frontend         | Streamlit                           |
| Évaluation       | RAGAS                               |
| Conteneurisation | Docker                              |
| Gestion deps     | uv                                  |

---

## 📦 Installation locale

### Prérequis

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) installé
- Une clé API Mistral

### Étapes

```bash
# 1. Cloner le repository
git clone https://github.com/lealjo27/Projet7.git
cd Projet7

# 2. Installer les dépendances avec uv
uv sync

# 3. Configurer les variables d'environnement
cp .env.example .env

# 4. Lancer l'indexation (obligatoire avant le chat)
python main.py
ou depuis l'interface swagger

# 5. Lancer l'interface Streamlit
streamlit run app.py

# 6. Ou lancer l'API FastAPI
uvicorn utils.api:app --reload
# Swagger UI : http://localhost:8000/docs
```

---

## ⚙️ Configuration

Créer un fichier `.env` à la racine du projet :

```env
MISTRAL_API_KEY=
SECRET_KEY=a creer
LOGIN=un login au choix
MDP=un mot de passe au choix
```

---

## 📡 API Endpoints

### 🔓 Racine

```
GET /
```
```json
{
  "message": "Bienvenue sur l'API du chatbot ! 🎉"
}
```

### 🔐 Authentification

```
POST /token
Content-Type: application/x-www-form-urlencoded
```

Corps de requête :
```
username=mdp&password=mdp
```

Réponse :
```json
{
  "access_token": "xxxxxxxxxxsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 📂 Indexation

Endpoint protégé — nécessite un token JWT.

```
POST /index?department=Eure&year=2026
Authorization: Bearer {access_token}
```

Réponse :
```json
{
  "message": "Index construit pour le département Eure, année 2026"
}
```

### 🤖 Chat

Endpoint protégé — nécessite un token JWT.

```
GET /chat?question=sortie vélo familiale
Authorization: Bearer {access_token}
```

Réponse :
```json
{
  "question": "sortie vélo familiale",
  "réponse": "Voici les événements correspondants..."
}
```

---

## 🧪 Tests

```bash
# Lancer tous les tests
pytest tests/ -v

# Avec couverture de code
pytest tests/ --cov=utils
```

---

## 🐳 Docker

```bash
# Construire l'image
docker build -t chatbot-evenements .

# Lancer le conteneur
docker run -p 8501:8501 --env-file .env chatbot-evenements
```

---

## 💻 Utilisation

### Avec Python

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Authentification
response = requests.post(
    f"{BASE_URL}/token",
    data={"username": "login", "password": "mdp"}
)
token = response.json()["access_token"]

# 2. Indexation
headers = {"Authorization": f"Bearer {token}"}
requests.post(f"{BASE_URL}/index?department=Eure&year=2026", headers=headers)

# 3. Poser une question
response = requests.get(
    f"{BASE_URL}/chat?question=sortie vélo familiale",
    headers=headers
)
print(response.json())
```

### Avec cURL

```bash
# 1. Authentification
TOKEN=$(curl -X POST "http://localhost:8000/token" \
  -d "username=login&password=secret123mdp" | jq -r '.access_token')

# 2. Poser une question
curl -X GET "http://localhost:8000/chat?question=sortie+velo" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 Évaluation RAGAS

La qualité du pipeline RAG a été évaluée avec **RAGAS** :
Lancer utils/evaluate.py


---

## 🔐 Sécurité

- ✅ Authentification par JWT
- ✅ Endpoints protégés sur `/index` et `/chat`
- ✅ Variables sensibles dans `.env` (non versionné)
- ✅ Gestion claire des erreurs HTTP
- ✅ Validation des entrées côté API

> ⚠️ **Recommandation** : ne pas conserver d'identifiants par défaut en production.

---

## 📚 Structure du projet

| Fichier                  | Rôle                                      |
|--------------------------|-------------------------------------------|
| `app.py`                 | Interface Streamlit (frontend)            |
| `main.py`                | Pipeline principal indexation/recherche   |
| `utils/api.py`           | Application FastAPI (backend)             |
| `utils/auth.py`          | Gestion de l'authentification JWT         |
| `utils/chatbot.py`       | Logique RAG + Mistral AI                  |
| `utils/data_loader.py`   | Chargement des événements via API         |
| `utils/embedder.py`      | Génération des embeddings                 |
| `utils/indexer.py`       | Construction et interrogation FAISS       |
| `utils/evaluate.py`      | Évaluation RAGAS                          |
| `tests/test_api.py`      | Tests unitaires                           |
| `Dockerfile`             | Image Docker                              |
| `pyproject.toml`         | Dépendances Python (uv)                   |

---

## 🛠️ Technologies utilisées

```
Mistral AI              - LLM pour la génération de réponses
FAISS                   - Index vectoriel pour la recherche sémantique
LangChain               - Orchestration du pipeline RAG
Sentence Transformers   - Génération des embeddings
FastAPI 0.138+          - Framework web API REST
Streamlit 1.41+         - Interface utilisateur conversationnelle
PyJWT                   - Authentification JWT
pytest                  - Framework de tests
Docker                  - Conteneurisation
uv                      - Gestion des dépendances Python
RAGAS                   - Évaluation de la qualité RAG
```

---

## 👤 Auteur

**Jo** — @lealjo27

📧 Email : lealjo27@gmail.com
🐙 GitHub : https://github.com/lealjo27

Version : 1.0.0
Statut : ✅ En développement
Dernière mise à jour : 2026-07-02
```

---
