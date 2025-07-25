from sentence_transformers import SentenceTransformer
import numpy as np
from configs import config

class Embedder:
    """
    Класс для генерации эмбеддингов текстов с помощью SentenceTransformer.

    Позволяет преобразовывать список строк в эмбеддинги для дальнейшего использования
    в retrieval/search задачах.
    """

    def __init__(self):
        """
        Инициализация эмбеддера и загрузка выбранной модели.
        """
        self.config = config['embedder']
        self.model = SentenceTransformer(self.config['model_name'])

    def encode(self, texts: list[str]) -> np.ndarray:
        """
        Преобразует список текстов в массив эмбеддингов.

        Args:
            texts (List[str]): Список строк (предложений или документов) для эмбеддинга.

        Returns:
            np.ndarray: Массив эмбеддингов формы (n_texts, embedding_dim).
        """
        return self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True  
        )
