# app.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_qa_module import ask_question  

app = FastAPI()

origins = ["*"]  

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

class QuestionRequest(BaseModel):
    question: str

@app.post("/query")
async def query_rag(request: QuestionRequest):
    response = ask_question(request.question)
    return {"response": response}

@app.get("/healthz")
async def health_check():
    return {"status": "ok"}

