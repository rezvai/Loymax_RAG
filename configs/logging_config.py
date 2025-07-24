from loguru import logger
import sys
import os 
from configs import env

def setup_logger(log_file: str):
    """
    Настраивает логгер Loguru для записи в консоль и файл.
    Логи всегда сохраняются в директорию "logs/" (имя файла задаётся параметром).
    Уровень логирования определяется переменными окружения:
      - если DEBUG=True в .env — уровень всегда DEBUG,
      - иначе берётся LOG_LEVEL (или INFO по умолчанию).

    Args:
        log_file (str): Имя файла лога (без пути). Файл будет создан в "logs/".

    Returns:
        logger: Настроенный экземпляр логгера Loguru.
    """
    debug_mode = env.bool("DEBUG", default=False)
    level = "DEBUG" if debug_mode else "INFO"
    
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    full_path = os.path.join(log_dir, log_file)
    
    logger.remove()
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:DD.MM.YYYY HH:mm:ss}</green> | <cyan>{name}</cyan> | <level>{level}</level> | {message}"
    )
    logger.add(
        full_path,
        rotation="10 MB",
        retention="10 days",
        level=level,
        encoding="utf-8",
        format="{time:DD.MM.YYYY HH:mm:ss} | {name} | {level} | {message}"
    )

    return logger