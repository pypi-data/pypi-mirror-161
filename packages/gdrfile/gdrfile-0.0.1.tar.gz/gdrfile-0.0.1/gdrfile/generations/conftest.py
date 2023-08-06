from gdrfile.helpers import AbstractGenerate, Helper


class GenerateConftest(AbstractGenerate, Helper):

    def __init__(self, dict_params: dict, path: str, *args, **kwargs) -> None:
        """Инициализируем переменные (параметры для вставки, название файла)."""
        super().__init__()
        self.params = dict_params
        self.sample_factory = 'sample/conftest/conftest_factory.py'
        self.sample_fixture = 'sample/conftest/conftest_fixture.py'
        self.sample_import = 'sample/conftest/conftest_import.py'
        self.done = 'done/tests/conftest.py'
        self.path_factory = self.generate_path_to_sample(
            self.sample_factory, path,
        )
        self.path_fixture = self.generate_path_to_sample(
            self.sample_fixture, path,
        )
        self.path_import = self.generate_path_to_sample(
            self.sample_import, path,
        )

    def start_generate(self):
        """Проверяем существует ли файл.

        Если нет - создаем. Если да - актуализируем.
        """
        # Открываем конечный файл и проверяем пуст он или нет.
        f = open(self.done, 'a+', encoding='utf-8')
        f.seek(0)
        initial_file = f.read()
        f.close()
        if initial_file:
            self.actual_conftest()
        else:
            self.initial_conftest()

    def formatted_file(self, text_file: str) -> str:
        """Подстановка в шаблон необходимых данных."""
        for key, value in self.params.items():
            # В словаре много ключей, ищем нужные по совпадению.
            if text_file.find(key) > 0:
                text_file = text_file.replace(key, str(value))
        return text_file

    def actual_conftest(self):
        """Актуализация conftest файла для тестов.

        Если анализируются несколько моделей, то в файл необходимо дозаписывать
        следующие данные:
        1) В from/import дозаписать клас модели.
        2) Создать DjangoModelFactory и зарегистрировать ее
        3) Написать фикстуру на формат вывода
        """
        with open(self.done, 'a+', encoding='utf-8') as f:
            f.seek(0)
            conftest_file = f.read()
            # Ищем в файле место, в котором осуществлена
            # регистрация DjangoModelFactory
            start_position = conftest_file.find('register(')
            end_position = conftest_file.find('@pytest.fixture')
            # 1) Вставляем все из файла до регистрации фабрики +
            # 2) Дописываем новую фабрику и ее регистрацию +
            # 3) Дописываем регистрацию фабрик из начального файла+
            # 4) Вставляем все фикстуры из начального файла
            # 5) Дописываем фикстуру на формат вывода для новой фабрики
            if start_position > 0:
                new_conftest_file = (
                    conftest_file[:start_position] +
                    self.conftest_factory()[:-2] +
                    conftest_file[start_position:end_position] +
                    conftest_file[end_position:] + '\n\n' +
                    self.conftest_fixture()
                )

        with open(self.done, 'w', encoding='utf-8') as f:
            f.write(new_conftest_file)

    def initial_conftest(self):
        """Первичное добавление импортов в файл, фабрики и фикстур."""
        with open(self.done, 'w', encoding='utf-8') as f:
            f.write(
                self.conftest_import() +
                self.conftest_factory() +
                self.conftest_fixture(),
            )

    def conftest_factory(self):
        """Возвращает часть conftest файла, отвечающего за фабрики."""
        with open(
            f'{self.path_factory}/{self.sample_factory}', 'r', encoding='utf-8',
        ) as f:
            conftest_factory_file = f.read()
            main_class_underline = self.params.get('{{main_class}}')
            main_class_camel = self.params.get('{{MainClass}}')
            # переменная для формирования тела фабрики
            factory_fields = ''
            fields_for_conftest = self.params.get('fields_for_conftest')

            for key, value in fields_for_conftest.items():
                if value == '__change_me__':
                    factory_field = f'    {key} = factory.SubFactory({value})\n'
                else:
                    factory_field = (
                            f'    {key} = factory.LazyAttribute(' +
                            f'lambda {main_class_underline}: {value})\n'
                    )
                factory_fields += factory_field
            factory_fields += f'\n\nregister({main_class_camel}Factory)\n\n\n'

        return self.formatted_file(conftest_factory_file) + factory_fields

    def conftest_fixture(self):
        """Возвращает часть conftest файла, отвечающего за фикстуры."""
        with open(
            f'{self.path_fixture}/{self.sample_fixture}', 'r', encoding='utf-8',
        ) as f:
            conftest_fixture = f.read()
            # Получаем из словаря название класса.
            main_class_underline = self.params.get('{{main_class}}')
            # формируем первую строку для format: return {'id': main_1.id,
            fixture_fields = (
                    '        return {\n' +
                    "            'id': {main_class}.pk,\n".format(
                        main_class=main_class_underline,
                    )
            )
            # Получаем из словаря поля и тип для faker.
            fields_for_conftest = self.params.get('fields_for_conftest')
            # Формирует каждую строку по виду 'id': main_1.id
            for key, value in fields_for_conftest.items():
                fixture_field = (
                    f"            '{key}': {main_class_underline}.{key},\n"
                )
                fixture_fields += fixture_field

            fixture_fields += (
                    '        }' +
                    '\n    return _{main_class}_format\n'.format(
                        main_class=main_class_underline
                    )
            )

        return self.formatted_file(conftest_fixture) + fixture_fields

    def conftest_import(self):
        """Возвращает часть conftest файла, отвечающего за импорты."""
        with open(
            f'{self.path_import}/{self.sample_import}', 'r', encoding='utf-8',
        ) as f:

            conftest_import = f.read()
        return self.formatted_file(conftest_import)
