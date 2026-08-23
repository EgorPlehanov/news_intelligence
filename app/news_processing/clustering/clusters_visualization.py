from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os



def generate_wordclouds(clusters):
    """
    Строит облака слов для кластеров новостей.

    Args:
        clusters (dict): Словарь кластеров, где каждому кластеру соответствует список новостей.

    Returns:
        None: Функция отображает графики через matplotlib.
    """
    for cluster_label, news_items in clusters.items():
        # Для облака слов используются уже предобработанные тексты, чтобы убрать шумовые слова.
        text = ' '.join(news_item.preprocessed_text for news_item in news_items)

        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        font_path = os.path.join(root_path, 'fonts', 'Roboto-Regular.ttf')
        print(font_path)
        wordcloud = WordCloud(font_path=font_path).generate(text)

        plt.figure(figsize=(8, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.title(f'Cluster {cluster_label}')
        plt.show()

        # wordcloud.to_file("images/wordcloud_{cluster_label}.png")
