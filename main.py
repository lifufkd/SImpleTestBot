#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import json
import smtplib
import base64
import platform
import telebot
import requests
import threading
import random
import schedule
import time
from datetime import datetime, timedelta, timezone
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


def upload_image_to_imgur(image_base64, client_id):
    url = "https://api.imgur.com/3/upload"
    headers = {
        "Authorization": f"Client-ID {client_id}"
    }
    data = {
        "image": base64.b64decode(image_base64),
        "type": "file"
    }
    response = requests.post(url, headers=headers, files=data)

    if response.status_code == 200:
        response_data = response.json()
        return response_data["data"]["link"]
    else:
        raise Exception(f"Failed to upload image: {response.status_code} {response.text}")


def generate_captcha(user_id):
    alphavet = ['1', '2', '3', '4', '5', '6', '7', '8', 'a', 'b', 'd', 'e', 'g', 'h', 'i', 'j', 'n', 'q', 't', 'y', 'A',
                'D',
                'E', 'F', 'G', 'M', 'N', 'P', 'Q', 'R']
    pattern = str()
    for i in range(5):
        pattern += choice(alphavet)
    temp_user_data.temp_data(user_id)[user_id][1] = pattern
    image_captcha = ImageCaptcha(width=300, height=200)
    image_captcha.write(pattern, 'captcha.png')


def bot_captcha(user_id):
    generate_captcha(user_id)
    captcha_img = open('captcha.png', 'rb')
    bot.send_photo(user_id, captcha_img, 'Подтверди капчу:')
    temp_user_data.temp_data(user_id)[user_id][0] = 3


def post_windshield(user_id):
    buttons = Bot_inline_btns()
    ids = list()
    text = split_text_by_period(config.get_config()['group_text'])
    ids.append(bot.send_photo(chat_id=user_id, photo=open('WOND.jpg', 'rb'),
                              caption=text[0]).message_id)
    if len(text) > 1:
        for index, i in enumerate(text[1:]):
            if index + 2 != len(text):
                ids.append(bot.send_message(chat_id=user_id, text=i).message_id)
            else:
                ids.append(bot.send_message(chat_id=user_id, text=i, reply_markup=buttons.group_btn(
                    config.get_config()['bot_link'])).message_id)
    return [user_id, ids]


def task():
    for i in db_actions.get_groups():
        try:
            for g in json.loads(i[1]):
                bot.delete_message(chat_id=i[0], message_id=g)
        except:
            pass
        data = post_windshield(i[0])
        db_actions.update_group(data[0], data[1])


def job(utc_offset):
    # Получение текущего времени в указанном часовом поясе
    tz = timezone(timedelta(hours=utc_offset))
    current_time = datetime.now(tz)

    # Проверка, если текущее время 00:00
    if current_time.hour == 0 and current_time.minute == 0:
        task()


def schedule_job(utc_offset):
    tz = timezone(timedelta(hours=utc_offset))
    now = datetime.now(tz)
    next_run = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Если текущее время уже прошло 00:00, планируем задачу на следующий день
    if now >= next_run:
        next_run += timedelta(days=1)

    delay = (next_run - now).total_seconds()

    # Запуск функции через указанное количество секунд
    schedule.every(int(delay)).seconds.do(job, utc_offset)


def add_airdrop_wond():
    data = db_actions.get_all_application()
    for i in data:
        date_now = datetime.today()
        date_client = datetime.strptime(i[2], '%Y-%m-%d %H:%M')
        if date_client + timedelta(days=30) <= date_now:
            db_actions.update_date_airdrop_wond(date_now, i[0])
            db_actions.update_balance(3, i[0])
            try:
                bot.send_message(i[0], f'{i[1]}!\nНа ваш баланс добавлено {float(3)} airdrop WOND')
            except:
                pass


def runner():
    while True:
        schedule.run_pending()
        add_airdrop_wond()
        time.sleep(1)


def profile(user_id):
    s = str()
    buttons = Bot_inline_btns()
    social_networks = db_actions.get_social_networks(user_id)
    user_info = db_actions.get_user_info(user_id)
    application = db_actions.get_application_by_user_id(user_id)
    print(social_networks, user_info, application)
    for name, value in social_networks.items():
        s += f'{name} - {value}\n'
    bot.send_message(user_id, f'Добро пожаловать <b>{application[3]}</b>!\n\n'
                              f'Ваш ID: <b>{user_id}</b>\n\n'
                              f'Ваш баланс: <b>{user_info[0]}</b> токенов\n\n'
                              f'Ваш логин: <b>{application[1]}</b>\n\n'
                              f'Ваш пароль: <b>{application[2]}</b>\n\n'
                              f'Ваши соц. сети:\n\n{s}', parse_mode='html',
                     reply_markup=buttons.profile_btns())


