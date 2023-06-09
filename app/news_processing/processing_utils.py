from app.database import get_db
from app.schemas import ClusterCreate
from app.crud import create_clusters



def validate_and_save_clusters(summaries_news_blocks, selected_date, selected_sources):
    '''Валидация и сохранение кластеров'''
    validated_clusters = []
    for cluster_label, cluster_dict in summaries_news_blocks.items():
        cluster_title = cluster_dict.get('cluster_title', 'None')
        cluster_text = cluster_dict.get('cluster_text', 'None')
        keywords = ' '.join(cluster_dict['keywords'])
        news_ids = [news.news_id for news in cluster_dict['items']]

        cluster_create = ClusterCreate(
            date=selected_date,
            cluster_num=cluster_label,
            title=cluster_title,
            text=cluster_text,
            keywords=keywords,
            news_ids=news_ids,
            sources=selected_sources
        )

        # Валидация объекта кластера
        validated_clusters.append(cluster_create)

    # Сохранение кластеров
    with get_db() as db:
        create_clusters(db, validated_clusters)



def convert_clasters_to_dict(clusters, selected_date):
    '''Преобразование кластеров в словарь'''
    result = {"date": selected_date.strftime('%d.%m.%Y'), "news_blocks": []}
    for cluster_lable, cluster_dict in clusters.items():
        news_list = cluster_dict['items']
        links = []
        for news in news_list:
            links.append({'date': news.date.strftime('%H:%M %d.%m.%Y'), "url": news.link, "link_title": news.title})
        result['news_blocks'].append({
            "title": cluster_dict['cluster_title'] if 'cluster_title' in cluster_dict else '1 1',
            "text": cluster_dict['cluster_text'] if 'cluster_text' in cluster_dict else '1 1',
            "links": sorted(links, key=lambda x: x['date']),
            "keywords": cluster_dict['keywords']
        })
    return result