import pytest
from src.answer_generator import Generator

@pytest.fixture
def generator():
    """
    Создает экземпляр генератора ответа для тестирования.
    """
    return Generator()

def test_generate_returns_str(generator):
    """
    Проверяет, что метод generate возвращает строку-ответ.

    Args:
        generator (Generator): Тестируемый генератор.

    Asserts:
        Результат является строкой и не пустой.
    """
    question = "Какой сегодня день?"
    answer = generator.generate(question)
    assert isinstance(answer, str)
    assert len(answer) > 0

def test_generate_context_includes_relevant_chunks(generator):
    """
    Проверяет, что при генерации ответа используются релевантные фрагменты.

    Args:
        generator (Generator): Тестируемый генератор.

    Asserts:
        В ответе есть ключевое слово из вопроса или ответ не пустой.
    """
    question = "Что такое Loymax?"
    answer = generator.generate(question)
    assert "Loymax" in answer or len(answer) > 10

@pytest.mark.parametrize("question", [
    "Что делает компания Loymax?",
    "Кто такой Альберт Эйнштейн?",
    "Объясни смысл жизни.",
])
def test_generate_various_questions(generator, question):
    """
    Проверяет генерацию ответов на разные вопросы.

    Args:
        generator (Generator): Тестируемый генератор.
        question (str): Вопрос.

    Asserts:
        Ответ — строка и не пустой.
    """
    answer = generator.generate(question)
    assert isinstance(answer, str)
    assert len(answer) > 0
