from langchain_community.vectorstores import FAISS
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
from langchain_mistralai import MistralAIEmbeddings
import os
import shutil
import pandas as pd
import re 

# Configuration commune
INDEX_PATH = "faiss_index"

def get_embeddings(api_key):
    # Essayez "mistral-embed" (attention aux espaces) 
    # ou le modèle le plus récent : "mistral-embed"
    return MistralAIEmbeddings(model="mistral-embed", mistral_api_key=api_key)

def nettoyer_texte(texte):
    """Nettoie le texte pour l'API Mistral."""
    if not isinstance(texte, str):
        return ""
    # Remplacer les retours à la ligne par des espaces
    texte = texte.replace('\n', ' ').replace('\r', ' ')
    # Supprimer les espaces multiples
    texte = re.sub(r'\s+', ' ', texte).strip()
    # Supprimer les caractères de contrôle non désirés
    texte = re.sub(r'[\x00-\x1f\x7f]', '', texte)
    return texte


def construire_index_langchain(df, api_key):
# suppression de l'ancien index au cas ou
    if os.path.exists(INDEX_PATH):
        shutil.rmtree(INDEX_PATH)
        print(f"Ancien index supprimé : {INDEX_PATH}")


    # 1. Préparation des documents
    documents = [
        Document(
            page_content=(
                f"Titre : {str(row.get('title_fr', 'Non précisé'))}\n"
                f"Date : {str(row.get('daterange_fr', 'Non précisée'))}\n"
                f"Ville : {str(row.get('location_city', 'Non précisée'))}\n"
                + nettoyer_texte(row.get("text", ""))
            ),

            metadata={
                "uid": str(row.get("uid", "")),
                "title": str(row.get("title_fr", "")),
                "city": str(row.get("location_city", "")),
                "description": str(row.get("description_fr", "")),
                "date": str(row.get("daterange_fr", ""))
            }
        ) 
        for _, row in df.iterrows() 
        if len(nettoyer_texte(row.get("text", ""))) > 10
    ]

    # 2. Création de l'objet embeddings (constructeur standard)
    embeddings = MistralAIEmbeddings(
        model="mistral-embed", 
        mistral_api_key=api_key
    )

# 3. Récupérer la dimension des embeddings
    print("Calcul d'un embedding de test...")
    test_vector = embeddings.embed_query(documents[0].page_content)

    dimension = len(test_vector)

    print("Dimension des embeddings :", dimension)

    # 4. Création de l'index HNSW
    m = 64
    index = faiss.IndexHNSWFlat(dimension, m)

    # Paramètres HNSW
    index.hnsw.efConstruction = 400
    index.hnsw.efSearch = 256

    print("Index FAISS utilisé : IndexHNSWFlat")
    print("M :", m)
    print("efConstruction :", index.hnsw.efConstruction)
    print("efSearch :", index.hnsw.efSearch)

    # 5. Création du vectorstore LangChain autour de FAISS
    vectorstore = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )

    # 6. Ajout des documents par lots
    taille_lot = 100

    for i in range(0, len(documents), taille_lot):
        lot = documents[i:i + taille_lot]
        print(f"Traitement du lot {i // taille_lot + 1}...")
        vectorstore.add_documents(lot)

    # 7. Sauvegarde
    vectorstore.save_local(INDEX_PATH)

    print(f"Succès : index HNSW sauvegardé dans {INDEX_PATH}")
    print("Nombre total de vecteurs indexés :", vectorstore.index.ntotal)



def verifier_indexation(df):
    """Vérifie que les événements attendus ont bien été indexés dans FAISS."""
    api_key = os.getenv("MISTRAL_API_KEY")

    # Même filtre que pendant l'indexation
    documents_attendus = [
        row for _, row in df.iterrows()
        if len(nettoyer_texte(row.get("text", ""))) > 10
    ]

    nb_evenements_total = len(df)
    nb_documents_attendus = len(documents_attendus)

    embeddings = get_embeddings(api_key)

    vectorstore = FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    nb_documents_faiss = vectorstore.index.ntotal

    print("Événements dans le DataFrame :", nb_evenements_total)
    print("Documents attendus dans FAISS :", nb_documents_attendus)
    print("Documents réellement indexés dans FAISS :", nb_documents_faiss)

    if nb_documents_attendus == nb_documents_faiss:
        print("OK : tous les événements valides ont été indexés.")
    else:
        print("PROBLÈME : le nombre de documents indexés ne correspond pas.")
        print("Différence :", nb_documents_attendus - nb_documents_faiss)

    

def rechercher_langchain(query, api_key, k=3, avec_score=False):
    """Effectue une recherche sémantique dans l'index."""
    query = nettoyer_texte(query)

    if not query:
        return []
    
    embeddings = get_embeddings(api_key)
    
    vectorstore = FAISS.load_local(
        INDEX_PATH, 
        embeddings, 
        allow_dangerous_deserialization=True
    )
    if avec_score:
        return vectorstore.similarity_search_with_score(query, k=k)

    return vectorstore.similarity_search(query, k=k)

