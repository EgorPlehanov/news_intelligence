from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from langdetect import detect
import langcodes
import pymorphy2
from sklearn.feature_extraction.text import CountVectorizer



# Словарь для кэширования результатов, чтобы ускорить лемматизацию
morph_cache = {}
morph = pymorphy2.MorphAnalyzer()


def get_text_language(text):
    '''Определение языка текста'''
    lang_code = detect(text)
    return langcodes.Language(lang_code).language_name('en')


def preprocess_text(text):
    '''Токенизация текста'''
    # Токенизация текста
    tokens = word_tokenize(text)
    
    # Приведение к нижнему регистру
    tokens = [token.lower() for token in tokens]
    
    # Удаление стоп-слов
    stop_words = set(stopwords.words('russian'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Лемматизация с кэшированием
    tokens = [morph_cache[token] if token in morph_cache else morph_cache.setdefault(token, morph.parse(token)[0].normal_form) for token in tokens]
    
    # Удаление символов пунктуации
    tokens = [token for token in tokens if token.isalnum()]
    
    return ' '.join(tokens)



def extract_keywords(text, max_keywords=10):
    # Токенизация текста
    tokens = word_tokenize(text)
    morph = pymorphy2.MorphAnalyzer()
    lemmas = set()
    for token in tokens:
        parsed_token = morph.parse(token)[0]
        if parsed_token.tag.POS in ['NOUN', 'ADJF', 'ADJS', 'VERB', 'INFN']:
            lemmas.add(parsed_token.normal_form)

    # Преобразование множества лемм в список ключевых слов
    keywords = list(lemmas)

    # Создание экземпляра CountVectorizer
    vectorizer = CountVectorizer()

    # Преобразование текста в матрицу признаков
    feature_matrix = vectorizer.fit_transform([token for token in tokens if morph.parse(token)[0].normal_form in keywords])

    # Расчет суммы по столбцам для каждого признака
    feature_sum = feature_matrix.sum(axis=0)

    # Получение списка индексов признаков с наибольшими суммами
    top_feature_indices = feature_sum.argsort()[0, -max_keywords:]

    # Получение списка ключевых слов
    vocabulary = vectorizer.vocabulary_
    keywords = [word for word, index in vocabulary.items() if index in top_feature_indices]

    return keywords
