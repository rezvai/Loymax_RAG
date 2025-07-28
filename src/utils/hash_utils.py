import hashlib

def calculate_text_hash(text: str) -> list:
    """
    Вычисляет MD5-хеш строки текста.

    Args:
        text (str): Исходный текст.

    Returns:
        str: Строка с MD5-хешем текста.
    """
    return hashlib.md5(text.encode("utf-8")).hexdigest()