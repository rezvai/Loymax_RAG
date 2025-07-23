class Preprocessor:
    def __init__(self):
        self.min_length = 0
    
    def preprocess_pipeline(self, filepath: str) -> list[dict]:
        pass
    
    def _to_lowercase(self, text: str) -> str:
        return text.lower()
    
    def _clean_text(self, text: str) -> str:
        pass
    
    def _is_empty_docs(self, doc: list[dict]) -> list[dict]:
        pass
    
    def _remove_duplicates_by_id(self, doc: list[dict]) -> list[dict]:
        pass
    
    def _remove_duplicates_by_hash(self, doc: list[dict]) -> list[dict]:
        pass
    
    def _filter_by_length(self, doc: list[dict], min_length: int = 20) -> list[dict]:
        pass
    
    
