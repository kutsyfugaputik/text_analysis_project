import unittest  # Импортируем модуль для создания тестов
import os  # Модуль для работы с файловой системой
import shutil  # Для кросс-платформенной работы с удалением директорий
import pandas as pd  # Библиотека для работы с таблицами (DataFrame)
from text_analysis_project.src.data_analysis_static import (  # Импортируем тестируемые функции из вашего модуля
    extract_keywords,
    analyze_texts,
    download_texts,
    filter_texts
)


class TestTextAnalysis(unittest.TestCase):
    """
    Класс, содержащий тесты для проверки функций анализа текста.
    """

    @classmethod
    def setUpClass(cls):
        """
        Метод для подготовки окружения перед выполнением всех тестов.
        Создает необходимые директории и загружает тексты.
        """
        cls.data_path = "data/text"  # Путь к директории с текстами
        cls.results_path = "results"  # Путь к директории с результатами анализа

        # Удаление предыдущих данных (если они есть), чтобы избежать конфликтов
        if os.path.exists(cls.data_path):
            shutil.rmtree(cls.data_path)  # Удаляем старую директорию с текстами
        if os.path.exists(cls.results_path):
            shutil.rmtree(cls.results_path)  # Удаляем старую директорию с результатами

        # Запускаем функцию загрузки текстов
        download_texts()

    def test_extract_keywords(self):
        """
        Тест функции extract_keywords: проверка извлечения ключевых слов из текста.
        """
        test_text = "This is a simple test sentence. This test is only for testing purposes."
        # Ожидаемый результат: слова с частотой встречаемости
        expected_keywords = [('test', 2), ('simple', 1), ('sentence', 1),
                             ('testing', 1)]  # Ожидаем 'testing', а не 'purposes'

        # Вызываем функцию extract_keywords с тестовым текстом
        result = extract_keywords(test_text, top_n=4)

        # Сравниваем результат с ожидаемым
        self.assertEqual(result, expected_keywords, "Функция extract_keywords работает некорректно.")

    def test_download_texts(self):
        """
        Тест функции download_texts: проверка, что тексты загружены корректно.
        """
        # Проверяем, что директория с текстами была создана
        self.assertTrue(os.path.exists(self.data_path), "Директория data/text не создана.")

        # Проверяем, что в директории есть файлы
        files = os.listdir(self.data_path)
        self.assertGreater(len(files), 0, "Тексты из корпуса gutenberg не были загружены.")

    def test_analyze_texts(self):
        """
        Тест функции analyze_texts: проверка создания Excel-файла с результатами анализа.
        """
        analyze_texts()  # Запускаем функцию анализа текстов

        # Путь к файлу с результатами анализа
        results_file = os.path.join(self.results_path, "data_analysis.xlsx")

        # Проверяем, что файл с результатами анализа был создан
        self.assertTrue(os.path.exists(results_file), "Файл результатов анализа не был создан.")

        # Проверяем содержимое файла: загружаем его как DataFrame
        df = pd.read_excel(results_file)
        self.assertGreater(len(df), 0, "Файл результатов анализа пустой.")  # Файл должен содержать записи

        # Проверяем наличие ожидаемых колонок
        self.assertIn('num_chars', df.columns, "Колонка num_chars отсутствует в результате анализа.")

    def test_filter_texts(self):
        """
        Тест функции filter_texts: проверка фильтрации текстов и сохранения результатов.
        """
        filter_texts()  # Запускаем фильтрацию текстов

        # Путь к файлу с отфильтрованными данными
        filtered_file = os.path.join(self.results_path, "filtered_data.xlsx")

        # Проверяем, что файл с отфильтрованными данными был создан
        self.assertTrue(os.path.exists(filtered_file), "Файл с отфильтрованными данными не был создан.")

        # Загружаем отфильтрованные данные как DataFrame
        filtered_df = pd.read_excel(filtered_file)
        self.assertGreater(len(filtered_df), 0, "Фильтрованный файл пустой.")  # Данные должны быть

        # Проверяем, что тексты с аннотацией сохранены в директорию
        processed_path = "data/processed_texts"
        self.assertTrue(os.path.exists(processed_path), "Директория для обработанных текстов не создана.")
        self.assertGreater(len(os.listdir(processed_path)), 0, "Обработанные тексты не были сохранены.")


if __name__ == "__main__":
    """
    Запуск тестов через командную строку.
    """
    unittest.main()
