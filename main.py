import telebot
from telebot import types
import json
import locale

bot = telebot.TeleBot('5788480055:A***');

name = '';
surname = '';
username = '';
typeusers = '';
chat_id = '';
list_number = '';

individual_message_text = '';
mas = {}


def create_user():  # создание пользователя в базе данных
    data = {}
    data['users'] = []

    with open(r'/Users/igorzaharov/Desktop/botTelegram/studentList.json', 'r', encoding='utf-8') as inputfile:
        data = json.load(inputfile)
    data['users'].append({
        "chatId": chat_id,
        "name": name,
        "surname": surname,
        "username": username,
        "typeusers": typeusers
    })

    with open(r'/Users/igorzaharov/Desktop/botTelegram/studentList.json', 'w') as outfile:
        json.dump(data, outfile, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': '))


def get_name(message):  # получаем имя
    global name, chat_id;
    name = message.text;
    chat_id = message.chat.id;
    bot.send_message(message.from_user.id, 'Какая у тебя фамилия?');
    bot.register_next_step_handler(message, get_surname);


def get_surname(message):  # получаем фамилию
    global surname;
    surname = message.text;
    question = 'Тебя зовут ' + name + ' ' + surname + '?';
    keyboard = types.InlineKeyboardMarkup();  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes');  # кнопка «Да»
    keyboard.add(key_yes);  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no');
    keyboard.add(key_no);
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)




@bot.message_handler(commands=['start'])
def start(message):  # начало регистрации
    global username;
    username = message.from_user.username;
    hello_text = "Приветствую, @" + username + "! я бот помощник для школьных вопросов. Выбери, кем ты являешься"
    keyboard = types.InlineKeyboardMarkup();  # наша клавиатура
    key_student = types.InlineKeyboardButton(text='Ученик', callback_data='student');  # кнопка «Да»
    keyboard.add(key_student);  # добавляем кнопку в клавиатуру
    key_teacher = types.InlineKeyboardButton(text='Учитель', callback_data='teacher');
    keyboard.add(key_teacher);
    bot.send_message(message.from_user.id, text=hello_text, reply_markup=keyboard)


@bot.message_handler(commands=['func'])
def start_way(message):  # развилка по функционалу после регистрации пользователя
    if typeusers == "teacher":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Отправить сообщение всем ученикам")
        item2 = types.KeyboardButton("Отправить сообщение выбранным ученикам")
        markup.add(item1)
        markup.add(item2)
        bot.send_message(message.from_user.id, 'Создавайте свои сообщения для учеников', reply_markup=markup)
    elif typeusers == "student":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Портал МЭШ")
        markup.add(item1)
        bot.send_message(message.from_user.id, 'Выбери функцию', reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, 'Для начала пройдите регистрацию')



def home_task(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Портал МЭШ", url='https://dnevnik.mos.ru/diary/diary/lessons')
    markup.add(button1)
    bot.send_message(message.chat.id, "Нажми на кнопку и перейди на сайт)".format(message.from_user), reply_markup=markup)



@bot.message_handler(content_types=['text'])
def func_processing(message):
    if message.text == 'Отправить сообщение всем ученикам':
        bot.send_message(chat_id, 'Введите текст сообщения');
        bot.register_next_step_handler(message, mass_send_message);
    if message.text == 'Отправить сообщение выбранным ученикам':
        bot.send_message(chat_id, 'Введите текст сообщения');
        bot.register_next_step_handler(message, individual_message);
    if message.text == 'Портал МЭШ':
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("Портал МЭШ", url='https://dnevnik.mos.ru/diary/diary/lessons')
        markup.add(button1)
        bot.send_message(message.chat.id, "Нажми на кнопку и перейди на сайт)".format(message.from_user), reply_markup=markup)
    # вызываем функцию вычитывания всех студентов и создаем сообщения в ЛС


def mass_send_message(message):
    data = {}
    data['users'] = []
    listIdChat = []

    with open(r'/Users/igorzaharov/Desktop/botTelegram/studentList.json', 'r', encoding='utf-8') as inputfile:
        data = json.load(inputfile)
    count = len(data['users'])

    for n in range(count):
        if data['users'][n]['typeusers'] == 'student':
            listIdChat.append(data['users'][n]['chatId'])

    cnt = len(listIdChat)
    text = '#Массовое_сообщение от ' + surname + ' ' + name + ': \n ' + message.text;
    for n in range(cnt):
        bot.send_message(listIdChat[n], text);


def individual_message(message):
    
    data = {}
    data['users'] = []
    global mas
    global individual_message_text 
    mas['students'] = []
    individual_message_text = message.text;

    with open(r'/Users/igorzaharov/Desktop/botTelegram/studentList.json', 'r', encoding='utf-8') as inputfile:
        data = json.load(inputfile)

    k = 1

    for n in range(len(data['users'])): # оставляем только студентов и нужную инфу по ним
        if data['users'][n]['typeusers'] == 'student':
            mas['students'].append({
                "number": k,
                "name": data['users'][n]['name'],
                "surname": data['users'][n]['surname'],
                "chatId": data['users'][n]['chatId']
            }) 
            k+=1


    for n in range(len(mas['students'])): # отправляем студентов учителю
        text = str(mas['students'][n]['number']) + ". " + str(mas['students'][n]['name']) + " " +str(mas['students'][n]['surname'])
        bot.send_message(message.from_user.id, text)

    bot.send_message(message.from_user.id, 'введите в одну строку номера получателей через пробел');
    bot.register_next_step_handler(message, individual_message_send);

def individual_message_send(message):
    global mas
    global individual_message_text 

    s = message.text  # ожидаем от учителя строку 
    index = len(s) - 1
    
    while index >= 0:
        if s[index] != " " :
            z = int(s[index]) - 1
            bot.send_message(mas['students'][z]['chatId'], individual_message_text); # рассылаем сообщения
        index = index - 1
    mas.clear()



@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global typeusers;
    if call.data == "student":  # call.data это callback_data, которую мы указали при объявлении кнопки
        typeusers = 'student';
        bot.send_message(call.message.chat.id, 'Отлично! Пройди авторизацию. ');
        bot.send_message(call.message.chat.id, 'Как твоё имя?');
        bot.register_next_step_handler(call.message, get_name);
    elif call.data == "teacher":
        typeusers = 'teacher';
        bot.send_message(call.message.chat.id, 'Отлично! Пройди авторизацию. Как твоё имя?');
        bot.register_next_step_handler(call.message, get_name);

    if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
        # добавить в список пользователей
        create_user()
        bot.send_message(call.message.chat.id,
                         'Отлично! Можешь пользоваться мной. Посмотри доступные функции в меню, либо написав /func');
        bot.register_next_step_handler(call.message, start_way);

    elif call.data == "no":
        bot.send_message(call.message.chat.id,
                         'Плохо, пройди регистрацию заново или попроси админа внести тебя в список класса. Введи своё имя');
        bot.register_next_step_handler(call.message, get_name);


bot.polling(none_stop=True, interval=0)