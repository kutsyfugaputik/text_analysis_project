import pytest
import json
from text_analysis_project.src.data_analysis_with_api import app, analyze_text, extract_keywords  # Замените your_module на имя вашего файла с приложением


# ===== ТЕСТЫ ДЛЯ ФУНКЦИЙ =====

def test_extract_keywords():
    """
    Тестирует функцию extract_keywords.
    Проверяет, что ключевые слова извлекаются корректно и возвращаются в нужном формате.
    """
    text = "The quick brown fox jumps over the lazy dog. The fox was quick and smart."
    top_keywords = extract_keywords(text, top_n=3)

    # Проверяем, что функция возвращает ровно 3 ключевых слова
    assert len(top_keywords) == 3

    # Проверяем, что самое частое слово — "fox", которое встречается 2 раза
    assert top_keywords[0] == ("fox", 2)

    # Проверяем, что все возвращенные слова являются строками
    for word, count in top_keywords:
        assert isinstance(word, str)
        assert isinstance(count, int)


def test_analyze_text():
    """
    Тестирует функцию analyze_text.
    Проверяет расчет базовой статистики и извлечение ключевых слов.
    """
    text = "Hello world! This is a test message."
    result = analyze_text(text)

    # Проверяем, что общее количество символов считается правильно
    assert result["num_chars"] == len(text)

    # Проверяем количество слов
    assert result["num_words"] == 7

    # Проверяем, что спам-коэффициент рассчитан корректно
    assert result["spam_ratio"] > 0

    # Проверяем, что ключевые слова извлечены
    assert len(result["keywords"]) > 0


# ===== ТЕСТЫ ДЛЯ API =====

@pytest.fixture
def client():
    """
    Фикстура для создания тестового клиента Flask.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_api_analyze_success(client):
    """
    Тестирует успешный запрос к API.
    Проверяет, что анализ текста возвращает корректный ответ.
    """
    response = client.post(
        "/analyze",
        data=json.dumps({"text": "This is a test text to analyze"}),
        content_type="application/json",
    )

    # Проверяем, что запрос выполнен успешно
    assert response.status_code == 200

    # Проверяем, что структура ответа содержит "analysis"
    data = response.get_json()
    assert "analysis" in data

    # Проверяем, что поле num_words содержит корректное значение
    assert data["analysis"]["num_words"] == 7


def test_api_missing_text_field(client):
    """
    Тестирует случай, когда в запросе отсутствует поле 'text'.
    Проверяет, что сервер возвращает корректную ошибку.
    """
    response = client.post(
        "/analyze",
        data=json.dumps({}),  # Отправляем пустой JSON
        content_type="application/json",
    )

    # Проверяем, что возвращается ошибка 400
    assert response.status_code == 400

    # Проверяем текст ошибки
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Поле 'text' отсутствует в запросе"


def test_api_empty_text(client):
    """
    Тестирует случай, когда переданный текст пуст.
    Проверяет, что сервер корректно обрабатывает такой запрос.
    """
    response = client.post(
        "/analyze",
        data=json.dumps({"text": ""}),
        content_type="application/json",
    )

    # Проверяем, что запрос выполнен успешно
    assert response.status_code == 200

    # Проверяем, что анализ текста возвращает корректные значения
    data = response.get_json()
    analysis = data["analysis"]
    assert analysis["num_words"] == 0  # Слов в тексте нет
    assert analysis["spam_ratio"] == 0  # Спам-коэффициент равен 0


def test_api_invalid_json(client):
    """
    Тестирует случай, когда запрос содержит некорректный JSON.
    Проверяет, что сервер возвращает ошибку 500.
    """
    response = client.post(
        "/analyze",
        data="Некорректные данные",  # Передаем некорректный JSON
        content_type="application/json",
    )

    # Проверяем, что возвращается ошибка 500
    assert response.status_code == 500

    # Проверяем текст ошибки
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Произошла ошибка при обработке текста"
