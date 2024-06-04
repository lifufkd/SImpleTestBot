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
#####################################


def generate_captcha(user_id):
    alphavet = ['1', '2', '3', '4', '5', '6', '7', '8', 'a', 'b', 'd', 'e', 'g', 'h', 'i', 'j', 'n', 'q', 't', 'y', 'A',
                'D',
                'E', 'F', 'G', 'M', 'N', 'P', 'Q', 'R']
    pattern = str()
    for i in range(5):
        pattern += choice(alphavet)
    print(pattern)
    temp_user_data.temp_data(user_id)[user_id][1] = pattern
    image_captcha = ImageCaptcha(width=300, height=200)
    image_captcha.write(pattern, 'captcha.png')


def bot_captcha(user_id):
    generate_captcha(user_id)
    captcha_img = open('captcha.png', 'rb')
    bot.send_photo(user_id, captcha_img, 'Подтверди капчу:')
    temp_user_data.temp_data(user_id)[user_id][0] = 3


def send_email(user_id):
    sender = config.get_config()['email_login']
    password = config.get_config()['email_pass']
    code_in_msg = str(random.randint(a=111111, b=999999))
    temp_user_data.temp_data(user_id)[user_id][2] = code_in_msg
    message = str(f'Ваш код подтверждения: {code_in_msg}')
    msg = MIMEText(message)
    email = temp_user_data.temp_data(user_id)[user_id][10]
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    try:
        server.login(sender, password)
        server.sendmail(sender, email, msg.as_string())
        return True
    except Exception as _ex:
        return False


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
                case 0:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][4] = user_input
                        bot.send_message(user_id, 'Придумайте пароль')
                        temp_user_data.temp_data(user_id)[user_id][0] = 1
                    else:
                        bot.send_message(user_id, 'Это не текст! Попробуйте ещё раз')
                case 1:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][5] = user_input
                        bot.send_message(user_id, 'Выберите аватарку')
                        temp_user_data.temp_data(user_id)[user_id][0] = 2
                    else:
                        bot.send_message(user_id, 'Это не текст! Попробуйте ещё раз')
                case 2:
                    if user_photo is not None:
                        photo_id = user_photo[-1].file_id
                        photo_file = bot.get_file(photo_id)
                        photo_to_bs64 = base64.b64encode(bot.download_file(photo_file.file_path)).decode('latin1')
                        temp_user_data.temp_data(user_id)[user_id][6] = photo_to_bs64
                        bot_captcha(user_id)
                    else:
                        bot.send_message(user_id, 'Это не фотография! Попробуйте ещё раз')
                case 3:
                    if user_input == temp_user_data.temp_data(user_id)[user_id][1]:
                        bot.send_message(user_id, 'Введите ФИО')
                        temp_user_data.temp_data(user_id)[user_id][0] = 4
                    else:
                        bot.send_message(user_id, 'Капча не подтверждена')
                        bot_captcha(user_id)
                case 4:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][7] = user_input
                        bot.send_message(user_id, 'Введите дату рождения (в формате дд.мм.гггг (12.12.2012))')
                        temp_user_data.temp_data(user_id)[user_id][0] = 5
                    else:
                        bot.send_message(user_id, 'Это не текст! Попробуйте ещё раз')
                case 5:
                    if user_input is not None:
                        try:
                            temp_user_data.temp_data(user_id)[user_id][8] = datetime.strptime(user_input, '%d.%m.%Y')
                            temp_user_data.temp_data(user_id)[user_id][0] = 6
                            bot.send_message(user_id, 'Введите город проживания')
                        except:
                            bot.send_message(user_id, 'Дата указана в неправильном формате! Попробуйте ещё раз')
                    else:
                        bot.send_message(user_id, 'Это не текст! Попробуйте ещё раз')
                case 6:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][9] = user_input
                        temp_user_data.temp_data(user_id)[user_id][0] = 7
                        bot.send_message(user_id, 'Введите E-mail')
                    else:
                        bot.send_message(user_id, 'Это не текст! Попробуйте ещё раз')
                case 7:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][10] = user_input
                        if send_email(user_id):
                            temp_user_data.temp_data(user_id)[user_id][0] = 8
                            bot.send_message(user_id, 'Введите код подтверждения с вашей почты')
                        else:
                            bot.send_message(user_id, 'Произошла ошибка. Введите адрес почты ещё раз')
                    else:
                        bot.send_message(user_id, 'Это не текст! Попробуйте ещё раз')
                case 8:
                    if user_input == temp_user_data.temp_data(user_id)[user_id][2]:
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
            if command == 'reg':
                temp_user_data.temp_data(user_id)[user_id][0] = 0
                bot.send_message(user_id, 'Введите свой никнейм')
            elif command == 'y':
                temp_user_data.temp_data(user_id)[user_id][0] = 7
                bot.send_message(user_id, 'Введите E-mail')
            elif command == 'n':
                send_email(user_id)
                bot.send_message(user_id, 'Введите код подтвержения с вашей почты')

    bot.polling(none_stop=True)


if '__main__' == __name__:
    os_type = platform.system()
    config = ConfigParser(config_name)
    temp_user_data = TempUserData()
    # db = DB(config.get_config()['db_file_name'], Lock())
    db_actions = DbAct(config)
    if config.get_config()['generate_token']:
        db_actions.generate_tokens()
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()
