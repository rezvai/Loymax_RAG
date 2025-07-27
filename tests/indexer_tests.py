import pytest
from src.indexing import Indexer

@pytest.fixture
def indexer() -> Indexer:
    """
    Фикстура для инициализации чистого Indexer перед каждым тестом.
    """
    return Indexer()

def test_index_simple(indexer: Indexer) -> None:
    """
    Проверяет индексацию списка документов с обязательными полями.
    """
    docs = [
        {"uid": "1", "text": "Документ 1, этот текст точно длиннее 20 символов."},
        {"uid": "2", "text": "Документ 2, тоже не короткий, всё хорошо!"},
    ]
    added = indexer.index(docs)
    assert added == 2

def test_index_with_metadatas(indexer: Indexer) -> None:
    """
    Проверяет индексацию документов с кастомными дополнительными метаданными.
    """
    docs = [
        {"uid": "10", "text": "Документ A, метаданные, длинный текст.", "source": "test1"},
        {"uid": "20", "text": "Документ B, тоже длинный, для теста.", "source": "test2"},
    ]
    added = indexer.index(docs)
    assert added == 2

def test_no_duplicates(indexer: Indexer) -> None:
    """
    Проверяет, что повторная индексация не создаёт дубликатов по uid/text.
    """
    docs = [
        {"uid": "X", "text": "Повторяющийся текст для проверки дублей, 123456!"},
        {"uid": "Y", "text": "Повторяющийся текст для проверки дублей, 123456!"},
    ]
    added_1 = indexer.index(docs)
    added_2 = indexer.index(docs)
    assert added_1 == 1 
    assert added_2 == 0  