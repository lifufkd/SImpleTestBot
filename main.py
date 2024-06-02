#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import smtplib
import base64
import platform
import telebot
import copy
import random
from datetime import datetime
from email.mime.text import MIMEText
from captcha.image import ImageCaptcha
from random import choice
from threading import Lock
from backend import TempUserData, DbAct
from config_parser import ConfigParser
from db import DB
from frontend import Bot_inline_btns

#####################################
config_name = 'secrets.json'
questions_name = 'questions.json'


#####################################


def get_random_question(user_id):
    temp = list()
    for i in config.get_questions().keys():
        if i not in temp_user_data.temp_data(user_id)[user_id][1]:
            temp.append(i)
    random_question = random.choice(temp)
    temp_user_data.temp_data(user_id)[user_id][1].append(random_question)


def get_answers(question):
    return config.get_questions()[question]


def check_end(user_id):
    if len(config.get_questions().values()) <= len(temp_user_data.temp_data(user_id)[user_id][1]):
        return True


def clener(user_id):
    print('123')
    temp_user_data.temp_data(user_id)[user_id][1] = copy.deepcopy([])
    temp_user_data.temp_data(user_id)[user_id][2] = 0


def next_question(user_id):
    buttons = Bot_inline_btns()
    get_random_question(user_id)
    bot.send_message(user_id, temp_user_data.temp_data(user_id)[user_id][1][-1],
                     reply_markup=buttons.questions(get_answers(temp_user_data.temp_data(user_id)[user_id][1][-1])),
                     parse_mode='html')


def generate_captcha(user_id):
    alphavet = ['1', '2', '3', '4', '5', '6', '7', '8', 'a', 'b', 'd', 'e', 'g', 'h', 'i', 'j', 'n', 'q', 't', 'y', 'A',
                'D',
                'E', 'F', 'G', 'M', 'N', 'P', 'Q', 'R']
    pattern = str()
    for i in range(5):
        pattern += choice(alphavet)
    print(pattern)
    temp_user_data.temp_data(user_id)[user_id][0] = 4
    temp_user_data.temp_data(user_id)[user_id][4] = pattern

    image_captcha = ImageCaptcha(width=300, height=200)
    image_captcha.write(pattern, 'captcha.png')


def bot_captcha(user_id):
    generate_captcha(user_id)
    captcha_img = open('captcha.png', 'rb')
    bot.send_photo(user_id, captcha_img, 'Подтверди капчу:')
    temp_user_data.temp_data(user_id)[user_id][0] = 6


def send_email(user_id):
    sender = config.get_config()['email_login']
    password = config.get_config()['email_pass']
    code_in_msg = str(random.randint(a=111111, b=999999))
    temp_user_data.temp_data(user_id)[user_id][6] = code_in_msg
    message = str(f'Ваш код подтверждения: {code_in_msg}')
    msg = MIMEText(message)
    email = temp_user_data.temp_data(user_id)[user_id][5]
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    try:
        server.login(sender, password)
        server.sendmail(sender, email, msg.as_string())
        return True
    except Exception as _ex:
        return False


def check_day_birthday(user_id, user_input):
    try:
        datetime.strptime(user_input, '%d.%m.%Y')
        bot.send_message(user_id, 'День рождения подтвержден')
        temp_user_data.temp_data(user_id)[user_id][9] = user_input
    except Exception as e:
        print(e)
        temp_user_data.temp_data(user_id)[user_id][0] = 8
        bot.send_message(user_id, 'Неправильный ввод!')


