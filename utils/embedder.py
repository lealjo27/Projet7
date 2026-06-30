import numpy as np
import pandas as pd
from mistralai.client import Mistral
import os

from dotenv import load_dotenv
from pathlib import Path

# Modèle d'embeddings Mistral
MODEL_NAME = "mistral-embed"
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

def charger_client(api_key: str = None) -> Mistral:
    """Charge le client Mistral"""
    key = os.getenv("MISTRAL_API_KEY")
    if not key:
        raise ValueError("Clé API Mistral manquante. Définissez MISTRAL_API_KEY.")
    return Mistral(api_key=key)

def generer_embeddings(
    df: pd.DataFrame,
    client: Mistral,
    batch_size: int = 100
) -> np.ndarray:
    """Génère les embeddings à partir de la colonne text du DataFrame, par lots."""

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"df doit être un DataFrame pandas, reçu : {type(df)}"
        )

    if "text" not in df.columns:
        raise ValueError(
            f"La colonne 'text' est absente du DataFrame. "
            f"Colonnes disponibles : {df.columns.tolist()}"
        )

    textes = df["text"].fillna("").astype(str).tolist()

    print(f"Génération des embeddings pour {len(textes)} événements...")
    print(f"Taille des batchs : {batch_size}")

    all_embeddings = []

    for start in range(0, len(textes), batch_size):
        end = min(start + batch_size, len(textes))
        batch = textes[start:end]

        print(
            f"Batch {start // batch_size + 1} : "
            f"événements {start + 1} à {end}"
        )

        response = client.embeddings.create(
            model=MODEL_NAME,
            inputs=batch
        )

        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)

    embeddings = np.array(all_embeddings)

  
    return embeddings

if __name__ == "__main__":
    from data_loader import load_events

    df = load_events()
    # df = df["text"].tolist()
    client = charger_client()
    embeddings = generer_embeddings(df, client)
    print(embeddings.shape)
