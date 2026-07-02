import os
import sys
from unittest.mock import MagicMock
from pathlib import Path
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


# 1. Patch Vertex AI
sys.modules['langchain_community.chat_models.vertexai'] = MagicMock()

# 2. Permettre l'import du chatbot (même dossier utils/)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 3. Imports
from openai import AsyncOpenAI
from ragas import evaluate, EvaluationDataset
from ragas.llms import llm_factory

from chatbot import chat_ragas  

# Limiter à 1 requête en parallèle + tolérer les pauses
from ragas.run_config import RunConfig

run_config = RunConfig(
    max_workers=1,
    max_retries=10,
    max_wait=60,
    timeout=300,
)

from ragas.metrics import Faithfulness, ContextPrecision, AnswerRelevancy, ContextRecall


# 4. Config env
base_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=base_dir / ".env", override=True)

# 5. LLM juge
raw_client = AsyncOpenAI(
    base_url="https://api.mistral.ai/v1",
    api_key=os.getenv("MISTRAL_API_KEY"),
)
llm = llm_factory("mistral-small-latest", client=raw_client, max_tokens=2048)

from langchain_mistralai import MistralAIEmbeddings

embeddings = MistralAIEmbeddings(
    model="mistral-embed",
    api_key=os.getenv("MISTRAL_API_KEY"),
)

# 6. Métriques
metrics = [Faithfulness(llm=llm),
           ContextPrecision(llm=llm),
           ContextRecall(llm=llm),
           AnswerRelevancy(llm=llm, embeddings=embeddings)]


# 7.  jeu de test : questions + réponses attendues 
golden = [
    {
        "user_input": "Quels événements ont lieu à Saint Mards de Fresne en 2026 ?",
        "reference": "Exposition de photographies d'hier à aujourd'hui, et visite libre de l'église",   
    },
    {
        "user_input": "Y a-t-il des concerts dans l'Eure ?",
        "reference": "il y a 17 concerts en 2026"

    },
    {
    "user_input": "Y a-t-il un concert de rock à Tokyo ?",
    "reference": "Aucun événement ne correspond à cette demande.",
},
    {
    "user_input": "A quelle date commencera la formation dispensée par la maison familiale et rurale de routot ?",
    "reference": "Elle commencera le 05 octobre 2026 pour une durée de 6 mois.",
},


]

# 8. On fait répondre  chatbot sur chaque question
eval_data = []
for item in golden:
    sortie = chat_ragas(item["user_input"])   # {"answer":..., "contexts":[...]}
    eval_data.append({
        "user_input": item["user_input"],
        "response": sortie["answer"],            # mapping answer → response
        "retrieved_contexts": sortie["contexts"],# mapping contexts → retrieved_contexts
        "reference": item["reference"],
    })

# 9. Évaluation
dataset = EvaluationDataset.from_list(eval_data)
result = evaluate(dataset=dataset, metrics=metrics, run_config = run_config)

print(result)
result.to_pandas().to_csv("resultats_ragas.csv", index=False)
print("\n✅ Détail sauvegardé dans resultats_ragas.csv")
