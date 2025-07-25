FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY rag_qa_module.py .
COPY vectorstore_ecole/ ./vectorstore_ecole/

CMD ["python", "rag_qa_module.py"]
