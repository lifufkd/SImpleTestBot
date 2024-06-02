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
