from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import uvicorn
from datetime import datetime, date
import os

# Импорт функций парсинга новостей
from .news_parser.parser_scheduler import start_scheduler
# Импорт функций кластеризации и сжатия новостей
from .news_processing.processing import news_processing



# Загрузка переменных окружения из файла .env
load_dotenv(".env")

# Запуск планировщика парсера новостей в отдельном потоке
start_scheduler()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/run-script")
async def run_script(request: Request):
    form = await request.form()
    selected_sources = form.getlist('items')[0].split(',')   #['ria', 'kp', 'Lenta']
    selected_date_text = form.getlist('date')[0]
    selected_date = datetime.strptime(selected_date_text, '%Y-%m-%d').date() if selected_date_text else date.today()

    if len(selected_sources) > 0 and selected_sources != ['']:
        news_blocks = news_processing(selected_date, selected_sources)
    else:
        news_blocks = []

    return templates.TemplateResponse("news.html", {"request": request, "news_data": news_blocks})
    


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", 8000)

    print('Сервер запущен')

    uvicorn.run("main:app", host=host, port=port, reload=True)
    # uvicorn.run("main:app", host=host, port=port)


# Запуск сервера командой bush
# uvicorn app.main:app --reload
# uvicorn app.main:app --host 0.0.0.0 --port 8000

# Удаление всех файлов __pycache__ в проекте (ДЛЯ POWERSHELL)
# Get-ChildItem -Include __pycache__ -Recurse -Directory | Remove-Item -Force -Recurse