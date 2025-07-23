import yaml

def load_config(config_path: str) -> dict:
    """Загружает конфигурационный файл YAML и возвращает его содержимое как словарь.
    
    Args:
        config_path (str): путь к конфигурационному файлу (YAML).
    
    Returns:
        dict: словарь с настройками, загруженными из YAML.
    """
    with open('r', config_path, encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    return config

config = load_config(r'config.yaml')