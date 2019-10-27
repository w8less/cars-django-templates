from cars.celery import app
from apps.telegram.config import BOT


@app.task
def send_message(chat_id, text, parse_mode='Markdown'):
    BOT.send_message(chat_id, text=text, parse_mode=parse_mode)
    return 0
