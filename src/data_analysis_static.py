import os
import nltk
import pandas as pd
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import logging

# Инициализация лемматизатора и загрузка необходимых данных
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Начало загрузки пакетов NLTK...")

nltk.download('punkt')
logging.info("Пакет punkt загружен.")
nltk.download('stopwords')
logging.info("Пакет stopwords загружен.")
nltk.download('wordnet')
logging.info("Пакет wordnet загружен.")

lemmatizer = WordNetLemmatizer()
from nltk.corpus import gutenberg

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def extract_keywords(text, top_n=10):
    """Извлекает топ-N популярных слов из текста, исключая стоп-слова и знаки препинания"""
    # Токенизация текста: делим на слова
    words = word_tokenize(text.lower())  # Приводим к нижнему регистру

    # Убираем знаки препинания и фильтруем стоп-слова
    stop_words = set(stopwords.words("english"))
    words = [word for word in words if word.isalpha() and word not in stop_words]

    # Лемматизация слов
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words]

    # Подсчитываем частоту слов
    word_counts = Counter(lemmatized_words)

    # Получаем топ-N самых популярных слов
    most_common_words = word_counts.most_common(top_n)

    # Возвращаем список популярных слов
    return most_common_words



def download_texts():
    """
    Загружает тексты из корпуса NLTK 'gutenberg' и сохраняет их в директорию 'data/text' с именем файла.
    """
    logging.info("Начало загрузки текстов из корпуса Gutenberg.")
    # Проверяем, существует ли директория для хранения текстов, если нет — создаем
    os.makedirs("data/text", exist_ok=True)

    # Перебираем все файлы в корпусе gutenberg
    for file_id in gutenberg.fileids():
        try:
            logging.info(f"Загрузка текста {file_id}.")
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
    logging.info("Начало анализа текстов.")

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
            logging.info(f"Анализ текста {file}.")
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
    logging.info("Начало фильтрации текстов.")

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
            logging.info(f"Обработка файла {file}.")
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
        logging.info("Запуск процесса загрузки текстов.")
        download_texts()  # Загрузка текстов из NLTK
        logging.info("Запуск анализа текстов.")
        analyze_texts()  # Анализ текстов
        logging.info("Запуск фильтрации текстов.")
        filter_texts()  # Фильтрация текстов
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
