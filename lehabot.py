# лехабот лоутаб
import telebot
from telebot import types
bot = telebot.TeleBot("7840655318:AAEYDbfYWDZQQj80bFbSKQBaSyYkeG2vhQ0")

@bot.message_handler(commands=["start", "hub", "main", "nekit"])
def main(message):
    bot.send_message(message.chat.id, "Привет! Отправь фотографию, и я сделаю стикер")

@bot.message_handler(content_types=["photo"])
def get_photo(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Вырезать объект из фото", callback_data="cut")
    btn2 = types.InlineKeyboardButton("Удалить фото", callback_data="delete")
    markup.row(btn2, btn1)
    bot.reply_to(message, "Выбери, что делать с фото", reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == "delete":
        bot.delete_message(callback.message.chat.id, callback.message.reply_to_message.message_id)
    elif callback.data == "cut":
        bot.edit_message_text("GAY GAy Gay gay ay y",callback.message.chat.id, callback.message.message_id)
        file = open("./output.png", "rb")
        bot.send_photo(callback.message.chat.id, file)

bot.polling(none_stop=True)
