import telebot
from telebot import types
from array import *
import random
import json

TOKEN = '1495900402:AAEg8wskz_ET0Vyc4NItXkNvMQfHVfrKU6U'
bot = telebot.TeleBot(TOKEN)

with open('questions.json') as f:
    jsonFile = json.load(f)

count_tasks = 3                         # Общее количество вопросов в тесте
current_task = 0                        # Текущее задание
count_right_tasks = 0                   # Количество правильных ответов
test_already_start = False              # Запущен тест или нет
array_of_questions = [0] * count_tasks  # Список заданий для выполнения


def generate_tasks(array_of_questions, count_tasks):
    for x in range(count_tasks):
        array_of_questions[x] = random.randint(0, len(jsonFile['contents']))
        print(array_of_questions[x])


# Handles all text messages that contains the commands '/start'
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id,
                     "Здравствуйте! Данный бот реализован для помощи в подготовке к ЕГЭ по информатике по заданию "
                     "раздела Логика - Составление таблицы истинности логической функции. Строки с пропущенными "
                     "значениями.")
    add_keyboard(message.chat.id)
    global current_task
    global count_right_tasks
    global test_already_start
    current_task = 0
    count_right_tasks = 0
    test_already_start = False


# Отображение кнопок для получения материалов и начала теста
def add_keyboard(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    key_info = types.InlineKeyboardButton(text='Материалы для подготовки', callback_data='key_info')
    keyboard.add(key_info)
    key_start = types.InlineKeyboardButton(text='Начать тест', callback_data='start_test')
    keyboard.add(key_start)
    # Показываем все кнопки сразу и пишем сообщение о выборе
    bot.send_message(chat_id,
                     text='Для получения информации по способам решения данного задания выберите «Материалы для '
                          'подготовки». \nДля начала выполнения теста выберите «Начать тест».',
                     reply_markup=keyboard)


# Обработчик нажатий на кнопки key_info и start_test
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global current_task
    global test_already_start
    global array_of_questions
    if call.data == "key_info":
        bot.send_message(call.message.chat.id, 'В файле ниже представлены материалы, которые помогут с решением задач '
                                               'из демо-вариантов ЕГЭ: сравниваются несколько способов решения, '
                                               'анализируются их достоинства и недостатки, возможные проблемы и '
                                               '«ловушки». Приведены рекомендации, позволяющие выбрать эффективные '
                                               'методы решения каждой конкретной задачи.')
        doc = open('assets/documents/ege2.doc', 'rb')
        bot.send_document(call.message.chat.id, doc)
        bot.send_message(call.message.chat.id, 'Для подготовки к данному заданию также можно ознакомиться с видео-материалом: https://youtu.be/CYYLntd--YA')
    elif call.data == "start_test":
        if not test_already_start:
            bot.send_message(call.message.chat.id, 'Начинаем тест!')
            bot.send_message(call.message.chat.id, 'Для досрочного завершения теста используйте команду /stop')
            test_already_start = True
            generate_tasks(array_of_questions, count_tasks)
            send_photo(call.message.chat.id, current_task, array_of_questions[current_task])
        else:
            bot.send_message(call.message.chat.id, 'Вы уже начали тест!')


@bot.message_handler(content_types=['text'])
def send_text(message):
    global current_task
    global count_right_tasks
    global test_already_start
    right_answer = jsonFile["contents"][array_of_questions[current_task]]['right_answer']
    if test_already_start:
        if message.text == '/stop':
            end_test(message.chat.id, count_right_tasks)
        else:
            if message.text.lower() == right_answer.lower():
                bot.send_message(message.chat.id, 'Молодец! Правильный ответ.')
                count_right_tasks += 1
                if current_task + 1 == count_tasks:
                    end_test(message.chat.id, count_right_tasks)
                else:
                    current_task += 1
                    send_photo(message.chat.id, current_task, array_of_questions[current_task])
            else:
                bot.send_message(message.chat.id, 'Неверный ответ! Верное решение:')
                img = open('assets/img/answers/' + jsonFile["contents"][array_of_questions[current_task]]['answer_img'], 'rb')
                bot.send_photo(message.chat.id, img)
                if current_task + 1 == count_tasks:
                    end_test(message.chat.id, count_right_tasks)
                else:
                    current_task += 1
                    send_photo(message.chat.id, current_task, array_of_questions[current_task])


# Функция для отправки задания
def send_photo(chat_id, current_task, question_number):
    bot.send_message(chat_id, 'Вопрос #' + str(current_task + 1))
    img = open('assets/img/tasks/' + jsonFile["contents"][question_number]['task_img'], 'rb')
    bot.send_photo(chat_id, img)


# Функция для завершения теста и обнуления всех счетчиков
def end_test(chat_id, count_right_answer):
    global current_task
    global count_right_tasks
    global test_already_start
    current_task = 0
    count_right_tasks = 0
    test_already_start = False
    bot.send_message(chat_id, "Тест завершен! Количество правильных ответов: " + str(count_right_answer))
    add_keyboard(chat_id)


# Обрабатывает все сообщения документы, аудио и фото
@bot.message_handler(content_types=['document', 'audio', 'photo'])
def handle_docs_audio(message):
    bot.send_message(message.chat.id, "К сожалению, я не понимаю такой формат файлов. Пожалуйста, используйте "
                                      "текстовые сообщения для работы с ботом.")


if __name__ == '__main__':
    bot.polling(none_stop=True)


bot.polling()

