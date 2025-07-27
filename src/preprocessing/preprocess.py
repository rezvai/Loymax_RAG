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
        if self.config.get("quality_check", False):
            docs_quality = self._quality_check(docs)
            if not docs_quality:
                self.logger.warning(f"Документы не прошли проверку - возврщается пустой список.")
                return []

        self.logger.info(f"Начало предобработки: {len(docs)} документов")

        if self.config.get("lowercase", False):
            docs = self._to_lowercase(docs)
            self.logger.info(f"Успешное приведения документов к нижнему регистру: {len(docs)} документов")

        if self.config.get("clean_text", False):
            docs = self._clean_text(docs)
            self.logger.info(f"Успешная очистка: {len(docs)} документов")

        if self.config["remove_duplicates"].get('by_id', False):
            docs = self._remove_duplicates_by_id(docs)
            self.logger.info(f"Успешное удаление дубликатов по ID: {len(docs)} документов")
        if self.config["remove_duplicates"].get('by_hash', False):
            docs = self._remove_duplicates_by_hash(docs)
            self.logger.info(f"Успешное удаление дубликатов по Hash: {len(docs)} документов")

        if self.config['filter_by_length']['working']:
            docs = self._filter_by_length(docs)
            self.logger.info(f"Успешная фильтрация по кол-ву символов {self.min_length}: {len(docs)} документов")

        self.logger.info(f"Предоработка завершена. Итог: {len(docs)} документов")
        return docs
    
    def _quality_check(self, docs: list[dict]) -> bool:
        """
        Проверяет качество данных перед препроцессингом:
        - проверка структуры (uid, text),
        - поиск пустых текстов,
        - подсчёт дублей,
        - подсчёт коротких текстов,
        - подсчёт битых символов.
        
        Логирует статистику. Возвращает False, если данные непригодны для обработки.
        
        Args:
            docs (list[dict]): список документов (каждый должен содержать 'uid' и 'text').

        Returns:
            bool: True — данные пригодны для обработки, False — стоит остановить пайплайн.
        """
        self.logger.info(f"Проверка качества данных: всего {len(docs)} документов")

        # Проверка структуры 
        invalid_docs = [d for d in docs if not isinstance(d, dict) or "uid" not in d or "text" not in d]
        if invalid_docs:
            self.logger.error(f"Документы с неверной структурой: {len(invalid_docs)}")
            return False  

        # Проверка пустых текстов
        empty_docs = [d for d in docs if not d["text"].strip()]
        if empty_docs:
            self.logger.warning(f"Пустые документы: {len(empty_docs)}")

        if len(empty_docs) == len(docs):
            self.logger.error("Все документы пустые — пайплайн остановлен")
            return False

        # Подсчет дублей
        uid_dupes = len(docs) - len({d["uid"] for d in docs})
        text_dupes = len(docs) - len({d["text"] for d in docs})
        self.logger.info(f"Дубликаты: {uid_dupes} по UID, {text_dupes} по тексту")

        # Подсчет коротких текстов
        short_docs = [d for d in docs if len(d["text"]) < self.min_length]
        self.logger.info(f"Короткие тексты (<{self.min_length} символов): {len(short_docs)}")

        # Подсчет битых символов
        broken_count = sum(d["text"].count("�") for d in docs)
        if broken_count:
            self.logger.warning(f"Найдено битых символов: {broken_count}")

        self.logger.info("Проверка качества завершена — данные пригодны для обработки")
        return True


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
