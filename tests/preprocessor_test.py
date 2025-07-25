import pytest
from typing import List, Dict
from src.preprocessing import Preprocessor

@pytest.fixture
def sample_docs() -> List[Dict[str, str]]:
    """
    Возвращает тестовый набор документов для проверки пайплайна.
    
    Returns:
        list[dict]: список тестовых документов с полями 'uid' и 'text'.
    """
    return [
        {"uid": 1, "text": "Hello World! <b>HTML</b>   "},
        {"uid": 2, "text": "     "},
        {"uid": 3, "text": "This is a clean text."},
        {"uid": 3, "text": "This is a clean text."},  
        {"uid": 4, "text": "Short"},
        {"uid": 5, "text": "Another document with � broken char."},
    ]

@pytest.fixture
def preprocessor() -> Preprocessor:
    """
    Создаёт экземпляр класса Preprocessor для тестов.
    
    Returns:
        Preprocessor: объект препроцессора с настройками из конфига.
    """
    return Preprocessor()

def test_quality_check_valid(preprocessor: Preprocessor, sample_docs: List[Dict[str, str]]) -> None:
    """
    Проверяет, что метод _quality_check возвращает True для корректных данных.

    Args:
        preprocessor (Preprocessor): экземпляр препроцессора.
        sample_docs (list[dict]): тестовый набор документов.
    """
    assert preprocessor._quality_check(sample_docs) is True

def test_quality_check_invalid_structure(preprocessor: Preprocessor) -> None:
    """
    Проверяет, что метод _quality_check возвращает False при некорректной структуре документов.

    Args:
        preprocessor (Preprocessor): экземпляр препроцессора.
    """
    bad_docs: List[Dict[str, str]] = [{"id": 1, "content": "Bad structure"}]  
    assert preprocessor._quality_check(bad_docs) is False

def test_to_lowercase(preprocessor: Preprocessor, sample_docs: List[Dict[str, str]]) -> None:
    """
    Проверяет, что все буквы в текстах после _to_lowercase переведены в нижний регистр.

    Args:
        preprocessor (Preprocessor): экземпляр препроцессора.
        sample_docs (list[dict]): тестовый набор документов.
    """
    docs: List[Dict[str, str]] = preprocessor._to_lowercase(sample_docs)
    
    for doc in docs:
        letters = [ch for ch in doc["text"] if ch.isalpha()]
        assert all(ch.islower() for ch in letters)

def test_clean_text_removes_html_and_broken(preprocessor: Preprocessor) -> None:
    """
    Проверяет, что _clean_text удаляет HTML-теги и битые символы.

    Args:
        preprocessor (Preprocessor): экземпляр препроцессора.
    """
    docs: List[Dict[str, str]] = [{"uid": 1, "text": "Hello <b>World</b> �"}]
    cleaned: List[Dict[str, str]] = preprocessor._clean_text(docs)
    assert "<b>" not in cleaned[0]["text"]
    assert "�" not in cleaned[0]["text"]

def test_remove_duplicates_by_id(preprocessor: Preprocessor) -> None:
    """
    Проверяет, что _remove_duplicates_by_id удаляет дубликаты документов с одинаковыми UID.

    Args:
        preprocessor (Preprocessor): экземпляр препроцессора.
    """
    docs: List[Dict[str, str]] = [{"uid": 1, "text": "A"}, {"uid": 1, "text": "B"}]
    unique: List[Dict[str, str]] = preprocessor._remove_duplicates_by_id(docs)
    assert len(unique) == 1

def test_remove_duplicates_by_hash(preprocessor: Preprocessor) -> None:
    """
    Проверяет, что _remove_duplicates_by_hash удаляет дубликаты с одинаковым текстом.

    Args:
        preprocessor (Preprocessor): экземпляр препроцессора.
    """
    docs: List[Dict[str, str]] = [
        {"uid": 1, "text": "Same text"},
        {"uid": 2, "text": "Same text"},
    ]
    unique: List[Dict[str, str]] = preprocessor._remove_duplicates_by_hash(docs)
    assert len(unique) == 1

def test_filter_by_length(preprocessor: Preprocessor) -> None:
    """
    Проверяет, что _filter_by_length оставляет только документы с длиной >= min_length.

    Args:
        preprocessor (Preprocessor): экземпляр препроцессора.
    """
    preprocessor.min_length = 10
    docs: List[Dict[str, str]] = [
        {"uid": 1, "text": "short"},
        {"uid": 2, "text": "long enough text"},
    ]
    filtered: List[Dict[str, str]] = preprocessor._filter_by_length(docs)
    assert len(filtered) == 1
    assert filtered[0]["uid"] == 2

def test_full_pipeline(preprocessor: Preprocessor, sample_docs: List[Dict[str, str]]) -> None:
    """
    Проверяет, что полный пайплайн preprocess_pipeline удаляет дубликаты,
    чистит тексты и фильтрует слишком короткие документы.

    Args:
        preprocessor (Preprocessor): экземпляр препроцессора.
        sample_docs (list[dict]): тестовый набор документов.
    """
    result: List[Dict[str, str]] = preprocessor.preprocess_pipeline(sample_docs)
    assert all(len(doc["text"]) >= preprocessor.min_length for doc in result)
    assert all("�" not in doc["text"] for doc in result)
    assert all("<" not in doc["text"] for doc in result)  