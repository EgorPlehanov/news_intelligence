from datetime import datetime, timedelta



def parse_date(date_str):
    '''Обрабатываем разные форматы даты'''
    now = datetime.now()
    
    if 'Вчера' in date_str:
        date_str = date_str.replace('Вчера,', '')
        news_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        date_str = f"{news_date}, {date_str.strip()}"
    elif ',' in date_str:
        date_parts = date_str.split(',')
        day_month = date_parts[0].strip().split(' ')
        month = {
            'января': '01',
            'февраля': '02',
            'марта': '03',
            'апреля': '04',
            'мая': '05',
            'июня': '06',
            'июля': '07',
            'августа': '08',
            'сентября': '09',
            'октября': '10',
            'ноября': '11',
            'декабря': '12'
        }[day_month[1]]
        news_date = f"{now.year}-{month}-{day_month[0]}"
        date_str = f"{news_date}, {date_parts[1].strip()}"
    else:
        time_str = date_str.strip()
        date_now = now.strftime("%Y-%m-%d")
        date_str = f"{date_now}, {time_str}"
    
    return datetime.strptime(date_str, "%Y-%m-%d, %H:%M")