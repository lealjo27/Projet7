import streamlit as st
from chatbot import chat
import httpx
import time

# Titre de l'application
st.title("Mon Chatbot 🤖")


# Initialisation de l'historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """Bonjour ! Je suis un assistant qui recommande des événements 🚴
Je m'appuie uniquement sur les événements de ma base pour répondre.
Comment puis-je t'aider ?"""
        }
    ]


# Affichage des messages précédents
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Zone de saisie utilisateur
if user_input := st.chat_input("Écris ton message ici..."):
    
    # Afficher le message de l'utilisateur
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        response = chat(user_input)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            time.sleep(5)  # attend 5 secondes
            response = "⚠️ Trop de requêtes envoyées, patiente quelques secondes et réessaie !"
        else:
            response = f"⚠️ Erreur API : {str(e)}"

    except Exception as e:
        response = f"⚠️ Une erreur est survenue : {str(e)}"

    # Afficher la réponse
    with st.chat_message("assistant"):
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
