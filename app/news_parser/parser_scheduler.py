import threading
import schedule
import time
from .parser import parse_news



def schedule_job():
    """
    Создает и выполняет расписание регулярного парсинга новостей.

    Args:
        Нет.

    Returns:
        None: Функция работает в бесконечном цикле планировщика.
    """
    # Определяем начальное время расписания на полуночь
    schedule.every(1).hours.at(':01').do(parse_news)
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_scheduler():
    """
    Запускает планировщик парсинга в отдельном потоке.

    Args:
        Нет.

    Returns:
        None: Функция стартует фоновый поток и не возвращает результат.
    """
    schedule_thread = threading.Thread(target=schedule_job)
    schedule_thread.start()
