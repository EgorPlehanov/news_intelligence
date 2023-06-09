from transformers import AutoTokenizer

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

from rouge_score import rouge_scorer
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
# nltk.download('stopwords')
# nltk.download('punkt')



def count_tokens(text):
    '''Считает количество токенов в тексте'''
    # Загрузка предварительно обученного токенизатора
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

    # Токенизация текста
    tokens = tokenizer.tokenize(text)

    # Подсчет количества токенов
    return len(tokens)



def summarize_text(text, sentences_count = 4):
    '''Сокрошение текста'''
    parser = PlaintextParser.from_string(text, Tokenizer("russian"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences_count=sentences_count)

    return ' '.join(str(s) for s in summary)



def evaluate_text_reduction(original_text, shortened_text):
    # Удаление пунктуации и приведение к нижнему регистру
    original_text = original_text.lower()
    shortened_text = shortened_text.lower()

    # Удаление стоп-слов
    stop_words = nltk.corpus.stopwords.words('russian')
    tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
    original_word_list = tokenizer.tokenize(original_text)
    shortened_word_list = tokenizer.tokenize(shortened_text)
    original_word_list = [word for word in original_word_list if word not in stop_words]
    shortened_word_list = [word for word in shortened_word_list if word not in stop_words]

    # Расчет коэффициента Жаккара
    original_set = set(original_word_list)
    shortened_set = set(shortened_word_list)
    jaccard_coefficient = len(original_set.intersection(shortened_set)) / len(original_set.union(shortened_set))

    # Расчет косинусного расстояния
    vectorizer = TfidfVectorizer()
    vectorized_text = vectorizer.fit_transform([original_text, shortened_text])
    cosine_distance = 1 - vectorized_text[0].dot(vectorized_text[1].T).toarray()[0][0]

    # Расчет BLEU
    original_tokens = nltk.word_tokenize(original_text)
    shortened_tokens = nltk.word_tokenize(shortened_text)
    bleu_score = nltk.translate.bleu_score.sentence_bleu([original_tokens], shortened_tokens)

    # Расчет ROUGE
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    rouge_scores = scorer.score(original_text, shortened_text)
    rouge_f_score = rouge_scores['rougeL'].fmeasure

    # Расчет удельной частоты уникальных слов
    original_unique_words = set(original_word_list)
    shortened_unique_words = set(shortened_word_list)
    original_word_density = len(original_unique_words) / len(original_word_list)
    shortened_word_density = len(shortened_unique_words) / len(shortened_word_list)

    # Вывод результатов оценки
    scores = {
        "Коэффициент Жаккара": jaccard_coefficient,
        "Косинусное расстояние": cosine_distance,
        "BLEU": bleu_score,
        "ROUGE F-мера": rouge_f_score,
        "Удельная частота уникальных слов (исходный текст)": original_word_density,
        "Удельная частота уникальных слов (сокращенный текст)": shortened_word_density
    }

    # print(scores)
    return scores



from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

def evaluate_clustering(labels, features):
    """
    Функция оценки качества кластеризации.

    Параметры:
    labels (list): Список меток кластеров для каждого объекта.
    features (list): Список признаков для каждого объекта. 
                     Должен быть двумерным (количество объектов x количество признаков).

    Возвращает:
    dict: Словарь со значениями метрик.
    """

    metrics = {}

    metrics['Silhouette Score'] = silhouette_score(features, labels)
    metrics['Davies-Bouldin Index'] = davies_bouldin_score(features, labels)
    metrics['Calinski-Harabasz Index'] = calinski_harabasz_score(features, labels)

    return metrics

# # Предполагается, что вы уже провели кластеризацию и получили метки кластеров.
# # 'labels' - это метки кластеров, а 'features' - это признаки объектов.
# metrics = evaluate_clustering(labels, features)

# # Вывод значений метрик.
# for metric, value in metrics.items():
#     print(f'{metric}: {value}')
