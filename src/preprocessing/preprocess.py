import hashlib
import re
import html

from configs.config import config

class Preprocessor:
    def __init__(self):
        self.config = config['preprocessing']
        if config['preprocessing']['filter_by_length']['working']:
            self.min_length = config['preprocessing']['filter_by_length']['min_length']
    
    def preprocess_pipeline(self, docs: list[dict]) -> list[dict]:
        """Выполняет последовательную предобработку списка документов:
        нормализацию текста, удаление пустых, фильтрацию по длине и дубликатам.
        
        Args:
            docs (list[dict]): список документов (каждый — словарь с ключами 'uid', 'text' и др.).
        
        Returns:
            list[dict]: очищенный список документов.
        """
        if self.config.get("check_empty_doc", False):
            if self._is_empty_doc(docs):
                return None
        
        if self.config.get("lowercase", False):
            docs = self._to_lowercase(docs)
            
        if self.config.get("clean_text", False):
            docs = self._clean_text(docs)
        
        if self.config["remove_duplicates"].get('by_id', False):
            docs = self._remove_duplicates_by_id(docs)
        if self.config["remove_duplicates"].get('by_hash', False):
            docs = self._remove_duplicates_by_hash(docs)
                
        if self.config['filter_by_length']['working']:
            docs = self._filter_by_length(docs)
            
        return docs
    
    def _to_lowercase(self, docs: list[dict]) -> list[dict]:
        """Приводит тексты всех документов к нижнему регистру.

        Args:
            docs (list[dict]): список документов (каждый документ содержит поле 'text').

        Returns:
            list[dict]: тот же список документов, но с текстами в нижнем регистре.
        """
        for i in range(len(docs)):
            docs[i]['text'] = docs[i]['text'].lower()
        return docs
    
    def _clean_text(self, docs: list[dict]) -> list[dict]:
        """Очищает тексты всех документов от HTML, битых символов, невидимых пробелов,
        табуляций, переводов строк и лишних пробелов (в зависимости от настроек в конфиге).

        Args:
            docs (list[dict]): список документов (каждый документ содержит поле 'text').

        Returns:
            list[dict]: тот же список документов, но с очищенными текстами.
        """
        clean_text_config = self.config['clean_text']
        for i in range(len(docs)):
            if clean_text_config.get('clear_html', False):
                docs[i]['text'] = html.unescape(docs[i]['text'])  # декодируем HTML-сущности (&nbsp; и т.д.)
                docs[i]['text'] = re.sub(r"<.*?>", " ", docs[i]['text'])  # удаляем HTML-теги
            if clean_text_config.get('clear_broken_bits', False):
                docs[i]['text'] = docs[i]['text'].replace("�", "")  # убираем битые символы
            if clean_text_config.get('clear_invisible_spaces', False):
                docs[i]['text'] = docs[i]['text'].replace("\xa0", " ").replace("\u200b", "")  # удаляем невидимые пробелы
            if clean_text_config.get('clear_tabs_and_line_breaks', False):
                docs[i]['text'] = docs[i]['text'].replace("\t", " ").replace("\n", " ")  # убираем табуляцию и переносы строк
            if clean_text_config.get('clear_multiple_spaces', False):
                docs[i]['text'] = re.sub(r"\s+", " ", docs[i]['text']).strip()  # нормализуем пробелы
        return docs
        
    def _is_empty_doc(self, docs: list[dict]) -> bool:
        """Проверяет, содержит ли список документов непустые тексты.
        
        Args:
            doc (list[dict]): список документов (каждый — словарь с полем 'text').
        
        Returns:
            bool: True, если в списке есть хотя бы один непустой текст.
        """
        return True if sum([len(t['text']) for t in docs]) > 0 else False
    
    def _remove_duplicates_by_id(self, doc: list[dict]) -> list[dict]:
        """Удаляет дубликаты документов по полю 'uid'.
        
        Args:
            doc (list[dict]): список документов.
        
        Returns:
            list[dict]: список без дубликатов по 'uid'.
        """
        exists = set()
        result = []
        for i in doc:
            if i['uid'] not in exists:
                exists.add(i['uid'])
                result.append(i)    
        return result
    
    def _remove_duplicates_by_hash(self, doc: list[dict]) -> list[dict]:
        """Удаляет дубликаты документов по хэшу текста ('text').
        
        Args:
            doc (list[dict]): список документов.
        
        Returns:
            list[dict]: список без дубликатов по содержимому текста.
        """
        exists = set()
        result = []
        for i in doc:
            text_hash = hashlib.md5(i['text'].encode('utf_8')).hexdigest()
            if text_hash not in exists:
                exists.add(text_hash)
                result.append(i)
        return result   
    
    def _filter_by_length(self, doc: list[dict]) -> list[dict]:
        """Фильтрует документы, удаляя слишком короткие тексты.
        
        Args:
            doc (list[dict]): список документов.
            min_length (int): минимальная допустимая длина текста (в символах).
        
        Returns:
            list[dict]: список документов с текстами достаточной длины.
        """
        return [i for i in doc if len(i['text']) > self.min_length]
