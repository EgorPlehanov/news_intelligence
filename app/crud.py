from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from . import models, schemas
from typing import List
from more_itertools import unique_everseen
from datetime import date, timedelta
from collections import defaultdict



def create_news(db: Session, news: schemas.NewsCreate):
    """
    Создает одну запись новости в базе данных.

    Args:
        db (Session): Активная SQLAlchemy-сессия.
        news (schemas.NewsCreate): Данные новости для сохранения.

    Returns:
        models.News: Сохраненная ORM-модель новости.
    """
    db_news = models.News(**news.dict())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news



def check_existing_news(db: Session, news: schemas.NewsCreate) -> bool:
    """
    Проверяет, есть ли в базе новость с такими же ключевыми полями.

    Args:
        db (Session): Активная SQLAlchemy-сессия.
        news (schemas.NewsCreate): Новость, которую нужно проверить на дублирование.

    Returns:
        bool: True, если совпадающая новость уже существует, иначе False.
    """
    # Новость считается дублем только при совпадении даты, заголовка, источника и ссылки.
    existing_news = db.query(models.News).filter(
        models.News.date == news.date,
        models.News.title == news.title,
        models.News.source_id == news.source_id,
        models.News.link == news.link
    ).first()
    return existing_news is not None



def create_news_bulk(db: Session, news_list: List[schemas.NewsCreate]):
    """
    Сохраняет список новостей, предварительно исключая дубли.

    Args:
        db (Session): Активная SQLAlchemy-сессия.
        news_list (List[schemas.NewsCreate]): Список новостей, полученных парсером.

    Returns:
        None: Функция сохраняет данные в БД и не возвращает значение.
    """
    unique_news = []
    # unique_everseen удаляет одинаковые объекты NewsCreate с учетом __hash__ и __eq__ из схемы.
    news_list = list(unique_everseen(news_list)) # Убираем дубли

    for news in news_list:
        if not check_existing_news(db, news):
            unique_news.append(models.News(**news.dict()))
        # Печать для проверки
        print(check_existing_news(db, news), news.date, news.title, news.source_id)

    db.bulk_save_objects(unique_news)
    db.commit()



def get_news(db: Session, news_id: int):
    """
    Возвращает одну новость по внутреннему идентификатору записи.

    Args:
        db (Session): Активная SQLAlchemy-сессия.
        news_id (int): Идентификатор записи новости в таблице.

    Returns:
        models.News | None: Найденная новость или None, если записи нет.
    """
    return db.query(models.News).filter(models.News.id == news_id).first()



def get_all_news(db: Session, skip: int = 0, limit: int = 100):
    """
    Возвращает список новостей с пагинацией.

    Args:
        db (Session): Активная SQLAlchemy-сессия.
        skip (int): Количество записей, которые нужно пропустить.
        limit (int): Максимальное количество записей в результате.

    Returns:
        list[models.News]: Список ORM-моделей новостей.
    """
    return db.query(models.News).offset(skip).limit(limit).all()



def get_news_by_date_sources(db: Session, date: date, sources: List[str]):
    """
    Получает новости за выбранный день и из выбранных источников.

    Args:
        db (Session): Активная SQLAlchemy-сессия.
        date (date): Дата, за которую нужно получить новости.
        sources (List[str]): Список описаний источников новостей.

    Returns:
        list[models.News]: Новости, удовлетворяющие фильтрам даты и источников.
    """
    # Получение начальной и конечной даты для выбранного дня
    start_date = date
    end_date = date + timedelta(days=1)
    # Диапазон строится как [start_date, end_date), чтобы захватить весь день без новостей следующей даты.
    news_items = db.query(models.News).join(models.Source).filter(
        models.News.date >= start_date,
        models.News.date < end_date,
        models.Source.description.in_(sources)
    ).all()
    return news_items



def get_sources_without_news_by_date_sources(db: Session, date: date, sources: List[str]):
    """
    Определяет источники, по которым нет новостей за выбранный день.

    Args:
        db (Session): Активная SQLAlchemy-сессия.
        date (date): Дата, за которую проверяется наличие новостей.
        sources (List[str]): Список описаний источников для проверки.

    Returns:
        List[str]: Источники, для которых в БД не найдено ни одной новости.
    """
    # Получение начальной и конечной даты для выбранного дня
    start_date = date
    end_date = date + timedelta(days=1)
    sources_without_news = []

    for source in sources:
        # Каждый источник проверяется отдельно, чтобы затем запустить парсинг только по недостающим данным.
        news_count = db.query(models.News).join(models.Source).filter(
            models.News.date >= start_date,
            models.News.date < end_date,
            models.Source.description == source
        ).count()

        if news_count == 0:
            sources_without_news.append(source)

    return sources_without_news



def create_clusters(db: Session, clusters: List[schemas.ClusterCreate]):
    """
    Сохраняет кластеры и связывает их с источниками и исходными новостями.

    Args:
        db (Session): Активная SQLAlchemy-сессия.
        clusters (List[schemas.ClusterCreate]): Валидированные данные кластеров.

    Returns:
        None: Функция изменяет состояние БД и не возвращает значение.
    """

    if clusters:
        # Получение общей даты и источников из первого кластера
        common_date = clusters[0].date
        common_sources = clusters[0].sources

        # Перед сохранением новой сводки удаляются старые кластеры для той же даты и набора источников.
        existing_clusters = db.query(models.Cluster).filter(
            and_(
                models.Cluster.date == common_date,
                models.Cluster.sources.any(models.Source.description.in_(common_sources))
            )
        ).all()

        for existing_cluster in existing_clusters:
            # Удаление существующего кластера и связанных записей
            db.delete(existing_cluster)
            db.commit()

        for cluster in clusters:
            # Создание записи кластера в таблице Cluster
            db_cluster = models.Cluster(
                date=cluster.date,
                create_date=cluster.create_date,
                cluster_num=cluster.cluster_num,
                title=cluster.title,
                summary=cluster.text,
                keywords=cluster.keywords
            )
            db.add(db_cluster)
            db.commit()
            db.refresh(db_cluster)

            # Получение id источников по их описанию и создание записей в таблице связке cluster_sources
            sources = db.query(models.Source).filter(models.Source.description.in_(cluster.sources)).all()
            for source in sources:
                db_cluster.sources.append(source)
            db.commit()

            # Создание записей в таблице связке news_clusters
            for news_id in cluster.news_ids:
                db_cluster.news.append(db.query(models.News).filter(models.News.news_id == news_id).first())
            db.commit()



def get_clusters_by_sources_and_date(db: Session, sources: List[str], selected_date: date):
    """
    Возвращает сохраненные кластеры для точного набора источников и даты.

    Args:
        db (Session): Активная SQLAlchemy-сессия.
        sources (List[str]): Выбранные пользователем источники.
        selected_date (date): Дата, за которую запрошена сводка.

    Returns:
        defaultdict: Словарь кластеров с новостями, ключевыми словами, заголовком и текстом.
    """
    clusters = db.query(models.Cluster).filter(models.Cluster.date == selected_date).all()

    result = defaultdict(lambda: {'items': [], 'keywords': [], 'cluster_title': '', 'cluster_text': ''})
    for cluster in clusters:
        cluster_sources = [source.description for source in cluster.sources]
        # Кластер подходит только если его источники полностью совпадают с выбранными пользователем.
        if set(sources) == set(cluster_sources) and len(sources) == len(cluster_sources):
            result[cluster.cluster_num] = {
                'items': cluster.news,
                'keywords': cluster.keywords.split(' '),
                'cluster_title': cluster.title,
                'cluster_text': cluster.summary
            }

    return result