def delete_last_message(user_id):
    bot.delete_message(user_id, temp_user_data.temp_data(user_id)[user_id][3][-1])
    temp_user_data.temp_data(user_id)[user_id][3] = temp_user_data.temp_data(user_id)[user_id][3][:-1]


def send_email(user_id):
    sender = config.get_config()['email_login']
    password = config.get_config()['email_pass']
    code_in_msg = str(random.randint(a=111111, b=999999))
    temp_user_data.temp_data(user_id)[user_id][2] = code_in_msg
    message = str(f'Ваш код подтверждения: {code_in_msg}')
    msg = MIMEText(message)
    email = temp_user_data.temp_data(user_id)[user_id][10]
    try:
        server = smtplib.SMTP_SSL("smtp.mail.ru", 465)
        server.login(sender, password)
        server.sendmail(sender, email, msg.as_string())
        return True
    except:
        return False


def send_email_to_admin(user_nickname, user_input):
    sender = config.get_config()['email_login']
    password = config.get_config()['email_pass']
    dest = config.get_config()['email_for_applications']
    message = str(f'Пользователь @{user_nickname} оставил заявку!\n{user_input}')
    msg = MIMEText(message)
    try:
        server = smtplib.SMTP_SSL("smtp.mail.ru", 465)
        server.login(sender, password)
        server.sendmail(sender, dest, msg.as_string())
        return True
    except Exception as e:
        print(e)
        return False


def split_text_by_period(text, max_length=1024):
    """
    Разделяет текст на части, каждая из которых не превышает max_length символов, разделяя текст только по точкам.

    :param text: str, исходный текст
    :param max_length: int, максимальная длина части текста
    :return: list, список частей текста
    """
    if len(text) <= max_length:
        return [text]

    parts = []
    current_part = []

    for sentence in text.split('.'):
        sentence = sentence.strip() + '.'
        if len(' '.join(current_part) + sentence) > max_length:
            parts.append(' '.join(current_part).strip())
            current_part = [sentence.strip()]
        else:
            current_part.append(sentence.strip())

    # Добавляем последнюю часть, если она не пустая
    if current_part:
        parts.append(' '.join(current_part).strip())

    # Убираем последний символ '.' у последнего элемента списка
    if parts and parts[-1].endswith('.'):
        parts[-1] = parts[-1][:-1]

    return parts


def add_chanel(user_id, chat_id, text, text1):
    if not db_actions.group_already_added(user_id):
        data = post_windshield(user_id)
        db_actions.add_group(data)
        temp_user_data.temp_data(chat_id)[chat_id][0] = None
        bot.send_message(chat_id,
                         text)
    else:
        bot.send_message(chat_id, text1)


