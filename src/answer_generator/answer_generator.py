from src.vector_db import Chroma_db
from src.indexing import Embedder
from configs.logging_config import setup_logger
from configs import config, all_models, env

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

class Generator:
    """
    Класс для генерации ответа на вопрос пользователя с помощью retrieval-augmented pipeline.
    Выполняет поиск релевантных фрагментов из векторной базы и отправляет их вместе с вопросом в LLM.
    """
    def __init__(self):
        """
        Инициализация генератора:
        - Загрузка векторной БД.
        - Настройка эмбеддера.
        - Чтение конфига (top_k, модель LLM и т.д.).
        - Инициализация выбранной LLM.
        """
        self.vector_db = Chroma_db()
        self.embedder = Embedder()
        self.config = config['answer_generator']
        self.top_k = self.config['top_k']
        self.logger = setup_logger("answer_generator.log")
        self.llm_model_name = self.config['llm_model_name']
        
        if self.llm_model_name in all_models['openai_models']:
            self.llm_model = ChatOpenAI(api_key=env.str("OPENAI_API_KEY"))
        elif self.llm_model_name in all_models['anthropic_models']:
            self.llm_model = ChatAnthropic(api_key=env.str("ANTHROPIC_API_KEY"))
        elif self.llm_model_name in all_models['google_models']:
            self.llm_model = ChatGoogleGenerativeAI(api_key=env.str("GOOGLE_API_KEY"))
        else:
            self.logger.warning(f"Модель {self.llm_model_name} не поддерживается")
            self.llm_model = None  
    
    def generate(self, question: str) -> str:
        """
        Генерирует ответ на вопрос пользователя с использованием RAG-подхода.

        Args:
            question (str): Вопрос пользователя на естественном языке.

        Returns:
            str: Сгенерированный ответ LLM. 
                Если модель не инициализирована, возвращается строка "Модель не инициализирована".
        """
        if self.llm_model is None:
            self.logger.error("LLM-модель не инициализирована. Ответ сгенерировать невозможно.")
            return "Модель не инициализирована"
        
        self.logger.debug("Начало генерации ответа.")
        question_emb = self.embedder.encode(question)
        results = self.vector_db.query(question_emb, self.top_k)
        docs = results.get("documents", [[]])[0]
        relevant_chunks = [text for text in docs if isinstance(text, str) and text.strip()]
        
        self.logger.debug(f"Найдено {len(relevant_chunks)} релевантных чанков.")
        context = "\n".join(relevant_chunks)
        
        prompt = self.config['prompt']
        
        full_prompt = (
            f"Контекст:\n{context}\n\n"
            f"Вопрос: {question}\n"
            f"{prompt}"
        )
        
        self.logger.debug(f"Промпт: {full_prompt}")
        
        output = self.llm_model.invoke(full_prompt)
        
        return output.content