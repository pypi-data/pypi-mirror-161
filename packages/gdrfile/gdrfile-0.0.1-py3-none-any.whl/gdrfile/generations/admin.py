from gdrfile.helpers import AbstractGenerate, Helper


class GenerateAdmin(AbstractGenerate, Helper):

    def __init__(self, dict_params: dict, path: str, *args, **kwargs) -> None:
        super().__init__()
        self.params = dict_params
        self.sample = 'sample/example_admin.py'
        self.done = 'done/admin.py'
        self.path = self.generate_path_to_sample(self.sample, path)

    def start_generate(self):
        """Генерация файла."""
        # Вызываем функцию, где открываем пример файла для админки и
        # считываем его, в заданные поля вставляем нужную информацию.
        initial_admin_file = self.generate_context(
            f'{self.path}/{self.sample}', self.params,
        )

        # Открываем конечный файл для чтения. Проверяем пустой он или нет.
        # Если пустой, то мы просто запоминаем то, что сформировали выше.
        # Если файл не пустой - формируем документ. Изменяем from/import
        # и дописываем сформированные выше данные в документ.
        with open(self.done, 'a+', encoding='utf-8') as f:
            f.seek(0)
            admin_file = f.read()
            if admin_file:
                # Поиск строки, где импортируется модель
                # и добавляем к ней новую модель
                str_old = admin_file.split('\n')[1]
                str_new = f"{str_old}, {self.params.get('{{MainClass}}')}"
                new_admin_file = admin_file.replace(str_old, str_new)

                # Добавляем в конец документа просто класс, без импортов.
                new_admin_file += self.remove_import(initial_admin_file)
            else:
                new_admin_file = initial_admin_file

        # Открываем конечный файл для записи и вносим в него
        # сформированные данные.
        with open(self.done, 'w', encoding='utf-8') as f:
            f.write(new_admin_file)
