import threading
import schedule
import time
from .parser import parse_news



def schedule_job():
    '''Запуск задачи парсинга новостей раз в час'''
    # Определяем начальное время расписания на полуночь
    schedule.every(1).hours.at(':01').do(parse_news)
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_scheduler():
    '''Запуск планировщика в отдельном потоке'''
    schedule_thread = threading.Thread(target=schedule_job)
    schedule_thread.start()
