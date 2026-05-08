from collections import defaultdict
import logging
from openai import OpenAI
import telebot
import random
import os


from bot_logic import gen_pass, gen_emodji, flip_coin
from tokens import BOT_TOKEN, OPENAI_API_KEY

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

dialog_history = defaultdict(list)

# Максимум последних фраз
MAX_HISTORY = 5

SYSTEM_PROMPT = """
Ты экологический помощник.

Ты отвечаешь только на темы:
- экология
- сортировка мусора
- переработка
- защита природы
- климат
- уменьшение выбросов CO2
- экономия воды и энергии
- устойчивый образ жизни

Если вопрос не относится к экологии —
вежливо скажи, что ты специализируешься только на экологических темах.

Отвечай простым и понятным языком.
"""




    
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой Telegram бот. Напиши что-нибудь!\nИспользуй /help чтобы узнать мои команды.")
    
@bot.message_handler(commands=['hello'])
def send_hello(message):
    bot.reply_to(message, "Привет! Как дела?")
    
@bot.message_handler(commands=['bye'])
def send_bye(message):
    bot.reply_to(message, "Пока! Удачи!")

@bot.message_handler(commands=['mem'])
def send_mem(message):
    img_dir = 'bot/images'
    # А вот так можно подставить имя файла из переменной!
    img_name = random.choice(os.listdir(img_dir))
    with open(f'{img_dir}/{img_name}', 'rb') as f:   # type: ignore
        bot.send_photo(message.chat.id, f)  


@bot.message_handler(commands=['eco'])
def send_eco(message):
    bot.reply_to(message, "Привет вот твой сайте:  https://free-eco.ru/articles/top-20-ekologicheskih-saytov ")


@bot.message_handler(commands=['pass'])
def send_bye(message):  
    bot.reply_to(message, "Привет вот твой пароль:" +  gen_pass(10))


@bot.message_handler(commands=['emodji'])
def send_emodji(message):
    emodji = gen_emodji()
    bot.reply_to(message, f"Вот эмоджи': {emodji}")

@bot.message_handler(commands=['coin'])
def send_coin(message):
    coin = flip_coin()
    bot.reply_to(message, f"Монетка выпала так: {coin}")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Вот список команд, которые я понимаю:\n /start - начать общение с ботом\n /hello - поздороваться с ботом\n /bye - попрощаться с ботом\n /pass - сгенерировать пароль\n /emodji - получить случайный эмоджи\n /coin - подбросить монетку\n /mem - получить мем \n /eco - получить сайт с экологической тематикой\n /help - показать это сообщение")


# Handle '/start' and '/help'
@bot.message_handler(commands=['say'])
def gpt_answer(message):
    bot.reply_to(message, """\
Привет! 🌱
Я экологический бот.
Спроси меня про сортировку мусора, защиту природы или снижение выбросов.
""")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    user_id = message.from_user.id
    user_text = message.text

    logging.info(f"Received message from user {user_id}: {user_text}")

    # Добавляем сообщение пользователя в историю
    dialog_history[user_id].append({
        "role": "user",
        "content": user_text
    })

    # Оставляем только последние 5 сообщений
    dialog_history[user_id] = dialog_history[user_id][-MAX_HISTORY:]

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(dialog_history[user_id])

    # logging.debug(f"Sending messages to OpenAI for user {user_id}: {messages}")
 
    thinking_message = bot.reply_to(message,
        "🤔 I am thinking..."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )

        bot_reply = response.choices[0].message.content

        logging.info(f"Received response from OpenAI for user {user_id}: {bot_reply}")

        # Сохраняем ответ бота
        dialog_history[user_id].append({
            "role": "assistant",
            "content": bot_reply
        })

        # Опять обрезаем историю
        dialog_history[user_id] = dialog_history[user_id][-MAX_HISTORY:]

        bot.delete_message(thinking_message.chat.id, thinking_message.message_id)
        
        bot.reply_to(message, bot_reply)

    except Exception as e:
        logging.error(f"Error while processing message from user {user_id}: {str(e)}")

        bot.reply_to(message, f"Ошибка: {str(e)}")

    



@bot.message_handler(commands=['eco_2'])
def echo_message_2(message):
    bot.reply_to(message, "Вот еще один экологический сайт: https://www.greenpeace.org/")

@bot.message_handler(commands=['eco_3'])
def echo_message_3(message):
    bot.reply_to(message, " Вот еще один экологический сайт: https://www.wwf.org/")



@bot.message_handler(commands=['eco_2'])
def echo_message_2(message):
    bot.reply_to(message, "Вот еще один экологический сайт: https://www.greenpeace.org/")

@bot.message_handler(commands=['eco_3'])
def echo_message_2(message):
    bot.reply_to(message, "")

logging.basicConfig(level=logging.INFO)
logging.info("starting bot")

bot.infinity_polling(
    logger_level=logging.INFO,
    # restart_on_change=True,
)

    
