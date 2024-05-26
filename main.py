#####################################
#            Created by             #
#                SBR                #
#####################################
import platform
import telebot
import copy
import random
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
    temp_user_data.temp_data(user_id)[user_id][1] = copy.deepcopy([])
    temp_user_data.temp_data(user_id)[user_id][2] = 0


def next_question(user_id):
    buttons = Bot_inline_btns()
    get_random_question(user_id)
    bot.send_message(user_id, temp_user_data.temp_data(user_id)[user_id][1][-1],
                     reply_markup=buttons.questions(get_answers(temp_user_data.temp_data(user_id)[user_id][1][-1])), parse_mode='html')


def main():
    @bot.message_handler(commands=['start'])
    def start_message(message):
        command = message.text.replace('/', '')
        user_id = message.chat.id
        db_actions.add_user(user_id, message.from_user.first_name, message.from_user.last_name,
                            f'@{message.from_user.username}')
        buttons = Bot_inline_btns()
        if command == 'start':
            bot.send_message(user_id, 'Пройти тест', reply_markup=buttons.start_buttons(), parse_mode='html')

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        command = call.data
        user_id = call.message.chat.id
        buttons = Bot_inline_btns()
        if db_actions.user_is_existed(user_id):
            if command == 'start':
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

    bot.polling(none_stop=True)


if '__main__' == __name__:
    os_type = platform.system()
    config = ConfigParser(config_name, questions_name)
    temp_user_data = TempUserData()
    db = DB(config.get_config()['db_file_name'], Lock())
    db_actions = DbAct(db, config)
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()
