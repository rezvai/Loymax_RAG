import hashlib
import re
import html
from configs import config, setup_logger

class Preprocessor:
    """
    Класс для предобработки текстовых документов:
    нормализация текста, очистка, удаление дубликатов, фильтрация по длине и проверка на пустые документы.
    """

    def __init__(self):
        """
        Инициализация конфигурации и параметров предобработки.
        """
        self.config = config['preprocessing']
        if self.config['filter_by_length']['working']:
            self.min_length = self.config['filter_by_length']['min_length']
        self.logger = setup_logger("preprocessor.log")

    def preprocess_pipeline(self, docs: list[dict]) -> list[dict]:
        """
        Последовательно обрабатывает список документов по шагам из конфигурации:
        приведение к нижнему регистру, очистка текста, удаление дубликатов и фильтрация по длине.

        Args:
            docs (list[dict]): список документов (каждый документ — словарь с ключами 'uid', 'text' и др.).

        Returns:
            list[dict]: список обработанных документов.
        """
        self.logger.info(f"Начало предобработки: {len(docs)} документов")
        
        # Проверка — пуст ли весь датасет
        if self.config.get("check_empty_doc", False) and not self._is_empty_doc(docs):
            self.logger.warning("Все документы пустые - возвращается пустой список")
            return []

        # Приведение к нижнему регистру
        if self.config.get("lowercase", False):
            docs = self._to_lowercase(docs)
            self.logger.info(f"Успешное приведения документов к нижнему регистру: {len(docs)} документов")

        # Очистка текста
        if self.config.get("clean_text", False):
            docs = self._clean_text(docs)
            self.logger.info(f"Успешная очистка: {len(docs)} документов")

        # Удаление дубликатов
        if self.config["remove_duplicates"].get('by_id', False):
            docs = self._remove_duplicates_by_id(docs)
            self.logger.info(f"Успешное удаление дубликатов по ID: {len(docs)} документов")
        if self.config["remove_duplicates"].get('by_hash', False):
            docs = self._remove_duplicates_by_hash(docs)
            self.logger.info(f"Успешное удаление дубликатов по Hash: {len(docs)} документов")

        # Фильтрация по длине
        if self.config['filter_by_length']['working']:
            docs = self._filter_by_length(docs)
            self.logger.info(f"Успешная фильтрация по кол-ву символов {self.min_length}: {len(docs)} документов")

        self.logger.info(f"Предоработка завершена. Итог: {len(docs)} документов")
        return docs

    def _to_lowercase(self, docs: list[dict]) -> list[dict]:
        """
        Приводит текст всех документов в списке к нижнему регистру.

        Args:
            docs (list[dict]): список документов (каждый содержит поле 'text').

        Returns:
            list[dict]: тот же список документов с изменённым текстом.
        """
        for i, doc in enumerate(docs):
            before_len = len(doc['text'])
            doc['text'] = doc['text'].lower()
            self.logger.debug(f"[to_lowercase] Документ {i}: длина {before_len} символов → {len(doc['text'])}")
        return docs 

    def _clean_text(self, docs: list[dict]) -> list[dict]:
        """
        Очищает тексты всех документов от HTML, битых символов, невидимых пробелов,
        табуляций, переводов строк и лишних пробелов (шаги зависят от конфига).

        Args:
            docs (list[dict]): список документов (каждый содержит поле 'text').

        Returns:
            list[dict]: тот же список документов с очищенными текстами.
        """
        clean_text_config = self.config['clean_text']
        for i, doc in enumerate(docs):
            original_len = len(doc['text'])
            if clean_text_config.get('clear_html', False):
                doc['text'] = html.unescape(doc['text'])
                doc['text'] = re.sub(r"<.*?>", " ", doc['text'])
            if clean_text_config.get('clear_broken_bits', False):
                doc['text'] = doc['text'].replace("�", "")
            if clean_text_config.get('clear_invisible_spaces', False):
                doc['text'] = doc['text'].replace("\xa0", " ").replace("\u200b", "")
            if clean_text_config.get('clear_tabs_and_line_breaks', False):
                doc['text'] = doc['text'].replace("\t", " ").replace("\n", " ")
            if clean_text_config.get('clear_multiple_spaces', False):
                doc['text'] = re.sub(r"\s+", " ", doc['text']).strip()
            self.logger.debug(f"[clean_text] Документ {i}: длина {original_len} → {len(doc['text'])}")
        return docs

    def _is_empty_doc(self, docs: list[dict]) -> bool:
        """
        Проверяет, есть ли в списке хотя бы один документ с непустым текстом.

        Args:
            docs (list[dict]): список документов (каждый содержит поле 'text').

        Returns:
            bool: True, если хотя бы один документ содержит непустой текст; False, если все пустые.
        """
        has_text = any(d.get("text") and d["text"].strip() for d in docs)
        self.logger.debug(f"[is_empty_doc] Найдено непустых документов: {'Да' if has_text else 'Нет'}")
        return has_text

    def _remove_duplicates_by_id(self, docs: list[dict]) -> list[dict]:
        """
        Удаляет дубликаты документов на основе поля 'uid'.

        Args:
            docs (list[dict]): список документов.

        Returns:
            list[dict]: список без дубликатов по 'uid'.
        """
        seen = set()
        unique_docs = []
        for doc in docs:
            if doc['uid'] not in seen:
                seen.add(doc['uid'])
                unique_docs.append(doc)
        self.logger.debug(f"[remove_duplicates_by_id] Удалено {len(docs) - len(unique_docs)} дубликатов (по uid)")
        return unique_docs
    def _remove_duplicates_by_hash(self, docs: list[dict]) -> list[dict]:
        """
        Удаляет дубликаты документов на основе хэша их текста ('text').

        Args:
            docs (list[dict]): список документов.

        Returns:
            list[dict]: список без дубликатов по содержимому текста.
        """
        seen = set()
        unique_docs = []
        for doc in docs:
            text_hash = hashlib.md5(doc['text'].encode('utf-8')).hexdigest()
            if text_hash not in seen:
                seen.add(text_hash)
                unique_docs.append(doc)
        self.logger.debug(f"[remove_duplicates_by_hash] Удалено {len(docs) - len(unique_docs)} дубликатов (по тексту)")
        return unique_docs

    def _filter_by_length(self, docs: list[dict]) -> list[dict]:
        """
        Удаляет документы с длиной текста меньше порогового значения.

        Args:
            docs (list[dict]): список документов (каждый содержит поле 'text').

        Returns:
            list[dict]: список документов, где длина текста >= self.min_length.
        """
        filtered = [doc for doc in docs if len(doc['text']) >= self.min_length]
        self.logger.debug(f"[filter_by_length] Удалено {len(docs) - len(filtered)} коротких текстов (<{self.min_length} символов)")
        return filtered
