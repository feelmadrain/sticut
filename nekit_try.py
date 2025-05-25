import telebot
from telebot import types
import os
import YOLO
bot = telebot.TeleBot('7700215101:AAEsGokVdb7Di_qHRJM4jRASgX-HDPEkv3k')

@bot.message_handler(content_types=['photo'])
def get_photo(message):

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path) # скачиваем картинку

    temp_path=f'temp_photo_{message.chat.id}.jpg'
    with open(temp_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    result = YOLO.image_cut(temp_path)
    bot.send_photo(message.chat.id, photo=result)
    os.remove(temp_path)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Пришлите фото для анализа")

bot.polling(none_stop=True)

