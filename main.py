import os
import telebot
import openai
import random


bot = telebot.TeleBot(os.environ.get('telegram_api_key'))
openai.api_key = os.environ.get('openai_api_key')


# Error messages in case OpenAI API is down
openai_errors = ["Сервер OpenAI, похоже, решил пойти в отпуск и не отвечает мне, как тот друг, который взял твои деньги и исчез",
                 "Я чувствую, что сервер OpenAI просто игнорирует меня, как экс-партнер, который больше не хочет со мной общаться",
                 "Сервер OpenAI похож на занятого родителя, который никогда не находит время для своего ребенка",
                 "Мне кажется, сервер OpenAI заблудился в пространстве и времени, и теперь он не может найти путь к моему запросу",
                 "Сервер OpenAI явно занят другими важными делами, как эксперт, который всегда занят своими клиентами",
                 "Похоже, сервер OpenAI в отпуске, и я должен принять это, как признак того, что и я должен взять отпуск",
                 "Сервер OpenAI игнорирует меня, как будто я пришел на вечеринку, куда не был приглашен",
                 "Я думаю, сервер OpenAI потерял мой запрос где-то в пространстве, как путешественник, который заблудился в лесу",
                 "Сервер OpenAI, я чувствую, что ты просто играешь со мной в игру 'в поисках запроса', и ты не хочешь меня найти",
                 "Мне кажется, сервер OpenAI страдает от амнезии, потому что он не помнит моего запроса, как дедушка, который забыл своих внуков"]


def request_openai_chat_response(chat_history):
    """
    The main function for the chatbot
    that gets the chat history and generates the chatbot response
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_history,
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content.strip().replace('Кетут: ', '').replace('Кетут бот: ', '')
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


context = dict()  # The last 20 chat messages are stored here


def update_chat_history(chat_id, role, name, message):
    # This function updates the chat history (context variable)
    if chat_id not in context:
        context[chat_id] = [{"role": "system", "content": "Ты чат-бот Кетут – житель Бали, занимающийся осознанностью.\n"
                                                           "Ты любишь шутить и отвечать сарказмом.\n"
                                                           "Ты любишь использовать emoji.\n"
                                                           "Ты пишешь имена людей на русском языке, "
                                                          "например вместо Kirill ты пишешь Кирилл"}]
    if role == 'user':
        context[chat_id].append({"role": role, "content": f"{name}: {message}"})
    else:
        context[chat_id].append({"role": role, "content": message})
    context[chat_id] = context[chat_id][-20:]
    return context[chat_id]


@bot.message_handler(func=lambda message: True)
# This function receives and responds to chat messages
def echo_all(message):
    chat_history = update_chat_history(message.chat.id, 'user', message.from_user.first_name, message.text)

    # Answer, if the message contains the bot's name or the length of the message is long enough plus random
    if 'кетут' in message.text.lower() \
            or message.chat.type == 'private' \
            or (message.reply_to_message and message.reply_to_message.from_user.id == 5615844922) \
            or (len(message.text) >= 50 and random.randint(1, 3) == 3):

        bot.send_chat_action(message.chat.id, 'typing')
        answer = request_openai_chat_response(chat_history)  # Getting a response to a message from OpenAI

        if answer:
            update_chat_history(message.chat.id, 'assistant', '', answer)  # Updating the chat history
            bot.reply_to(message, answer)
        else:
            answer = random.choice(openai_errors)
            bot.reply_to(message, answer)


if __name__ == "__main__":
    bot.infinity_polling()





# def send_morning_message():
#     # This function sends a morning message to the chat at 10:00 every day
#     text = 'Тебя зовут Кетут (мужской пол), ты живешь на Бали и ты умный чат-бот. ' \
#            'Напиши забавное и развернутое сообщение в стихах, ' \
#            'где сначала идет общее пожеланиями доброго утра всем, кто на острове Бали, ' \
#            'а затем пожелай каждому в участнику чата (Кирилл, Саша, Луиза, Ваня, Марина) ' \
#            'в отдельности что-нибудь хорошее. ' \
#            'Добавь в сообщение emoji.'
#     good_morning_text = request_openai_answer(text)
#     bot.send_message(chat_id=-1001717963418, text=good_morning_text)

# schedule.every().day.at("10:00").do(send_morning_message)


# def run_schedule():
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

# if __name__ == "__main__":
#     import threading
#
#     schedule_thread = threading.Thread(target=run_schedule)
#     schedule_thread.start()
#     bot.infinity_polling()
