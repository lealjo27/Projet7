# utils/chatbot.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from indexer import rechercher_langchain
from data_loader import recup_api
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

api_key = recup_api()

llm = ChatMistralAI(
    model="mistral-large-latest",
    api_key=api_key,
    temperature=0,
)

prompt = ChatPromptTemplate.from_template("""
    Tu es un assistant qui recommande des événements 
    Utilise UNIQUEMENT les événements ci-dessous pour répondre, ceux ci ont lieu en 2026
    Si aucun événement ne correspond, dis-le clairement.
    Ne propose rien si rien ne correspond.
    Si une question ne respecte pas les règles morales, explique que tu n'as pas le droit de répondre.

    Evenements disponibles : {context}
    Question : {question}
    Réponse (claire, en français, avec les détails utiles : date, lieu, type) :
""")

chain = prompt | llm | StrOutputParser()

# ── Fonction utilisée par l'API ───────────────────────────────────
def chat(question: str) -> str:
    résultats = rechercher_langchain(question, api_key, k=3)
    context = "\n---\n".join([doc.page_content for doc in résultats])
    return chain.invoke({"context": context, "question": question})

# Special ragas
def chat_ragas(question: str) -> dict:
    résultats = rechercher_langchain(question, api_key, k=3)
    context = "\n---\n".join([doc.page_content for doc in résultats])
    answer = chain.invoke({"context": context, "question": question})
    return {
        "answer": answer,
        "contexts": [doc.page_content for doc in résultats]
    }


# ── Mode terminal ─────────────────────────────────────────────────
if __name__ == "__main__":
    while True:
        question = input("Quel genre d'événement cherches-tu : ")
        if question.lower() == "quitter":
            break
        print("\n" + chat(question) + "\n")
