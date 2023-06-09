import requests
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime, timedelta
from time import sleep
from urllib.parse import urljoin
import re
from app.schemas import NewsCreate
from ..parser_utils import parse_date
from app.news_processing.clustering.clustering_utils import preprocess_text



def get_article_text(url):
    '''Получаем текст статьи'''
    retry_count = 0
    while retry_count < 3:
        try:
            response = requests.get(url)
            response.raise_for_status()
            content = response.content
            soup = BeautifulSoup(content, 'html.parser')
            
            # Находим все блоки статьи с data-type="text"
            article_blocks = soup.find_all('div', class_='article__block', attrs={'data-type': 'text'})
            
            article_text = ''
            
            # Обходим все блоки статьи и извлекаем текст из блока article__text
            for block in article_blocks:
                article_text += ' ' + block.find('div', class_='article__text').text.strip()
            
            # Удаляем ссылки из текста статьи
            article_text = re.sub(r'<a.*?>(.*?)<\/a>', r'\1', article_text)
            
            return article_text
        
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            retry_count += 1
            
            if retry_count >= 3:
                print("Exceeded maximum retry attempts. Returning an empty string.")
                break
            
            print(f"Retrying in 1 minute... (attempt {retry_count})")
            sleep(60)  # Delay for 1 minute before retrying
    
    return ''


def parse_ria_news()-> List[NewsCreate]:
    '''Собираем статьи с сайта РИА Новости'''
     # Получаем текущую дату и время
    now = datetime.now()

    # Вычисляем начальную и конечную даты для последнего часа
    previous_hour = now - timedelta(hours=1)
    start_time = previous_hour.replace(minute=0, second=0, microsecond=0)
    end_time = previous_hour.replace(minute=59, second=59, microsecond=999)

    # Адрес страницы с новостями на сайте РИА Новости
    date_str = (now - timedelta(days=(1 if now.hour == 0 else 0))).strftime("%Y%m%d")
    url = f"https://ria.ru/{date_str}/"

    # Список для хранения новостей
    news_list = []
    has_more_news = True

    while has_more_news:
        try:
            response = requests.get(url)
            content = response.content
            soup = BeautifulSoup(content, 'html.parser')
            news_blocks = soup.find_all('div', class_='list-item')

            for block in news_blocks:
                # Извлечение информации о новости
                date = block.find('div', class_='list-item__date').text.strip()
                news_datetime = parse_date(date)

                # Проверка времени новости и добавление ее в список
                if start_time <= news_datetime <= end_time:
                    title = block.find('a', class_='list-item__title').text.strip()
                    link = block.find('a', class_='list-item__title')['href']
                    article_text = get_article_text(link)
                    preprocessed_text = preprocess_text(article_text)
                    
                    # Создание объекта NewsCreate
                    news = NewsCreate(
                        date=news_datetime, 
                        link=link,
                        title=title, 
                        text=article_text,
                        preprocessed_text=preprocessed_text,
                        source_id=1
                    )
                    news_list.append(news)

                elif news_datetime < start_time:
                    # Если дата новости стала меньше start_time, прекратить сбор новостей
                    has_more_news = False
                    break

            # Поиск кнопки "Еще 20 материалов" на странице
            show_more_button = soup.find('div', class_='list-more')
            if show_more_button is None:
                has_more_news = False
            else:
                show_more_url = show_more_button['data-url']
                # Объединение базового URL страницы с относительным URL кнопки "Еще 20 материалов"
                url = urljoin(url, show_more_url)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            retry_count += 1
            
            if retry_count > 5:
                print("Exceeded maximum retry attempts. Exiting.")
                break
            
            print(f"Retrying in 5 minutes... (attempt {retry_count})")
            sleep(60)  # Delay for 5 minutes before retrying
            continue

    return news_list[::-1]
