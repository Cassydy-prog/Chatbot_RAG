# app.py

from fastapi import FastAPI
from pydantic import BaseModel
from rag_qa_module import ask_question  

app = FastAPI()

# Schéma des données reçues en POST
class QuestionRequest(BaseModel):
    question: str

# Endpoint POST pour interroger le RAG
@app.post("/query")
async def query_rag(request: QuestionRequest):
    """
    Reçoit une question, l'envoie à la chaîne RAG, 
    et retourne la réponse générée par le LLM.
    """
    response = ask_question(request.question)
    return {"response": response}

@app.get("/healthz")
async def health_check():
    return {"status": "ok"}
