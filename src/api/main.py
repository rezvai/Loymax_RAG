from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json

from src.indexing import Indexer
from src.answer_generator import Generator

app =FastAPI(
    title="Loymax RAG QA service",
    version="0.0.1"
)
app.mount("/static", StaticFiles(directory="src/api/static"), name="static")

indexer = Indexer()
generator = Generator()

class Document(BaseModel):
    uid: str
    text: str
    
class QueryRequest(BaseModel):
    question: str
    
@app.post("/index_text")
async def index_documents_text(docs: list[Document]):
    """
    Индексирует список документов, переданных в теле запроса (JSON).
    
    Args:
        docs (list[Document]): Список документов, каждый с полями 'uid' и 'text'.
    
    Returns:
        dict: Информация о количестве добавленных документов.
    """
    docs_dict = [doc.model_dump() for doc in docs]
    added = indexer.index(docs_dict)
    return {"added": added, "message": f"Добавлено {len(added)} документов"}

@app.post("/index_file")
async def index_documents_file(file: UploadFile = File(...)):
    """
    Индексирует документы из загруженного JSON-файла.
    
    Args:
        file (UploadFile): JSON-файл со списком документов для индексации.
    
    Raises:
        HTTPException: Если файл не .json, формат неверный или ошибка чтения.
    
    Returns:
        dict: Информация о статусе и количестве добавленных документов.
    """
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Только .json файлы поддерживаются.")
    try:
        content = await file.read()
        docs = json.loads(content)
        if not isinstance(docs, list):
            raise ValueError("В JSON должен быть список документов")
        added = indexer.index(docs)
        return {"status": "ok", "added_docs": added}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка загрузки: {e}")
        

@app.post("/query")
async def generate_answer(query: QueryRequest):
    """
    Генерирует ответ на вопрос пользователя на основе RAG-архитектуры.
    
    Args:
        query (QueryRequest): Объект с вопросом пользователя.
    
    Raises:
        HTTPException: Если не удалось сгенерировать ответ.
    
    Returns:
        dict: Ответ модели (LLM) на заданный вопрос.
    """
    answer = generator.generate(query.question)
    
    if not answer:
        raise HTTPException(status_code=500, detail="Ошибка генерации овтета")
    return {"answer": answer}