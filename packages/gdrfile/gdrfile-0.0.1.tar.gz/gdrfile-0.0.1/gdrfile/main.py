import argparse

import os
import sys

from dotenv import load_dotenv
from gdrfile import generate_sample as gs
from gdrfile import helpers


preparation = helpers.Preparation()


def main():
    """Устанавливаем параметры генерации файлов.

    Данные передаются через аргументы команды или через .env файл.
    Если переданы данные через аргументы команды и передан путь до .env файла,
    то в приоритете данные, указанные в аргументах команды.

    Для корректной работы необходимы следующие переменные:
    PATH_TO_API - путь до папки с приложением.
    PATH_TO_MODELS - путь до папки models.
    APP_NAME - название приложения.
    """
    parser = argparse.ArgumentParser(
        prog='gdrfile',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Генерация начальных файлов для django приложений.'
    )
    parser.add_argument(
        '-env',
        '--env-path',
        type=str,
        help='Путь до .env файла. Пример: settings/config',
    )
    parser.add_argument(
        '-pm',
        '--path-to-models',
        type=str,
        help='Путь до папки models. Пример: server/apps/name_app/models',
    )
    parser.add_argument(
        '-pa',
        '--path-to-api',
        type=str,
        help='Путь до приложения. Пример: server.apps.name_app. ' +
             'Используется для указания корректных импортов',
    )
    parser.add_argument(
        '-an',
        '--app-name',
        type=str,
        help='Название приложения. Пример: app_name.',
    )
    parser.add_argument(
        '-pmc',
        '--parent-model-class',
        type=str,
        default='',
        help='Названия родительских классов моделей. Пример:  BaseModel, ' +
             'MPTTModel и др. Доступны разделители \';\' и \',\'.'
    )
    parser.add_argument(
        '-mf',
        '--model-fields',
        type=str,
        default='',
        help='Поля в моделях могут быть из сторонних пакетов. Для их ' +
             'корректного анализа необходимо указать информацию о них.' +
             'Необходимо указать тип поля в модели, тип поля в сериализаторе ' +
             'и тип поля в тестах. ' +
             'Пример: PhoneField, CharField(), fake.number(); ' +
             'Для корректной работы необходимо поля разделить \',\', а в ' +
             'конце поставить \';\''
    )
    parser.add_argument(
        '-clear',
        '--clear',
        action='store_true',
        help='Очистка сгенерированных файлов.',
    )
    parser.add_argument(
        '-r',
        '--rules',
        action='store_true',
        help='Флаг для генерации файлов с учетом прав доступа ' +
             '(библиотеки django-rules). По умолчанию False.',
    )

    args = check_args(vars(parser.parse_args()))

    # Если указан путь до .env файла, ищем в нем необходимые переменные.
    # В приоритете данные переданные в аргументах команды.
    if args.get('env_path'):
        env_path = os.path.expanduser(args.get('env_path'))
        load_dotenv(os.path.join(env_path, '.env'))

        if args.get('path_to_models') is None:
            args.update(
                {'path_to_models': os.environ.get('GDRFILE_PATH_TO_MODELS')},
            )
        if args.get('path_to_api') is None:
            args.update(
                {'path_to_api': os.environ.get('GDRFILE_PATH_TO_API')},
            )
        if args.get('app_name') is None:
            args.update(
                {'app_name': os.environ.get('GDRFILE_APP_NAME')},
            )
        if args.get('parent_model_class') is None:
            args.update(
                {
                    'parent_model_class':
                        os.environ.get('GDRFILE_PARENT_MODEL_CLASS'),
                },
            )
        if args.get('model_fields') is None:
            args.update(
                {
                    'model_fields':
                        os.environ.get('GDRFILE_MODEL_FIELDS'),
                },
            )
        args.update({'rules': os.environ.get('GDRFILE_RULES')})

    gdrfile(args)
    return 1


def check_args(args: dict) -> dict:
    """Проверка .env файла или данных, переданных в аргументах команды.

    Проверка на указание необходимого минимума данных для корректной генерации
    файлов.
    """
    if (
            not args.get('clear') and
            not any([args.get('path_to_models'), args.get('env_path')])
    ):
        print(
            'При вызове команды gdrfile необходимо передать путь до .env ' +
            'файла с необходимыми настройками или указать аргументы команды ' +
            '(подробнее gdrfile -h).'
        )
        sys.exit()
    if (
            not args.get('clear') and
            args.get('path_to_models') and
            not all([args.get('path_to_api'), args.get('app_name')])
    ):
        print(
            'Для корректной работы программы необходимо указать путь до ' +
            'приложения и название приложения (подробнее gdrfile -h)'
        )
        sys.exit()
    return args


def gdrfile(args=None, **kwargs):
    """Запуск анализа файлов, содержащих код моделей и генерации файлов. """
    # Если вызвана очистка ранее сгенерированных файлов.
    if args.get('clear'):
        preparation.cleaning_file_directory_done()
        print('Сгенерированные файлы очищены.')
        sys.exit()

    # Формируем путь до папки с моделями
    path_to_models = os.path.join(os.getcwd(), f"{args.get('path_to_models')}")
    # Формируем общие параметры для генерации django файлов.
    general_params = preparation.formation_general_params(
        args.get('path_to_api'), args.get('app_name'),
    )
    # Считываем все файлы из папки models и начинаем их анализ.
    for filename in os.listdir(path_to_models):
        # проверяем только файлы с расширением .py
        if filename.find('.py') < 0:
            continue
        with open(os.path.join(path_to_models, filename), 'r') as f:
            all_params = preparation.start_analysis(
                f.read(),
                general_params,
                args.get('rules'),
                args.get('parent_model_class'),
                args.get('model_fields'),
            )
            # Если удалось получить параметры запускаем генерацию.
            # Если не удалось, ищем дальше в папке файлы с django моделями
            if all_params:
                generate_sample = gs.GenerateSample(
                    all_params, os.path.dirname(__file__)
                )
                if args.get('rules'):
                    generate_sample.start_with_rules()
                generate_sample.start_without_rules()
            continue

    if not os.path.exists(os.path.join(os.getcwd(), 'done')):
        print(
            'Не удалось найти файлы моделей в папке: ' +
            '{0}. '.format(args.get('path_to_models')) +
            'Проверьте корректность переданного пути.'
        )
        sys.exit()
    print(
        'Генерация закончена, поздравляю! Сгенерированные файлы находятся ' +
        'в папке done, в каталоге из которого вызвана команда gdrfile.'
    )


if __name__ == "__main__":
    sys.exit(main())
