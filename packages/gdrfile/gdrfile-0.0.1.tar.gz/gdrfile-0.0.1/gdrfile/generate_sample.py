from gdrfile.generations.admin import GenerateAdmin
from gdrfile.generations.conftest import GenerateConftest
from gdrfile.generations.rules import GenerateRules
from gdrfile.generations.serializers import GenerateSerializers
from gdrfile.generations.tests import GenerateTests
from gdrfile.generations.views import GenerateViews
from gdrfile.generations.views_this_rules import GenerateViewsThisRules
from gdrfile.generations.init_serializers import GenerateInitSerializers
from gdrfile.generations.init_views import GenerateInitViews
from gdrfile.generations.routers import GenerateRouters


class GenerateSample(object):
    """Основной класс для генерации всех файлов."""

    def __init__(self, dict_params: dict, path: str, *args, **kwargs) -> None:
        """Получаем словарь параметров для работы генератора файлов."""
        self.dict_params = dict_params
        self.path = path

    def start_with_rules(self):
        """Запуск генерации файлов с учетом прав доступа."""
        self.generate_views_this_rules()
        self.generate_rules()
        self.start()

    def start_without_rules(self):
        """Запуск генерации файлов без прав доступа."""
        self.generate_views()
        self.start()

    def start(self):
        """Основной метод для генерации документов."""
        self.generate_admin()
        self.generate_serializers()
        self.generate_tests()
        self.generate_conftest()
        self.generate_init_views()
        self.generate_init_serializers()
        self.generate_routers()

    def generate_admin(self):
        """Генерация файла для административной панели."""
        admin = GenerateAdmin(self.dict_params, self.path)
        admin.start_generate()

    def generate_views(self):
        """Генерация файлов для представлений."""
        admin = GenerateViews(self.dict_params, self.path)
        admin.start_generate()

    def generate_views_this_rules(self):
        """Генерация файлов для представлений с правами."""
        admin = GenerateViewsThisRules(self.dict_params, self.path)
        admin.start_generate()

    def generate_serializers(self):
        """Генерация файлов для сериализаторов."""
        admin = GenerateSerializers(self.dict_params, self.path)
        admin.start_generate()

    def generate_rules(self):
        """Генерация файлов для прав доступа пакета rules."""
        admin = GenerateRules(self.dict_params, self.path)
        admin.start_generate()

    def generate_tests(self):
        """Генерация файлов для тестов."""
        admin = GenerateTests(self.dict_params, self.path)
        admin.start_generate()

    def generate_conftest(self):
        """Генерация файла для настроек тестов - файла conftest."""
        admin = GenerateConftest(self.dict_params, self.path)
        admin.start_generate()

    def generate_init_views(self):
        """Генерация init файла для представлений."""
        admin = GenerateInitViews(self.dict_params, self.path)
        admin.start_generate()

    def generate_init_serializers(self):
        """Генерация init файла для сериализаторов."""
        admin = GenerateInitSerializers(self.dict_params, self.path)
        admin.start_generate()

    def generate_routers(self):
        """Генерация файла для маршрутизатора."""
        admin = GenerateRouters(self.dict_params, self.path)
        admin.start_generate()
