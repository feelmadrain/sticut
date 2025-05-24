import os
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv
from neural_network import process_image_with_nn
from utils import save_uploaded_image, cleanup_temp_files

# Загрузка токена из .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для вырезания объектов с фото. Отправь мне изображение, и я верну обработанную версию."
    )

# Обработка изображений
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем файл изображения
    photo = update.message.photo[-1]  # Берем изображение с наивысшим разрешением
    file = await photo.get_file()
    
    # Сохраняем изображение во временную папку
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, f"{update.message.message_id}.jpg")
    await file.download_to_drive(file_path)
    
    try:
        # Обрабатываем изображение нейросетью
        output_path = process_image_with_nn(file_path)
        
        # Отправляем результат пользователю
        with open(output_path, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption="Вот вырезанный объект!"
            )
        
        # Очищаем временные файлы
        cleanup_temp_files(file_path, output_path)
    
    except Exception as e:
        await update.message.reply_text(f"Ошибка обработки: {str(e)}")
        cleanup_temp_files(file_path)

# Обработка ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Произошла ошибка. Попробуй еще раз!")
    print(f"Error: {context.error}")

# Основная функция
async def main():
    # Инициализация приложения
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_error_handler(error_handler)
    
    # Запуск бота
    print("Бот запущен...")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    asyncio.run(main())