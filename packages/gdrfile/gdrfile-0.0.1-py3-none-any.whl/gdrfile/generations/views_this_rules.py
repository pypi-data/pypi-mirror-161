from gdrfile.helpers import AbstractGenerate, Helper


class GenerateViewsThisRules(AbstractGenerate, Helper):
    """Генерация представления с правилами доступа."""

    def __init__(self, dict_params: dict, path: str, *args, **kwargs) -> None:
        """Инициализируем переменные (параметры для вставки, название файла)."""
        super().__init__()
        self.params = dict_params
        self.name_file = dict_params.get('{{main_class}}').lower()
        self.sample = 'sample/example_views_this_rules.py'
        self.done = 'done/api/views/'
        self.path = self.generate_path_to_sample(self.sample, path)

    def start_generate(self):
        """Генерация файла."""
        # Вызываем функцию, где открываем пример файла для представлений и
        # считываем его, в заданные поля вставляем нужную информацию.
        initial_file = self.generate_context(
            f'{self.path}/{self.sample}',
            self.params,
        )

        # Открываем конечный файл для записи. Записываем то, что сформировали.
        with open(
            f'{self.done}{self.name_file}.py', 'w', encoding='utf-8',
        ) as f:
            f.write(initial_file)
