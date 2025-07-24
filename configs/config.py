import yaml
import environ
import os


##################################
# Инициализация конфига приложения
##################################
def load_config(config_path: str) -> dict:
    """Загружает конфигурационный файл YAML и возвращает его содержимое как словарь.
    
    Args:
        config_path (str): путь к конфигурационному файлу (YAML).
    
    Returns:
        dict: словарь с настройками, загруженными из YAML.
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    return config

config = load_config(os.path.join(os.path.dirname(__file__), 'config.yaml'))


####################################
# Инициализация переменных окружения
####################################
env = environ.Env(
    DEBUG=(bool, False),
)

environ.Env.read_env(os.path.join(os.path.dirname(__file__), '.env'))