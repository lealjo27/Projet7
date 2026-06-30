import os
import sys
from unittest.mock import MagicMock
from pathlib import Path
from dotenv import load_dotenv

# 1. Patch de sécurité pour éviter l'erreur d'importation manquante
sys.modules['langchain_community.chat_models.vertexai'] = MagicMock()

# 2. Imports nécessaires
from openai import AsyncOpenAI
from ragas import evaluate, EvaluationDataset
from ragas.llms import llm_factory
# On importe directement depuis le package des métriques pour accéder aux classes
from ragas.metrics import Faithfulness, ContextPrecision

# 3. Configuration de l'environnement
base_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=base_dir / ".env", override=True)

# 4. Client asynchrone (Groq compatible OpenAI)
raw_client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

# 5. Création du wrapper LLM pour Ragas
llm = llm_factory("llama-3.3-70b-versatile", client=raw_client)

# 6. Initialisation des métriques en tant qu'objets instanciés
metrics = [
    Faithfulness(llm=llm),
    ContextPrecision(llm=llm),
]

# 7. Préparation du dataset
data = [
    {
        "user_input": "Quelle est la capitale de la France ?",
        "response": "La capitale est Paris.",
        "retrieved_contexts": ["Paris est la capitale de la France."],
        "reference": "Paris",
    }
]

dataset = EvaluationDataset.from_list(data)

# 8. Évaluation
result = evaluate(dataset=dataset, metrics=metrics)

print(result)