def main():
    @bot.message_handler(commands=['start'])
    def start_message(message):
        command = message.text.replace('/', '')
        user_id = message.chat.id
        db_actions.add_user(user_id, message.from_user.first_name, message.from_user.last_name,
                            f'@{message.from_user.username}')
        buttons = Bot_inline_btns()
        if command == 'start':
            bot.send_message(user_id, 'Для начала Вам необходимо зарегестрироваться в боте!⬇️⬇️⬇️',
                             reply_markup=buttons.reg_btns())
            # bot.send_message(user_id, 'Пройти тест', reply_markup=buttons.start_buttons(), parse_mode='html')

    @bot.message_handler(content_types=['text', 'photo'])
    def messages(message):
        user_id = message.chat.id
        buttons = Bot_inline_btns()
        user_input = message.text
        user_photo = message.photo
        code = temp_user_data.temp_data(user_id)[user_id][0]
        if db_actions.user_is_existed(user_id):
            match code:
                case 4:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][3][0] = user_input
                        bot.send_message(user_id, 'Отправьте вашу аватарку')
                        temp_user_data.temp_data(user_id)[user_id][0] = 5
                    else:
                        bot.send_message(user_id, 'Не вверный ввод')
                case 5:
                    if user_photo is not None:
                        photo_id = user_photo[-1].file_id
                        photo_file = bot.get_file(photo_id)
                        photo_to_bs64 = base64.b64encode(bot.download_file(photo_file.file_path)).decode('latin1')
                        temp_user_data.temp_data(user_id)[user_id][7] = photo_to_bs64
                        bot.send_message(user_id, 'Аватарка успешно загружена')
                        bot_captcha(user_id)
                    else:
                        bot.send_message(user_id, 'Это не фотография')
                case 6:
                    if user_input == temp_user_data.temp_data(user_id)[user_id][4]:
                        bot.send_message(user_id, 'Вы подтвердили капчу')
                        bot.send_message(user_id, 'Придумайте пароль')
                        temp_user_data.temp_data(user_id)[user_id][0] = 7
                    else:
                        bot.send_message(user_id, 'Капча не подтверждена')
                        bot_captcha(user_id)
                case 7:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][8] = user_input
                        bot.send_message(user_id, 'Введите ФИО')
                        temp_user_data.temp_data(user_id)[user_id][0] = 8
                    else:
                        bot.send_message(user_id, 'Не вверный ввод')
                case 8:
                    if user_input is not None:
                        bot.send_message(user_id, 'Введите дату рождения (в формате дд.мм.гггг (12.12.2012))')
                        temp_user_data.temp_data(user_id)[user_id][0] = 9
                    else:
                        bot.send_message(user_id, 'Не вверный ввод')
                case 9:
                    if user_input is not None:
                        check_day_birthday(user_id, user_input)
                        bot.send_message(user_id, 'Введите город проживания')
                        temp_user_data.temp_data(user_id)[user_id][0] = 10
                    else:
                        bot.send_message(user_id, 'Не вверный ввод')
                case 10:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][10] = user_input
                        bot.send_message(user_id, 'Введите E-mail')
                        temp_user_data.temp_data(user_id)[user_id][0] = 11
                    else:
                        bot.send_message(user_id, 'Не вверный ввод')
                case 11:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][5] = user_input
                        if send_email(user_id):
                            temp_user_data.temp_data(user_id)[user_id][0] = 12
                            bot.send_message(user_id, 'Введите код подтвержения с вашей почты')
                        else:
                            temp_user_data.temp_data(user_id)[user_id][0] = 10
                            bot.send_message(user_id, 'Не вверный ввод ')
                    else:
                        bot.send_message(user_id, 'Не вверный ввод')
                case 12:
                    if user_input == temp_user_data.temp_data(user_id)[user_id][6]:
                        bot.send_message(user_id, 'Вы успешно зарегестировались!')
                    else:
                        bot.send_message(user_id, 'Код не верный, попробуйте еще раз!\n\n'
                                                  'Вы хотите поменять адрес почты?', reply_markup=buttons.email_btns())

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        command = call.data
        user_id = call.message.chat.id
        buttons = Bot_inline_btns()
        if db_actions.user_is_existed(user_id):
            if command == 'start':
                print('123')
                clener(user_id)
                next_question(user_id)
            elif command[:8] == 'question':
                answers_stat = list()
                data = get_answers(temp_user_data.temp_data(user_id)[user_id][1][-1])
                for i in data:
                    answers_stat.append(i[2])
                if answers_stat[int(command[8:])]:
                    temp_user_data.temp_data(user_id)[user_id][2] += 1
                    bot.send_message(user_id, f'Правильный ответ!!!\n\n{data[int(command[8:])][1]}', parse_mode='html')
                else:
                    bot.send_message(user_id, f'Неправильный ответ\n\n{data[int(command[8:])][1]}', parse_mode='html')
                if check_end(user_id):
                    db_actions.write_statistic(temp_user_data.temp_data(user_id)[user_id][2], user_id)
                    clener(user_id)
                    bot.send_message(user_id, 'Пройти ещё раз', reply_markup=buttons.start_buttons(), parse_mode='html')
                else:
                    next_question(user_id)
            elif command == 'reg':
                bot.send_message(user_id, 'Введите свой никнейм')
                temp_user_data.temp_data(user_id)[user_id][0] = 4
            elif command == 'y':
                bot.send_message(user_id, 'Введите E-mail')
                temp_user_data.temp_data(user_id)[user_id][0] = 11
            elif command == 'n':
                send_email(user_id)
                bot.send_message(user_id, 'Введите код подтвержения с вашей почты')

    bot.polling(none_stop=True)


if '__main__' == __name__:
    os_type = platform.system()
    config = ConfigParser(config_name, questions_name)
    temp_user_data = TempUserData()
    db = DB(config.get_config()['db_file_name'], Lock())
    db_actions = DbAct(db, config)
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()
