
import nltk
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import logging
from flask import Flask, request, jsonify

# Скачиваем необходимые ресурсы из NLTK
nltk.download('stopwords')
nltk.download('punkt_tab')
nltk.download('gutenberg')
from nltk.corpus import gutenberg

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Инициализация Flask
app = Flask(__name__)

def extract_keywords(text, top_n=10):
    """Извлекает топ-N популярных слов из текста, исключая стоп-слова и знаки препинания."""
    words = word_tokenize(text.lower())
    words = [word for word in words if word.isalpha()]
    stop_words = set(stopwords.words("english"))
    filtered_words = [word for word in words if word not in stop_words]
    word_counts = Counter(filtered_words)
    return word_counts.most_common(top_n)

def analyze_text(text):
    """Анализирует текст и возвращает статистику."""
    common_words = ["the", "and", "to", "a", "in", "of", "for", "on", "with"]
    words = text.split()
    spam_count = sum(1 for word in words if word.lower() in common_words)
    spam_ratio = spam_count / len(words) * 100 if len(words) > 0 else 0

    return {
        "num_chars": len(text),
        "num_chars_no_spaces": len(text.replace(" ", "")),
        "num_words": len(words),
        "num_lines": text.count("\n"),
        "spam_ratio": round(spam_ratio, 2),
        "keywords": extract_keywords(text, top_n=10),
    }

@app.route("/analyze", methods=["POST"])
def analyze_api():
    """REST API для анализа текста. Принимает текст и возвращает статистику."""
    try:
        data = request.get_json()
        if "text" not in data:
            return jsonify({"error": "Поле 'text' отсутствует в запросе"}), 400

        text = data["text"]
        result = analyze_text(text)
        return jsonify({"analysis": result}), 200

    except Exception as e:
        logging.error(f"Ошибка при обработке запроса: {e}")
        return jsonify({"error": "Произошла ошибка при обработке текста"}), 500

if __name__ == "__main__":
    try:
        app.run(debug=True, host="0.0.0.0", port=5000)
    except Exception as e:
        logging.error(f"Ошибка при запуске приложения: {e}")
