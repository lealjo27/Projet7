import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
from pydantic import BaseModel, EmailStr

# ─────────────────────────────────────────────
# 1. Chargement des variables d'environnement
# ─────────────────────────────────────────────
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
LOGIN = os.getenv("LOGIN")
MDP = os.getenv("MDP")

# Vérifications au démarrage (fail fast)
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY manquante dans le fichier .env")
if not LOGIN or not MDP:
    raise RuntimeError("Les variables LOGIN et MDP doivent être définies dans .env")

# Schéma OAuth2 : indique que la route pour obtenir le jeton est "/token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ─────────────────────────────────────────────
# 2. Modèles Pydantic
# ─────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str


# ─────────────────────────────────────────────
# 3. Gestion des mots de passe (hashage bcrypt)
# ─────────────────────────────────────────────
def get_password_hash(password: str) -> str:
    """Transforme un mot de passe en clair en un hash Bcrypt sécurisé."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare le mot de passe en clair avec sa version hachée."""
    try:
        pwd_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False


# ─────────────────────────────────────────────
# 4. Fausse base de données
# La clé du dict = le username (indispensable !)
# ─────────────────────────────────────────────
fake_users_db = {
    LOGIN: {
        "username": LOGIN,
        "email": "alice@example.com",
        "hashed_password": get_password_hash(MDP),
        "disabled": False,
    }
}


# ─────────────────────────────────────────────
# 5. Création du jeton JWT
# ─────────────────────────────────────────────
def create_access_token(data: dict) -> str:
    """Génère un jeton JWT signé qui expire après 30 min."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ─────────────────────────────────────────────
# 6. Authentification d'un utilisateur (helper)
# ─────────────────────────────────────────────
def authenticate_user(username: str, password: str):
    """Renvoie l'utilisateur si login + mot de passe sont valides, sinon None."""
    user = fake_users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


# ─────────────────────────────────────────────
# 7. Le "douanier" : vérifie le jeton à chaque requête protégée
# ─────────────────────────────────────────────
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Vérifie le jeton. S'il est valide, renvoie l'utilisateur, sinon bloque."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Jeton invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user_dict = fake_users_db.get(token_data.username)
    if user_dict is None:
        raise credentials_exception

    # On bloque les comptes désactivés
    if user_dict.get("disabled"):
        raise HTTPException(status_code=400, detail="Compte désactivé")

    # On renvoie l'utilisateur SANS son mot de passe
    return User(**user_dict)
