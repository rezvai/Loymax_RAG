import hashlib

def calculate_text_hash(text: str) -> list:
    """
    Вычисляет md5-хеш строки текста.

    Args:
        text (str): Исходный текст.

    Returns:
        str: MD5-хеш текста.
    """
    return hashlib.md5(text.encode("utf-8")).hexdigest()