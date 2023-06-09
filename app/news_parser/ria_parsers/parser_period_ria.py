from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import os
from bs4 import BeautifulSoup
from app.schemas import NewsCreate
from typing import List
from ..parser_utils import parse_date
from .parser_scheduler_ria import get_article_text
from app.news_processing.clustering.clustering_utils import preprocess_text



def get_news_data(start_time, end_time, content)-> List[NewsCreate]:
    '''Вытаскиваем из html кода списка данные о новостях'''
    news_list = []
    
    soup = BeautifulSoup(content, 'html.parser')
    news_blocks = soup.find_all('div', class_='list-item')

    for block in news_blocks:
        # Извлечение информации о новости
        date = block.find('div', class_='list-item__date').text.strip()
        news_datetime = parse_date(date)

        print(news_datetime)    # Отслеживаем дату

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
            break

    return news_list[::-1]


def parse_ria_news_period_data(start_date=None, end_date=None, is_save_to_file=False):
    '''Собираем новости за указанный период'''
    if start_date is None:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    elif not isinstance(start_date, datetime):
        start_date = datetime.combine(start_date, datetime.min.time())
    
    if end_date is None:
        end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
    elif not isinstance(end_date, datetime):
        end_date = datetime.combine(end_date, datetime.max.time()).replace(microsecond=0)

    try:
        # Адрес страницы с новостями на сайте РИА Новости
        url = f'https://ria.ru/{end_date.strftime("%Y%m%d")}/'

        # Инициализация драйвера браузера (например, Chrome)
        driver = webdriver.Chrome()

        # Открытие страницы
        driver.get(url)

        # Прокручивание страницы вниз
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(1)  # Добавляем задержку для полной загрузки новых элементов

        # Нажатие на кнопку "Еще 20 материалов"
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="list-more color-btn-second-hover"]'))
        )
        button.click()

        # Прокручиваем страницу для загрузки остальных новостей
        while True:
            # Прокручивание страницы вниз
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(1)  # Добавляем задержку для полной загрузки новых элементов

            # Ожидание загрузки новых элементов
            # Вам может потребоваться адаптировать селектор и условия ожидания в соответствии с вашим случаем
            new_items = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="list"]'))
            )

            # Проверяем, сколько новых элементов было загружено
            if len(new_items) == 0:
                break  # Прерываем цикл, если новые элементы больше не загружаются

            # Получаем дату последнего загруженного элемента

            last_date_element = new_items[0].find_elements(By.XPATH, './/div[@class="list-item__date"]')[-1]
            date_str = last_date_element.text.strip()
            news_date = parse_date(date_str)

            # Проверяем, не выходит ли новость за указанную дату
            if news_date < start_date:
                break  # Прерываем цикл, если новость выходит за указанную дату

        content = new_items[0].get_attribute('innerHTML')

        # Сохранение содержимого в файл
        if is_save_to_file:
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ria_data.html')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        driver.quit()   # Закрытие браузера

        # Вытаскиваем из html кода списка данные о новостях
        news_list = get_news_data(start_date, end_date, content)

        return news_list
    
    except Exception as e:
        # Обработка ошибки
        if 'driver' in locals():
            driver.quit()   # Закрытие браузера
            
        print(f"An error occurred: {e}")
        return []


# ПРИМЕР ВЫЗОВА ==================================================================================

# start_date = datetime(2023, 5, 27)  # Замените эту дату на нужную вам
# end_date = datetime.now()  # Замените эту дату на нужную вам
# news_items = parse_news_period_data(start_date, end_date)

# TEST ================================================================================
# content = parse_news_period_data( datetime(2023, 5, 22),  datetime(2023, 5, 28))
# with open(r'D:\!!!DIPLOM\NEW_NewsParser\news_parse_FastAPI\app\news_parser\ria_data.html', 'r', encoding='utf-8') as file:
    # content = file.read()
# TEST ================================================================================
