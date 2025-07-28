import chromadb
from chromadb.config import Settings
from typing import Any

from configs import setup_logger
from src.utils import calculate_text_hash

class Chroma_db:
    """
    Класс-обёртка для работы с ChromaDB: хранение и поиск эмбеддингов документов.
    """
    def __init__(self, persist_dir: str = "vector_db"):
        """
        Инициализирует клиента и коллекцию ChromaDB, настраивает логирование.

        Args:
            persist_dir (str, optional): Папка для хранения ChromaDB. Defaults to "vector_db".
        """
        self.client = chromadb.Client(Settings(persist_directory=persist_dir))
        self.collection = self.client.get_or_create_collection("documents")
        self.logger = setup_logger("chroma_db.log")
        self.logger.info(f"Chroma DB инициализирована, путь: {persist_dir}")
        
    def get_existing_ids(self) -> list[str]:
        """
        Получает все id, уже сохранённые в коллекции.

        Returns:
            list[str]: Список строковых id.
        """
        all_ids = self.collection.get(include=["documents"])["ids"]
        self.logger.debug(f"Текущее количество документов в базе: {len(all_ids)}")
        qnique_all_lids = set(all_ids)
        list_all_ids = list(qnique_all_lids)
        return list_all_ids
        
    def _get_existing_hashes(self) -> set:
        """
        Получает все text_hash, уже сохранённые в коллекции.

        Returns:
            set: Множество строковых md5-хешей текстов.
        """
        hashes = set()
        result = self.collection.get(include=["metadatas"])
        metadatas = result["metadatas"] or []
        for meta in metadatas:
            if meta and "text_hash" in meta:
                hashes.add(meta["text_hash"])
        self.logger.info(f"Количество уникальных text_hash: {len(hashes)}")
        
        return hashes
    
    def add_unique_by_hash(self, ids: list[str], texts: list[str], embeddings: list[str], metadatas: list[dict[str, Any]]) -> None:
        """
        Добавляет только уникальные документы по хешу текста (text_hash).

        Args:
            ids (list[str]): Уникальные идентификаторы документов.
            texts (list[str]): Исходные тексты документов.
            embeddings (list[list[float]]): Эмбеддинги документов.
            metadatas (list[dict[str, Any]]): Метаданные документов (по одному словарю на документ).
        """
        existing_hashes = self._get_existing_hashes()
        new_ids, new_embeddings, new_metadatas = [], [], []
        for i, text in enumerate(texts):
            hashed_text = calculate_text_hash(text)
            if hashed_text not in existing_hashes:
                metadata = dict(metadatas[i]) if metadatas else {}
                metadata["text_hash"] = hashed_text
                new_ids.append(ids[i])
                new_embeddings.append(embeddings[i])
                new_metadatas.append(metadata)
                
        if new_ids:
            self.collection.add(
                ids=new_ids,
                documents=[texts[i] for i in range(len(new_ids))],
                embeddings=new_embeddings,
                metadatas=new_metadatas
            )
            self.logger.info(f"Добавлено {len(new_ids)} новых уникальных документов.")
        else:
            self.logger.info("Новых уникальных документов дял добавления не обнаружено.")
            
            
    def query(self, embedding: list, top_k: int = 5) -> dict:
        """
        Ищет наиболее похожие документы по эмбеддингу.

        Args:
            embedding (List[float]): Вектор эмбеддинга запроса.
            top_k (int, optional): Сколько результатов вернуть. Defaults to 5.

        Returns:
            dict: Результаты поиска (ids, расстояния, метаданные).
        """
        result = self.collection.query(query_embeddings=[embedding], n_results=top_k)
        self.logger.debug(f"Выполнен поиск: top_k={top_k}, найден результатов: {len(result)}")
        return result
        
    def delete_by_id(self, ids: list[int]) -> int: 
        """
        Удаляет документы по их id.

        Args:
            ids (list[str]): Список id для удаления.

        Returns:
            int: Оставшееся число документов в коллекции.
        """
        self.collection.delete(ids=ids)
        remaining = len(self.get_existing_ids())
        self.logger.info(f"Удалено {len(ids)} документов. В коллекции осталось: {remaining}")
        
        return remaining
        
    def clear(self) -> None:
        """
        Полностью очищает коллекцию от всех документов.
        """
        all_ids = self.get_existing_ids()
        if all_ids:
            self.collection.delete(ids=all_ids)
            self.logger.info(f"Коллекция полностью очищена. Было удалено: {len(all_ids)}")
        else:
            self.logger.info("Коллекция уже пуста. Удалять нечего.")
