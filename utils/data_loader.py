import requests
import pandas as pd
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from pathlib import Path
from dotenv import load_dotenv

def recup_evenements(department : str = "Eure", year: str = "2026") ->dict:

    url = (
        "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/"
        "evenements-publics-openagenda/exports/json/"
    )
    params = {
        "lang": "fr",
        "refine": [
            f"firstdate_begin:{year}",
            f"lastdate_begin:{year}",
            f"lastdate_end:{year}",
            f"location_department:{department}",
        ],
        "timezone": "Europe/Paris",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()

def normalize_data(data: dict) -> pd.DataFrame:
    """Aplatit le JSON en DataFrame pandas"""
    return pd.json_normalize(data)

def select_columns(df: pd.DataFrame) -> pd.DataFrame:

    colonnes = [
        'uid', 'slug', 'canonicalurl', 'title_fr', 'description_fr', 'longdescription_fr',
        'image', 'thumbnail', 'originalimage', 'updatedat', 'daterange_fr',
        'firstdate_begin', 'firstdate_end', 'lastdate_begin', 'lastdate_end',
        'timings', 'location_uid', 'location_name', 'location_address',
        'location_postalcode', 'location_city', 'location_department',
        'location_region', 'location_countrycode', 'location_website',
        'location_links', 'location_tags', 'location_description_fr',
        'location_access_fr', 'status', 'originagenda_title',
        'originagenda_uid', 'registration', 'links',
        'location_coordinates.lon', 'location_coordinates.lat'
    ]
    return df[colonnes]

def nettoyer_df(df):
    # Balises html
    def clean_html(text):
        if pd.isna(text):
            return ''
        return re.sub('<.*?>', '', text).strip()
    
    df['description_fr'] = df['description_fr'].apply(clean_html)
    df['longdescription_fr'] = df['longdescription_fr'].apply(clean_html)
    df['location_description_fr'] = df['location_description_fr'].apply(clean_html)
    df['location_access_fr'] = df['location_access_fr'].apply(clean_html)

    # Lignes sans titre ni description
    df = df.dropna(subset=['title_fr', 'description_fr', 'longdescription_fr'])
    df = df[df['title_fr'].str.strip() != '']
    df = df[df['description_fr'].str.strip() != '']
    df = df[df['longdescription_fr'].str.strip() != '']


    # Espaces
    df['title_fr'] = df['title_fr'].str.strip()
    df['description_fr'] = df['description_fr'].str.strip()
    df['longdescription_fr'] = df['longdescription_fr'].str.strip()
    

    # 4. Réinitialiser l'index
    df = df.reset_index(drop=True)

    return df


def chunking(df):
    all_chunks = []

    splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50
)

    
    for idx, row in df.iterrows():
        chunks = splitter.split_text(row["text"])
                
        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "uid": row["uid"],
                "title_fr": row["title_fr"],
                "description_fr": row["description_fr"], 
                "location_city": row["location_city"],
                "location_address": row["location_address"],
                "daterange_fr": row["daterange_fr"],
            })
    
    return pd.DataFrame(all_chunks)


def prepa_embedding(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["text"] = (
        df["title_fr"].fillna("").astype(str).str.strip()
        + " "
        + df["description_fr"].fillna("").astype(str).str.strip()
    )

    df["text"] = (
        df["text"]
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    return df

def load_events(department: str = "Eure", year: str = "2026") -> pd.DataFrame:
    """Fonction principale : récupère, normalise et sélectionne les colonnes"""
    data = recup_evenements(department, year)
    df = normalize_data(data)
    df = select_columns(df)
    df = nettoyer_df(df)  # ✅ Nettoyer d'abord
    df = prepa_embedding(df)  # ✅ Puis créer la colonne "text"
    
    df = supprimer_doublons_evenements(df)

    df = chunking(df)  # ✅ Enfin chunker

    return df


def supprimer_doublons_evenements(df):
    """Supprime les événements doublons ayant le même titre, ville et date."""

    colonnes = ["title_fr", "location_city", "daterange_fr"]

    # Vérification des colonnes
    colonnes_manquantes = [col for col in colonnes if col not in df.columns]
    if colonnes_manquantes:
        raise ValueError(f"Colonnes manquantes : {colonnes_manquantes}")

    df = df.copy()

    # Normalisation pour éviter les faux différents
    for col in colonnes:
        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.strip()
        )

    avant = len(df)

    df = df.drop_duplicates(
        subset=colonnes,
        keep="first"
    )

    apres = len(df)

    print("Suppression des doublons titre/ville/date")
    print("Lignes avant :", avant)
    print("Lignes après :", apres)
    print("Doublons supprimés :", avant - apres)

    return df
  
def recup_api():
    base_dir = Path(__file__).resolve().parent.parent
    env_path = base_dir / ".env"

    # Chargement forcé du fichier .env
    load_dotenv(dotenv_path=env_path, override=True)


    api_key = os.getenv("MISTRAL_API_KEY")
    return api_key

if __name__ == "__main__":
    df = load_events()
    print(df.columns.tolist())
    print(df.shape)
    print(df[['title_fr', 'description_fr', 'daterange_fr']].head())
# Exemple avec une liste de chunks
    # print("Nombre total de chunks :", len(df))
    # print("\nPremier chunk :")
    # print(df.iloc[0].to_dict()) # Affiche le1er chunk (texte + métadonnées)

