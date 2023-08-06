from gdrfile.helpers import AbstractGenerate, Helper


class GenerateRouters(AbstractGenerate, Helper):
    """ Генерация файлов для маршрутизации."""

    def __init__(self, dict_params: dict, path: str, *args, **kwargs) -> None:
        """Инициализируем переменные (параметры для вставки, название файла)."""
        super().__init__()
        self.params = dict_params
        self.sample = 'sample/example_routers.py'
        self.done = 'done/api/routers.py'
        self.path = self.generate_path_to_sample(self.sample, path)

    def start_generate(self):
        """Проверяем существует ли файл.

        Если нет - создаем. Если да - актуализируем.
        """
        # Открываем конечный файл и проверяем пуст он или нет.
        f = open('done/api/routers.py', 'a+', encoding='utf-8')
        f.seek(0)
        initial_file = f.read()
        f.close()
        if initial_file:
            self.actual_router()
        else:
            self.initial_router()

    def actual_router(self):
        """Актуализация данных в файле с routers.

        Если анализируются несколько моделей, то в файл необходимо дозаписывать
        следующие данные:
        1) В from/import дозаписать клас представления.
        2) Добавить в routers ссылку для доступа.
        """
        with open(self.done, 'a+', encoding='utf-8') as f:
            f.seek(0)
            routers_file = f.read()
            # Ищем в файле место, в котором сформированы импорты из
            # представлений, чтобы добавить в эти импорты другие представления
            # если моделей для анализа несколько.
            str_start_find = 'from {path_to_app}.api.views import ('.format(
                path_to_app=self.params.get('{{path_to_app}}'),
            )
            str_end_find = 'class {app_name}APIRootView(APIRootView):'.format(
                app_name=self.params.get('{{AppName}}'),
            )
            start_position = routers_file.find(str_start_find)
            end_position = routers_file.find(str_end_find)
            if start_position > 0:
                from_import = routers_file[start_position:end_position]
                # 1) Берем все то, что до импорта представлений +
                # 2) from_import[:-4] - удаляем ненужные отступы и
                # закрывающуюся скобку в импорте +
                # 3) Дописываем новый класс представления +
                # 4) Вставляем все из прошлого файла с конца импортов
                # представлений до конца файла +
                # 5) Дописываем регистрацию нового роутера.
                new_routers_file = (
                        routers_file[:start_position] +
                        from_import[:-4] +
                        '    {main_class}ViewSet,\n)\n\n\n'.format(
                            main_class=self.params.get('{{MainClass}}'),
                        ) +
                        routers_file[end_position:-1] + '\n' +
                        "router.register('{main_class}s', {main_class_vs}ViewSet, '{main_class}s')\n".format(  # noqa: E501
                            main_class=self.params.get('{{main-class}}'),
                            main_class_vs=self.params.get('{{MainClass}}'),
                        )
                )

        with open(self.done, 'w', encoding='utf-8') as f:
            f.write(new_routers_file)

    def initial_router(self):
        """Первичное добавление информации в routers."""
        initial_file = self.generate_context(
            f'{self.path}/{self.sample}', self.params,
        )
        with open(self.done, 'w', encoding='utf-8') as f:
            f.write(initial_file)
