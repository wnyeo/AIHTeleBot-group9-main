import telebot
import os
from dotenv import load_dotenv
import model

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
bot.set_webhook()

@bot.message_handler(commands=['start'])
def start(message):
    """
    Bot will introduce itself upon /start command, and prompt user for his request
    """
    try:
        # Start bot introduction
        start_message = "Hello! Ask me anything about HealthServe or interacting with migrant workers. I will help to answer your queries as much as I can! \n \n 你好！您可以向我询问有关 HealthServe 或与外籍员工互动的任何问题。我会尽我所能帮助解答您的疑问。"
        bot.send_message(message.chat.id, start_message)

    except Exception as e:
        bot.send_message(
            message.chat.id, 'Sorry, something seems to gone wrong! Please try again later!')


@bot.message_handler(content_types=['text'])
def send_text(message):
    response = model.getResponse(message.text)
    bot.send_message(message.chat.id, response)

def main():
    """Runs the Telegram Bot"""
    print('Loading the configurations...') 
    print('Successfully loaded! Starting bot... Ready to serve!')
    bot.infinity_polling()

if __name__ == '__main__':
    main()