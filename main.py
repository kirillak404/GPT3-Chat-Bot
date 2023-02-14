import config
import telebot
import openai
import random
import schedule
import time

#test
bot = telebot.TeleBot(config.telegram_api_key)
openai.api_key = config.openai_api_key


# Генерация ответов на сообщения в чататх через OpenAI
def request_openai_ansewer(chat_history):
    prompt = f'Кетут это просветленный чат-бот мужского пола, живущий на Бали и увлекающийся осознанностью, ' \
             f'вдумчиво отвечающий на сообщения с шутками и сарказом, ' \
             f'добавляя в ответ emoji и имя автора (на русском) сообщения:\n\n{chat_history}\nКетут (бот):'
    print(prompt)
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.7,
            max_tokens=400,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop = ["автор", "отвечает", "от Кетута"]
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


# Кастомный запрос ответа от OpenAI
def request_openai_wishes(message):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=message,
            temperature=0.7,
            max_tokens=800,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].text
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


context = dict()  # тут храним последние 5 сообщений из чатов

def update_chat_history(chat_id, name, message):
    if chat_id not in context:
        context[chat_id] = []
    context[chat_id].append(f'{name}: {message}')
    context[chat_id] = context[chat_id][-5:]
    return '\n'.join(context[chat_id])


@bot.message_handler(func=lambda message: True)
def echo_all(message):

    chat_history = update_chat_history(message.chat.id, message.from_user.first_name, message.text)
    if 'кетут' in message.text.lower()\
            or (message.reply_to_message and message.reply_to_message.from_user.id == 5615844922)\
            or (len(message.text) >= 50 and random.randint(1, 3) == 3):

        bot.send_chat_action(message.chat.id, 'typing')
        answer = request_openai_ansewer(chat_history)  # это отправляем в OpenAI
        if answer:
            update_chat_history(message.chat.id, 'Кетут (бот)', answer)
            bot.reply_to(message, answer)
        else:
            pass


# Отправка сообщений по таймеру
def send_morning_message():
    text = 'Тебя зовут Кетут (мужской пол), ты живешь на Бали и ты умный чат-бот. ' \
           'Напиши забавное и развернутое сообщение в стихах, где сначала идет общее пожеланиями доброго утра всем, кто на острове Бали, ' \
           'а затем пожелай каждому в участнику чата (Кирилл, Саша, Луиза, Ваня, Марина) в отдельности что-нибудь хорошее. ' \
           'Добавь в сообщение emoji.'
    good_morning_text = request_openai_wishes(text)
    bot.send_message(chat_id=-1001717963418, text=good_morning_text)

schedule.every().day.at("10:00").do(send_morning_message)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    import threading
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.start()
    bot.infinity_polling()