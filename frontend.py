#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
from telebot import types
#####################################


class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=2)

    def start_buttons(self):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        product_catalog = types.InlineKeyboardButton('Пройти тест', callback_data='start', parse_mode='html')
        keyboard.add(product_catalog)
        return keyboard

    def questions(self, data):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for index, i in enumerate(data):
            product_catalog = types.InlineKeyboardButton(i[0], callback_data=f'question{index}', parse_mode='html')
            keyboard.add(product_catalog)
        return keyboard

    def reg_btns(self):
        reg = types.InlineKeyboardButton('Зарегестрироваться', callback_data='reg')
        self.__markup.add(reg)
        return self.__markup

    def email_btns(self):
        y = types.InlineKeyboardButton('Да!', callback_data='y')
        n = types.InlineKeyboardButton('Нет!', callback_data='n')
        self.__markup.add(y, n)
        return self.__markup

    def question_btns(self):
        f = types.InlineKeyboardButton('Работаю по найму', callback_data='question0')
        s = types.InlineKeyboardButton('Являюсь самозанятым, ИП или основателем ООО (АО)', callback_data='question1')
        t = types.InlineKeyboardButton('Не работаю, получаю социальные пособия', callback_data='question2')
        o = types.InlineKeyboardButton('Я пенсионер', callback_data='question3')
        k = types.InlineKeyboardButton('Я учусь', callback_data='question4')
        self.__markup.add(f, s, t, o, k)
        return self.__markup

    def second_question(self):
        f = types.InlineKeyboardButton('У меня низкий доход', callback_data='vopros0')
        s = types.InlineKeyboardButton('Я ищу партнеров для совместных проектов', callback_data='vopros1')
        t = types.InlineKeyboardButton('Я инвестор, могу приобретать активы', callback_data='vopros2')
        self.__markup.add(f, s, t)
        return self.__markup