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
        reg = types.InlineKeyboardButton('Зарегистрироваться', callback_data='reg')
        self.__markup.add(reg)
        return self.__markup

    def admin_btns(self):
        reg = types.InlineKeyboardButton('Добавить группу', callback_data='add_group')
        self.__markup.add(reg)
        return self.__markup

    def group_btn(self, bot_link):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        reg = types.InlineKeyboardButton('Регистрация подписчика', url=bot_link)
        keyboard.add(reg)
        return keyboard

    def email_btns(self):
        y = types.InlineKeyboardButton('Да!', callback_data='y')
        n = types.InlineKeyboardButton('Нет!', callback_data='n')
        self.__markup.add(y, n)
        return self.__markup

    def back_in_profile(self):
        a = types.InlineKeyboardButton('вернуться назад', callback_data='profile_back')
        self.__markup.add(a)
        return self.__markup

    def cancel_write_to_admin(self):
        a = types.InlineKeyboardButton('Отмена', callback_data='write_back')
        self.__markup.add(a)
        return self.__markup

    def profile_btns(self):
        a = types.InlineKeyboardButton('Мои ответы', callback_data='profile1')
        b = types.InlineKeyboardButton('Связь с администрацией', callback_data='profile2')
        c = types.InlineKeyboardButton('Добавить соц. сеть', callback_data='profile3')
        d = types.InlineKeyboardButton('Мои заявки', callback_data='profile4')
        self.__markup.add(a, b, c, d)
        return self.__markup

    def social_networks(self):
        a = types.InlineKeyboardButton('Вконтакте', callback_data='social_networksВконтакте')
        b = types.InlineKeyboardButton('Телеграмм', callback_data='social_networksТелеграмм')
        c = types.InlineKeyboardButton('Одноклассники', callback_data='social_networksОдноклассники')
        d = types.InlineKeyboardButton('Тенчат', callback_data='social_networksТенчат')
        self.__markup.add(a, b, c, d)
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