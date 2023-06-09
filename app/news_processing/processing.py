from app.database import get_db
from app.crud import get_sources_without_news_by_date_sources, get_clusters_by_sources_and_date
from app.news_parser.parser import parse_news
from .clustering.clustering import clusterize_news
from .summarize.summarize_clusters import summarize_clusters
from .processing_utils import validate_and_save_clusters, convert_clasters_to_dict



def news_processing(selected_date, selected_sources):
    print(selected_sources, selected_date)

    # Получение кластеров по источникам и дате
    with get_db() as db:
        summaries_news_blocks = get_clusters_by_sources_and_date(db, selected_sources, selected_date)

    if len(summaries_news_blocks) == 0:

        # Проверяем наличие новостей для указанных источников и даты в БД
        with get_db() as db:
            sources_without_news = get_sources_without_news_by_date_sources(db, selected_date, selected_sources)

        # Запускаем парсинг если данных нет
        if len(sources_without_news) > 0:
            parse_news(selected_date, selected_date, sources_without_news)

        # Кластеризация новостей
        clusters = clusterize_news(selected_sources, selected_date)

        # Суммаризация кластеров
        summaries_news_blocks = summarize_clusters(clusters)

        # Валидация и сохранение кластеров
        validate_and_save_clusters(summaries_news_blocks, selected_date, selected_sources)

    # Преобразование кластеров в словарь результата
    result = convert_clasters_to_dict(summaries_news_blocks, selected_date)

    return result



