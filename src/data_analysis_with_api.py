import os
import nltk
import pandas as pd
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import logging

# Скачиваем необходимые ресурсы из NLTK
nltk.download('stopwords')
nltk.download('punkt_tab')
nltk.download('gutenberg')

from nltk.corpus import gutenberg

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_keywords(text, top_n=10):
    """Извлекает топ-N популярных слов из текста, исключая стоп-слова и знаки препинания"""
    # Токенизация текста: делим на слова
    words = word_tokenize(text.lower())  # Приводим к нижнему регистру

    # Убираем знаки препинания
    words = [word for word in words if word.isalpha()]

    # Загружаем список стоп-слов
    stop_words = set(stopwords.words("english"))

    # Отфильтровываем стоп-слова
    filtered_words = [word for word in words if word not in stop_words]

    # Подсчитываем частоту слов
    word_counts = Counter(filtered_words)

    # Получаем топ-N самых популярных слов
    most_common_words = word_counts.most_common(top_n)

    # Возвращаем список популярных слов
    return most_common_words

def download_texts():
    """
    Загружает тексты из корпуса NLTK 'gutenberg' и сохраняет их в директорию 'data/text' с именем файла.
    """
    # Проверяем, существует ли директория для хранения текстов, если нет — создаем
    os.makedirs("data/text", exist_ok=True)

    # Перебираем все файлы в корпусе gutenberg
    for file_id in gutenberg.fileids():
        try:
            # Считываем текст из файла корпуса
            text = gutenberg.raw(file_id)

            # Открываем файл для записи текста в директорию 'data/text'
            with open(f"data/text/{file_id}", "w", encoding="utf-8") as f:
                f.write(text)

            logging.info(f"Текст {file_id} успешно сохранен.")
        except Exception as e:
            logging.error(f"Ошибка при загрузке {file_id}: {e}")

    logging.info("Все тексты успешно сохранены в data/text.")

def analyze_texts():
    """
    Читает все тексты из директории 'data/text', анализирует их и сохраняет результаты в файл 'results/data_analysis.xlsx'.
    Для каждого текста собираются параметры: количество символов, количество символов без пробелов, количество слов и количество строк.
    Также рассчитывается заспамленность и количество ключевых слов.
    """
    def analyze_text(text):
        """
        Функция для анализа текста. Возвращает словарь с параметрами текста.
        """
        common_words = ["the", "and", "to", "a", "in", "of", "for", "on", "with"]
        words = text.split()
        spam_count = sum(1 for word in words if word.lower() in common_words)
        spam_ratio = spam_count / len(words) * 100 if len(words) > 0 else 0

        return {
            "num_chars": len(text),
            "num_chars_no_spaces": len(text.replace(" ", "")),
            "num_words": len(words),
            "num_lines": text.count("\n"),
            "spam_ratio": spam_ratio,
            "num_keywords": sum(1 for word in words if word.lower() in common_words),
        }

    # Список для хранения результатов анализа каждого текста
    data = []
    text_files = os.listdir("data/text")

    # Перебираем все файлы с текстами
    for file in text_files:
        try:
            with open(f"data/text/{file}", "r", encoding="utf-8") as f:
                text = f.read()

            # Анализируем текст
            stats = analyze_text(text)

            # Добавляем имя файла в результаты
            stats["file"] = file

            # Добавляем результат в общий список
            data.append(stats)

            logging.info(f"Текст {file} успешно проанализирован.")
        except Exception as e:
            logging.error(f"Ошибка при анализе {file}: {e}")

    # Преобразуем список данных в DataFrame
    df = pd.DataFrame(data)

    # Сохраняем результаты анализа в Excel файл
    os.makedirs("results", exist_ok=True)
    df.to_excel("results/data_analysis.xlsx", index=False)
    logging.info("Анализ завершён. Результаты сохранены в results/data_analysis.xlsx.")

def filter_texts():
    """Фильтрует тексты на основе анализа и добавляет аннотацию и ключевые слова в отфильтрованные файлы"""
    # Проверка существования Excel файла с результатами анализа
    if not os.path.exists("results/data_analysis.xlsx"):
        logging.error("Файл с результатами анализа не найден!")
        return

    # Чтение данных из Excel
    df = pd.read_excel("results/data_analysis.xlsx")

    # Преобразование столбца 'num_keywords' в числовой формат, если необходимо
    df["num_keywords"] = pd.to_numeric(df["num_keywords"], errors='coerce')

    # Пример фильтрации: Количество символов больше 1000 и количество ключевых слов больше 5
    filtered_df = df[(df["num_chars"] > 1000) & (df["num_keywords"] > 5)]

    # Сохранение отфильтрованных данных в Excel
    filtered_df.to_excel("results/filtered_data.xlsx", index=False)
    logging.info("Фильтрация завершена. Результаты сохранены в results/filtered_data.xlsx.")

    # Сохранение отфильтрованных текстов с аннотацией и ключевыми словами
    os.makedirs("data/processed_texts", exist_ok=True)
    for file in filtered_df["file"]:
        try:
            with open(f"data/text/{file}", "r", encoding="utf-8") as f:
                content = f.read()

            # Аннотация
            annotation = f"--- Аннотация: Файл прошел фильтрацию. Количество символов: {filtered_df[filtered_df['file'] == file]['num_chars'].values[0]}, Количество ключевых слов: {filtered_df[filtered_df['file'] == file]['num_keywords'].values[0]} ---\n"

            # Извлечение популярных слов
            keywords = extract_keywords(content, top_n=10)
            keywords_text = "Популярные слова: " + ", ".join([word[0] for word in keywords])

            # Добавляем аннотацию и ключевые слова к содержимому текста
            content_with_annotation = annotation + keywords_text + "\n\n" + content

            # Записываем текст с аннотацией и ключевыми словами в новый файл
            with open(f"data/processed_texts/{file}", "w", encoding="utf-8") as f:
                f.write(content_with_annotation)

            logging.info(f"Текст {file} успешно отфильтрован и сохранен.")
        except Exception as e:
            logging.error(f"Ошибка при обработке {file}: {e}")

if __name__ == "__main__":
    # Запуск всех функций по очереди
    try:
        download_texts()  # Загрузка текстов из NLTK
        analyze_texts()  # Анализ текстов
        filter_texts()  # Фильтрация текстов
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")