import pytest
from src.vector_db.chroma_db import Chroma_db, calculate_text_hash
import chromadb.api.shared_system_client

@pytest.fixture(autouse=True)
def reset_chroma_singleton():
    """
    Сброс синглтона между тестами
    """
    chromadb.api.shared_system_client.SharedSystemClient._identifier_to_system = {}

@pytest.fixture()
def db(tmp_path_factory) -> Chroma_db:
    """
    Создаёт временную тестовую базу Chroma_db для всей сессии тестирования.
    Args:
        tmp_path_factory: Встроенная фикстура pytest для создания временных директорий.
    Returns:
        Chroma_db: Экземпляр тестовой базы.
    """
    tmp_dir = tmp_path_factory.mktemp("chroma_test_db")
    return Chroma_db(persist_dir=str(tmp_dir))

def test_add_and_query(db: Chroma_db) -> None:
    """
    Проверяет добавление новых документов и их последующий поиск по эмбеддингу.

    Args:
        db (Chroma_db): Тестовая база Chroma_db.
    """
    ids = ["1", "2"]
    texts = ["Привет мир", "Ещё один текст"]
    embeddings = [[0.1] * 384, [0.2] * 384]  
    metadatas = [{"source": "test"} for _ in ids]

    db.add_unique_by_hash(ids, texts, embeddings, metadatas)
    assert len(db.get_existing_ids()) == 2

    result = db.query(embeddings[0], top_k=2)
    assert "ids" in result
    assert len(result["ids"][0]) >= 1

def test_duplicate_by_hash(db: Chroma_db) -> None:
    """
    Проверяет, что дубликат по хешу не добавляется второй раз.
    Args:
        db (Chroma_db): Тестовая база Chroma_db.
    """
    ids = ["3"]
    texts = ["Привет мир"]
    embeddings = [[0.3] * 384]
    metadatas = [{"source": "dup"}]

    db.add_unique_by_hash(ids, texts, embeddings, metadatas)
    db.add_unique_by_hash(ids, texts, embeddings, metadatas)

    assert len(db.get_existing_ids()) == 1


def test_delete_and_clear(db: Chroma_db) -> None:
    """
    Проверяет удаление документа по id и полную очистку коллекции.
    Args:
        db (Chroma_db): Тестовая база Chroma_db.
    """
    ids = ["1"]
    texts = ["Тестовый документ"]
    embeddings = [[0.1] * 384]
    metadatas = [{"source": "test"}]
    db.add_unique_by_hash(ids, texts, embeddings, metadatas)

    db.delete_by_id(["1"])
    assert "1" not in db.get_existing_ids()

    db.clear()
    assert len(db.get_existing_ids()) == 0


def test_hash_function() -> None:
    """
    Проверяет корректность работы функции calculate_text_hash.
    """
    h1 = calculate_text_hash("Test123")
    h2 = calculate_text_hash("Test123")
    h3 = calculate_text_hash("Another text")
    assert h1 == h2
    assert h1 != h3
