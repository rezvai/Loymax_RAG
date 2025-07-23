import hashlib
import re
import html

class Preprocessor:
    def __init__(self):
        self.min_length = 0
    
    def preprocess_pipeline(self, filepath: str) -> list[dict]:
        pass
    
    def _to_lowercase(self, text: str) -> str:
        return text.lower()
    
    def _clean_text(self, text: str) -> str:
        # unescape &nbsp; to " " and etc.
        text = html.unescape(text)
        # replace html tags
        text = re.sub(r"<.*?>", " ", text)  
        # delete broken bits
        text = text.replace("�", "")
        # delete specially space and delete invisible space
        text = text.replace("\xa0", " ").replace("\u200b", "")
        # delete tabulations
        text = text.replace("\t", " ").replace("\n", " ")
        # delete multiple spaces
        text = re.sub(r"\s+", " ", text).strip()
        return text
        
    def _is_empty_doc(self, doc: list[dict]) -> bool:
        return True if sum([len(t['text']) for t in doc]) > 0 else False
    
    def _remove_duplicates_by_id(self, doc: list[dict]) -> list[dict]:
        exists = set()
        result = []
        for i in doc:
            if i['uid'] not in exists:
                exists.add(i['uid'])
                result.append(i)    

        return result
    
    def _remove_duplicates_by_hash(self, doc: list[dict]) -> list[dict]:
        exists = set()
        result = []
        for i in doc:
            text_hash = hashlib.md5(i['text'].encode('utf_8')).hexdigest()
            if text_hash not in exists:
                exists.add(text_hash)
                result.append(i)

        return result   
    
    def _filter_by_length(self, doc: list[dict]) -> list[dict]:
        return [i for i in doc if len(i['text']) > self.min_length]
    
    
