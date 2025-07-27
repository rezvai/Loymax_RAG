from src.preprocessing import Preprocessor
from src.indexing import Embedder
from src.vector_db import Chroma_db
from configs.logging_config import setup_logger

class Indexer:
    """
    Класс для пайплайна индексации документов в ChromaDB.
    """
    def __init__(self):
        self.vector_db = Chroma_db()
        self.preprocessor = Preprocessor()
        self.embedder = Embedder()
        self.logger = setup_logger("indexer.log")
        
    def index(self, raw_docs: list[dict]) -> int:
        """
        Индексирует список документов: выделяет текст, uid, сохраняет все остальные поля как метадату.

        Args:
            raw_docs (list[dict]): Список документов c произвольными полями, обязательно 'uid', 'text'.

        Returns:
            int: Количество реально добавленных новых документов (без дублей).
        """
        self.logger.info(f"Начало индексации документов. Количество документов {len(raw_docs)}")
        prep_docs = []
        metadatas = []
        for doc in raw_docs:
            prep_doc = {"uid": doc.get("uid"), "text": doc.get("text", "")}
            prep_docs.append(prep_doc)
            meta = {k: v for k, v in doc.items() if k != "text"}
            metadatas.append(meta)

        processed_docs = self.preprocessor.preprocess_pipeline(prep_docs)
        if not processed_docs:
            self.logger.warning("Нет валидных документов для индексации.")
            return 0

        valid_uids = set(doc["uid"] for doc in processed_docs)
        valid_metadatas = [meta for meta in metadatas if meta["uid"] in valid_uids]
        texts = [doc["text"] for doc in processed_docs]
        
        embeddings = self.embedder.encode(texts)
        ids = [doc["uid"] for doc in processed_docs]

        before_count = len(self.vector_db.get_existing_ids())
        self.vector_db.add_unique_by_hash(ids, texts, embeddings, valid_metadatas)
        after_count = len(self.vector_db.get_existing_ids())
        self.logger.info(f"Конец индексации документов.")
        return after_count - before_count