def main():
    @bot.message_handler(commands=['start', 'admin', 'connect', 'profile', 'get_db', 'load_db'])
    def start_message(message):
        command = message.text.replace('/', '')
        user_id = message.chat.id
        chat_id = message.from_user.id
        buttons = Bot_inline_btns()
        db_actions.add_user_local(chat_id, message.from_user.first_name, message.from_user.last_name,
                            f'@{message.from_user.username}')
        if db_actions.user_is_existed_local(chat_id) or db_actions.user_is_existed_local(chat_id):
            if db_actions.user_is_admin_local(chat_id):
                if command == 'connect':
                    add_chanel(user_id, chat_id, 'Группа успешно добавлена, витрина с ботом будет перемещаться ежедневно в 00:00 по МСК', 'Группа уже добавлена!')
                elif command == 'admin':
                    bot.send_message(chat_id, 'Выберите действие', reply_markup=buttons.admin_btns())
                elif command == 'get_db':
                    bot.send_document(chat_id, open(config.get_config()['db_file_name'], 'rb'))
                elif command == 'load_db':
                    temp_user_data.temp_data(chat_id)[chat_id][0] = 17
                    bot.send_message(chat_id, 'Отправьте файл с БД')
            if db_actions.user_id_registered(chat_id):
                if command == 'start':
                    bot.send_message(chat_id, 'Добро пожаловать в чат-бот опроса подписчиков - граждан России!\n\n'
                                              'Честные, реальные ответы на вопросы чат-бота дают подписчикам права на:\n\n'
                                              '1. Сотрудничество в ReFi проекте для роста своих доходов, улучшения уровня жизни, исправления социального неравенства.\n\n'
                                              '2. Ежемесячное получение и накопление системных ценных токенов в своих личных кабинетах.\n\n'
                                              '3. Совместную с партнерами и инвесторами конвертацию и продажу полученных цифровых активов.\n\n'
                                              '4. Направление выручки от продажи токенов на решение заявленных социальных, экологических, финансовых и иных проблем подписчиков.\n\n'
                                              '5. Коллективные инвестиции в свои региональные проекты и в программы развития экономики России.\n\n'
                                              '6. Создание общей децентрализованной экосистемы учета, управления и роста активов и капиталов подписчиков.\n\n'
                                              '7. Обеспечение постоянной и массовой благотворительной поддержки нуждающихся граждан России.')
                elif command == 'profile':
                    if temp_user_data.temp_data(chat_id)[chat_id][17]:
                        profile(chat_id)
                    else:
                        temp_user_data.temp_data(chat_id)[chat_id][0] = 15
                        bot.send_message(chat_id, 'Введите логин')
            else:
                if command == 'start':
                    bot.send_message(chat_id, 'Добро пожаловать в чат-бот опроса подписчиков - граждан России!\n\n'
                                              'Честные, реальные ответы на вопросы чат-бота дают подписчикам права на:\n\n'
                                              '1. Сотрудничество в ReFi проекте для роста своих доходов, улучшения уровня жизни, исправления социального неравенства.\n\n'
                                              '2. Ежемесячное получение и накопление системных ценных токенов в своих личных кабинетах.\n\n'
                                              '3. Совместную с партнерами и инвесторами конвертацию и продажу полученных цифровых активов.\n\n'
                                              '4. Направление выручки от продажи токенов на решение заявленных социальных, экологических, финансовых и иных проблем подписчиков.\n\n'
                                              '5. Коллективные инвестиции в свои региональные проекты и в программы развития экономики России.\n\n'
                                              '6. Создание общей децентрализованной экосистемы учета, управления и роста активов и капиталов подписчиков.\n\n'
                                              '7. Обеспечение постоянной и массовой благотворительной поддержки нуждающихся граждан России.', reply_markup=buttons.reg_btns())

    @bot.message_handler(content_types=['text', 'photo', 'document'])
    def messages(message):
        user_id = message.from_user.id
        document = message.document
        user_nickname = message.from_user.username
        buttons = Bot_inline_btns()
        user_input = message.text
        user_photo = message.photo
        code = temp_user_data.temp_data(user_id)[user_id][0]
        if db_actions.user_is_existed_local(user_id):
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
                            datetime.strptime(user_input, '%d.%m.%Y').date()
                            temp_user_data.temp_data(user_id)[user_id][8] = user_input
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
                        bot.send_message(user_id, 'Введите вашу дейстующую электронную почту')
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
                        bot.send_message(user_id, 'Укажите вашу занятость', reply_markup=buttons.question_btns())
                    else:
                        bot.send_message(user_id, 'Код не верный, попробуйте еще раз!\n\n'
                                                  'Вы хотите поменять адрес почты?', reply_markup=buttons.email_btns())
                case 9:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][13] = user_input
                        temp_user_data.temp_data(user_id)[user_id][0] = 10
                        bot.send_message(user_id, 'Какая наиболее важная экологическая проблема для Вас?')
                    else:
                        bot.send_message(user_id, 'Это не текст! Попробуйте ещё раз')
                case 10:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][14] = user_input
                        temp_user_data.temp_data(user_id)[user_id][0] = 11
                        bot.send_message(user_id, 'Иная наиболее важная проблема для Вас?')
                    else:
                        bot.send_message(user_id, 'Это не текст! Попробуйте ещё раз')
                case 11:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][15] = user_input
                        user_photo = upload_image_to_imgur(temp_user_data.temp_data(user_id)[user_id][6],
                                                                  config.get_config()['imgur_client_id'])
                        db_actions.add_application(user_id, user_nickname, user_photo,
                                            temp_user_data.temp_data(user_id)[user_id][4:])
                        db_actions.add_application_local(user_id, user_photo, temp_user_data.temp_data(user_id)[user_id][4:])
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        bot.send_message(user_id, 'Предварительный опрос завершен, спасибо вам!\n\n'
                                                  'Для роста ваших доходов и решения проблем вы можете участвовать в одном из Телеграм сообществ проекта:\n\n'
                                                  '1. https://t.me/basic_digital_income - при вашем выборе пассивного участия.\n\n'
                                                  '2. https://t.me/wonderful_partners - при вашем выборе активного партнерства предпринимателей.\n\n'
                                                  '3. https://t.me/wonderful_investors - при выборе ваших инвестиций в цифровые активы и криптовалюты.')
                    else:
                        bot.send_message(user_id, 'Это не текст! Попробуйте ещё раз')
                case 12:
                    if user_input is not None:
                        try:
                            add_chanel(int(user_input), user_id,
                                       'Канал успешно добавлен, витрина с ботом будет перемещаться ежедневно в 00:00 по МСК',
                                       'Канал успешно добавлен!')
                        except:
                            temp_user_data.temp_data(user_id)[user_id][0] = None
                            bot.send_message(user_id, 'Бот не состоит в канале с таким ID!')
                    else:
                        bot.send_message(user_id, 'Это не текст! Попробуйте ещё раз')
                case 13:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        admins = db_actions.get_admins()
                        db_actions.add_admin_application(user_id, user_input)
                        send_email_to_admin(user_nickname, user_input)
                        for i in admins:
                            bot.send_message(i, f'Пользователь @{user_nickname} оставил заявку!\n{user_input}')
                        bot.send_message(user_id, 'Ваша заявка отправлена')
                    else:
                        bot.send_message(user_id, 'Это не текст! Попробуйте ещё раз')
                case 14:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        delete_last_message(user_id)
                        db_actions.update_social_networks(user_id, temp_user_data.temp_data(user_id)[user_id][16], user_input)
                        bot.send_message(user_id, 'Соц. сеть успешно добавлена!')
                    else:
                        bot.send_message(user_id, 'Это не текст! Попробуйте ещё раз')
                case 15:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][18][0] = user_input
                        temp_user_data.temp_data(user_id)[user_id][0] = 16
                        bot.send_message(user_id, 'Введите пароль')
                    else:
                        bot.send_message(user_id, 'Это не текст! Попробуйте ещё раз')
                case 16:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][18][1] = user_input
                        temp_user_data.temp_data(user_id)[user_id][17] = True
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        if db_actions.user_is_authorized(temp_user_data.temp_data(user_id)[user_id][18]):
                            profile(user_id)
                        else:
                            bot.send_message(user_id, 'Данные не верны')

                    else:
                        bot.send_message(user_id, 'Это не текст! Попробуйте ещё раз')
                case 17:
                    if document is not None:
                        file_info = bot.get_file(document.file_id)
                        file_name = document.file_name
                        downloaded_file = bot.download_file(file_info.file_path)
                        with open(file_name, 'wb') as new_file:
                            new_file.write(downloaded_file)
                    else:
                        bot.send_message(user_id, 'Это не файл! Попробуйте ещё раз')

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        command = call.data
        user_id = call.message.chat.id
        buttons = Bot_inline_btns()
        if db_actions.user_is_existed_local(user_id):
            if db_actions.user_is_admin_local(user_id):
                if command == 'pre_add_group':
                    bot.send_message(user_id, 'Что вы хотите добавить?', reply_markup=buttons.add_choise_btns())
                if command[:9] == 'add_group':
                    match command[9:]:
                        case '1':
                            bot.send_message(user_id, 'Отправьте из группы команду /connect')
                        case '2':
                            temp_user_data.temp_data(user_id)[user_id][0] = 12
                            bot.send_message(user_id, 'Введите ID канала')
            if db_actions.user_id_registered(user_id):
                if command == 'profile_back':
                    delete_last_message(user_id)
                elif command == 'write_back':
                    temp_user_data.temp_data(user_id)[user_id][0] = None
                    delete_last_message(user_id)
                elif command[:15] == 'social_networks':
                    temp_user_data.temp_data(user_id)[user_id][16] = command[15:]
                    temp_user_data.temp_data(user_id)[user_id][0] = 14
                    message_id = bot.send_message(user_id, f'Введите ссылку на свой профиль в {command[15:]}', reply_markup=buttons.cancel_write_to_admin()).message_id
                    temp_user_data.temp_data(user_id)[user_id][3].append(message_id)
                elif command[:7] == 'profile':
                    match command[7:]:
                        case '1':
                            application = db_actions.get_application_by_user_id(user_id)
                            caption = f'Ваше ФИО: <b>{application[3]}</b>\n\n' \
                                      f'Ваш никнейм: <b>{application[1]}</b>\n\n' \
                                      f'Ваш пароль: <b>{application[2]}</b>\n\n' \
                                      f'Ваша дата рождения: <b>{application[4]}</b>\n\n' \
                                      f'Ваш город проживания: <b>{application[5]}</b>\n\n' \
                                      f'Ваша почта: <b>{application[6]}</b>\n\n' \
                                      f'Ваша занятость: <b>{application[7]}</b>\n\n' \
                                      f'Ваша категория: <b>{application[8]}</b>\n\n' \
                                      f'Ваша наиболее важная социальная проблема: <b>{application[9]}</b>\n\n' \
                                      f'Ваша наиболее важная экологическая проблема: <b>{application[10]}</b>\n\n' \
                                      f'Иная наиболее важная проблема: <b>{application[11]}</b>\n'
                            message_id = bot.send_photo(chat_id=user_id, caption=caption, reply_markup=buttons.back_in_profile(), photo=application[0], parse_mode='html').message_id
                            temp_user_data.temp_data(user_id)[user_id][3].append(message_id)
                        case '2':
                            temp_user_data.temp_data(user_id)[user_id][0] = 13
                            message_id = bot.send_message(user_id, 'Напишите свою заявку администратору', reply_markup=buttons.cancel_write_to_admin()).message_id
                            temp_user_data.temp_data(user_id)[user_id][3].append(message_id)
                        case '3':
                            bot.send_message(user_id, 'Выберите социальную сеть которую хотите добавить: ', reply_markup=buttons.social_networks())
                        case '4':
                            s = str()
                            admin_applications = db_actions.get_admin_application(user_id)
                            for i in admin_applications:
                                if i[2]:
                                    status = 'Закрыта'
                                else:
                                    status = 'Открыта'
                                s += f"{'*'*20}\n" \
                                     f"Время открытия заявки: {i[1]}\n" \
                                     f"Тело заявки: {i[0]}\n" \
                                     f"Статус заявки: {status}\n" \
                                     f"{'*'*20}\n\n"
                            message_id = bot.send_message(user_id, f"Ваши заявки: \n\n{s}", reply_markup=buttons.back_in_profile()).message_id
                            temp_user_data.temp_data(user_id)[user_id][3].append(message_id)

            if command == 'reg':
                temp_user_data.temp_data(user_id)[user_id][0] = 0
                bot.send_message(user_id, 'Введите свой никнейм')
            elif command == 'y':
                temp_user_data.temp_data(user_id)[user_id][0] = 7
                bot.send_message(user_id, 'Введите E-mail')
            elif command == 'n':
                send_email(user_id)
                bot.send_message(user_id, 'Введите код подтвержения с вашей почты')
            elif command[:8] == 'question':
                messages = ['Работаю по найму', 'Являюсь самозанятым, ИП или основателем ООО (АО)', 'Не работаю, получаю социальные пособия', 'Я пенсионер', 'Я учусь']
                temp_user_data.temp_data(user_id)[user_id][11] = messages[int(command[8:])]
                bot.send_message(user_id, 'Установите вашу категорию', reply_markup=buttons.second_question())
            elif command[:6] == 'vopros':
                answers = ['Я малоимущий и пассивный пользователь', 'Мне необходимо активное сотрудничество в группе для совместного роста доходов, улучшения уровня жизни, развития бизнеса и благотворительности', 'Я являюсь инвестором, могу приобретать цифровые финансовые активы у других подписчиков и конвертировать для роста прибыли.']
                temp_user_data.temp_data(user_id)[user_id][12] = answers[int(command[6:])]
                temp_user_data.temp_data(user_id)[user_id][0] = 9
                bot.send_message(user_id, 'Какая наиболее важная социальная проблема для вас?')

    bot.infinity_polling(timeout=10, long_polling_timeout = 5)


if '__main__' == __name__:
    os_type = platform.system()
    config = ConfigParser(config_name)
    temp_user_data = TempUserData()
    db = DB(config.get_config()['db_file_name'], Lock())
    db_actions = DbAct(config, db)
    if config.get_config()['generate_token']:
        db_actions.generate_tokens()
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    schedule_job(config.get_config()['timezone'])
    threading.Thread(target=runner).start()
    main()

