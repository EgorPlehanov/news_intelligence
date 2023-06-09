import hdbscan
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
# Импорт функций создания сессии базы данных
from app.database import get_db
from app.crud import get_news_by_date_sources
from .clustering_utils import extract_keywords
from ..summarize.summarize_utils import evaluate_clustering



def clusterize_news(sources, date):
    # Вызов CRUD-операции для получения новостей из базы данных
    with get_db() as db:
        news_items = get_news_by_date_sources(db, date, sources)

    # Подготовка данных
    documents = []
    for news_item in news_items:
        documents.append(news_item.preprocessed_text)

    # Применение векторизации TF-IDF
    vectorizer = TfidfVectorizer()
    data_vectorized = vectorizer.fit_transform(documents)

    # # Применение метода понижения размерности (Truncated SVD)
    # svd = TruncatedSVD(n_components=100)
    # X = svd.fit_transform(X)

    # # Стандартизация данных
    # scaler = StandardScaler()
    # X = scaler.fit_transform(X)

    # Кластеризация новостей с использованием алгоритма HDBSCAN
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=2,
        gen_min_span_tree=True
        # min_cluster_size=5,
        # min_samples=2,
        # alpha=0.5,
        # cluster_selection_epsilon=0.5,
        # cluster_selection_method='eom'
    )
    clusterer.fit(data_vectorized.toarray())

    # 'labels_' содержит метки кластеров для каждого текста
    cluster_labels = clusterer.labels_

    # Оценка кластеризации
    print('\nОценка кластеризации: ', evaluate_clustering(cluster_labels, data_vectorized.toarray()), end='\n\n')

    # Распределение новостей по кластерам
    clusters = defaultdict(lambda: {'items': [], 'keywords': []})
    for i, news_item in enumerate(news_items):
        cluster_label = cluster_labels[i]
        if cluster_label != -1:  # Исключаем выбросы
            cluster = clusters[cluster_label]
            cluster['items'].append(news_item)

        else:
            print(f"Выброс новости: {news_item.title}")

    print('Всего новостей', len(news_items))
    print('Выброшено новостей', len(news_items) - sum(len(cluster_dict['items']) for cluster_dict in clusters.values()))

    # Получение списка ключевых слов для каждого кластера
    for cluster_label, cluster_dict in clusters.items():
        cluster_documents = ' '.join([item.preprocessed_text for item in cluster_dict['items']])
        # Сохранение списка ключевых слов в словаре кластера
        cluster_dict['keywords'] = extract_keywords(cluster_documents)

    return clusters