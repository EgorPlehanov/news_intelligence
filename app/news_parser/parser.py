from ..crud import create_news_bulk
from datetime import datetime
import sys

# Импорт функций создания сессии базы данных
from ..database import get_db

from .ria_parsers.parser_scheduler_ria import parse_ria_news
from .ria_parsers.parser_period_ria import parse_ria_news_period_data


def parse_news(start_date=None, end_date=None, selected_sources=None):
    print('Парсинг новостей запущен', datetime.now().strftime('%H:%M:%S'))

    all_news = []
    # Вызываем функции для парсинга новостей с разных ресурсов
    if start_date is None or end_date is None or selected_sources is None:
        all_news.extend(parse_ria_news())
    else:
        for source in selected_sources:
            # Формируем имя функции на основе значения источника
            function_name = f"parse_{source}_news_period_data"
            # Проверяем, существует ли функция с таким именем
            if hasattr(sys.modules[__name__], function_name):
                # Получаем объект функции
                function = getattr(sys.modules[__name__], function_name)
                # Вызываем функцию парсинга с параметрами
                all_news.extend(function(start_date, end_date))

    # Сохраняем все новости в базу данных за один раз, используя CRUD-операцию
    with get_db() as db:
        create_news_bulk(db, all_news)
    print('Новости сохранены в базу данных')
