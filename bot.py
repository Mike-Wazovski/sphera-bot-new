import os
import telegram
from telegram.ext import Updater, MessageHandler, filters
import openai
from PIL import Image
import requests
from io import BytesIO

# === ТВОИ НАСТРОЙКИ (НЕ МЕНЯЙ!) ===
TELEGRAM_TOKEN = "8026450624:AAFCN-efXeC1psLFRNsZN5uPwwgydOHPD00"
CHAT_ID = 1570500473
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ===================================

# Инициализация
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
bot = telegram.Bot(token=TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

def image_to_text(photo_file):
    try:
        image_bytes = BytesIO()
        photo_file.download(out=image_bytes)
        image_bytes.seek(0)
        image = Image.open(image_bytes)

        buffer = BytesIO()
        image.convert("RGB").save(buffer, format="JPEG")
        img_base64 = buffer.getvalue().encode('base64').decode().replace('\n', '')

        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Реши задачу кратко. Ответ до 100 слов."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"image/jpeg;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка GPT: {str(e)}"

def handle_message(update, context):
    chat_id = update.effective_chat.id
    if chat_id != CHAT_ID:
        return

    try:
        if update.message.photo:
            photo = update.message.photo[-1]
            photo_file = photo.get_file()
            answer = image_to_text(photo_file)
            bot.send_message(chat_id=chat_id, text=f"🧠 Ответ:\n{answer}")

        elif update.message.text:
            text = update.message.text
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Кратко реши: {text}"}],
                max_tokens=150
            )
            answer = response.choices[0].message.content.strip()
            bot.send_message(chat_id=chat_id, text=f"🧠 Ответ:\n{answer}")

    except Exception as e:
        bot.send_message(chat_id=chat_id, text=f"❌ Ошибка: {str(e)}")

# Обработчики
updater.dispatcher.add_handler(MessageHandler(filters.PHOTO, handle_message))
updater.dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Запуск
updater.start_polling()
print("✅ Бот запущен и ждёт сообщения...")
updater.idle()
