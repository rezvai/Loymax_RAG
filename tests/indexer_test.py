import pytest
import numpy as np
from src.indexing import Embedder

@pytest.fixture(scope="module")
def embedder() -> Embedder:
    """
    Фикстура для инициализации Embedder один раз на модуль.

    Returns:
        Embedder: Экземпляр класса Embedder.
    """
    return Embedder()

def test_embedder_shape(embedder: Embedder) -> None:
    """
    Проверяет, что encode возвращает массив правильной формы для нескольких текстов.

    Args:
        embedder (Embedder): Экземпляр Embedder.
    """
    texts = [
        "Пример первого текста.",
        "Второй текст, тоже по-русски."
    ]
    embeddings = embedder.encode(texts)
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape[0] == len(texts)
    assert embeddings.shape[1] > 0  

def test_embedder_empty_list(embedder: Embedder) -> None:
    """
    Проверяет, что при пустом списке текстов encode возвращает массив формы (0, embedding_dim).

    Args:
        embedder (Embedder): Экземпляр Embedder.
    """
    embeddings = embedder.encode([])
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape[0] == 0

def test_embedder_unicode_support(embedder: Embedder) -> None:
    """
    Проверяет поддержку Unicode: русский, emoji, китайский.

    Args:
        embedder (Embedder): Экземпляр Embedder.
    """
    texts = ["тест на русском", "emoji 😀", "китайский 中文"]
    embeddings = embedder.encode(texts)
    assert embeddings.shape[0] == len(texts)
    assert not np.isnan(embeddings).any()  

def test_embedder_repeatability(embedder: Embedder) -> None:
    """
    Проверяет детерминированность: одинаковый текст должен давать одинаковый эмбеддинг.

    Args:
        embedder (Embedder): Экземпляр Embedder.
    """
    text = ["Один и тот же текст."] * 2
    embeddings = embedder.encode(text)
    np.testing.assert_allclose(embeddings[0], embeddings[1], rtol=1e-5, atol=1e-6)
