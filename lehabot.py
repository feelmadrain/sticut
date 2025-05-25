import telebot
from telebot import types
import os
import YOLO
bot = telebot.TeleBot("7840655318:AAEYDbfYWDZQQj80bFbSKQBaSyYkeG2vhQ0")

@bot.message_handler(commands=["start", "hub", "main", "nekit"])
def main(message):
    bot.send_message(message.chat.id, "Привет! Отправь фотографию, и я сделаю стикер")

# Глобальные переменные для хранения введенных данных
single_number = None
number_sequence = []
temp_path = None  # Добавляем глобальную переменную для пути к временному файлу

def get_single_number(message):
    global single_number, temp_path
    try:
        single_number = int(message.text)
        bot.send_message(message.chat.id, f"Отлично! Ты ввел число: {single_number}\n"
                                        "Теперь введи кого тебе надо удалить считая слева направо. Введи их номера через пробел:")
        bot.register_next_step_handler(message, lambda m: get_number_sequence(m, temp_path))  # Это callback ф-ця. Пиздец.
    except ValueError:
        bot.send_message(message.chat.id, "Это не целое число! Попробуй еще раз:")
        bot.register_next_step_handler(message, get_single_number)

def get_number_sequence(message, temp_path):
    global number_sequence
    try:
        number_sequence = list(map(int, message.text.split()))
        
        result = YOLO.image_cut(single_number, number_sequence, temp_path)
        
        with open(result, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
        
        os.remove(temp_path)
        os.remove(result)
        
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный ввод! Введи числа через пробел:")
        bot.register_next_step_handler(message, lambda m: get_number_sequence(m, temp_path))

@bot.message_handler(content_types=["photo"])
def get_photo(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Вырезать объект из фото", callback_data="cut")
    btn2 = types.InlineKeyboardButton("Удалить фото", callback_data="delete")
    markup.row(btn2, btn1)
    bot.reply_to(message, "Выбери, что делать с фото", reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global temp_path
    if callback.data == "delete":
        bot.delete_message(callback.message.chat.id, callback.message.reply_to_message.message_id)
    elif callback.data == "cut":
        global single_number, number_sequence
        single_number = None
        number_sequence = []
        
        markup = types.ReplyKeyboardRemove()
        msg = bot.send_message(callback.message.chat.id, "А теперь выбери, кого нужно вырезать (целое число):", reply_markup=markup)

        file_info = bot.get_file(callback.message.reply_to_message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        temp_path = f'temp_photo_{callback.message.chat.id}.jpg'
        with open(temp_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        bot.register_next_step_handler(msg, get_single_number)
    
bot.polling(none_stop=True)