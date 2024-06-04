#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
from amocrm.v2 import tokens, Lead as _Lead, custom_field
import sys
import os
import json
#####################################


class TempUserData:
    def __init__(self):
        super(TempUserData, self).__init__()
        self.__user_data = {}

    def temp_data(self, user_id):
        if user_id not in self.__user_data.keys():
            self.__user_data.update({user_id: [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]}) #3/0 - никнейм, 4 - капча, 5 - адрес емэйл, 6 - код отправленный на емэйл, 7 - bs64 аватарка, 8 - пароль, 9 - день рождения, 10 - город проживания
        return self.__user_data


class AmoCrmLead(_Lead):
    tg_id = custom_field.NumericCustomField("tg_id")
    telegram_contact = custom_field.TextCustomField("telegram_contact")
    user_fio = custom_field.DateCustomField("user_fio")
    user_birthdate = custom_field.TextCustomField("user_birthdate")
    user_email = custom_field.TextCustomField("user_email")
    user_city = custom_field.TextCustomField("user_city")
    user_nick = custom_field.TextCustomField("user_nick")
    user_password = custom_field.TextCustomField("user_password")
    user_photo = custom_field.TextCustomField("user_photo")
    user_employment = custom_field.TextCustomField("user_employment")
    user_category = custom_field.TextCustomField("user_category")
    user_social_problem = custom_field.TextCustomField("user_social_problem")
    user_environmental_problem = custom_field.TextCustomField("user_environmental_problem")


class DbAct:
    def __init__(self, config):
        super(DbAct, self).__init__()
        # self.__db = db
        self.__config = config
        self.init()

    def init(self):
        tokens.default_token_manager(
            client_id=self.__config.get_config()['amocrm_client_id'],
            client_secret=self.__config.get_config()['amocrm_client_secret'],
            subdomain=self.__config.get_config()['amocrm_subdomain'],
            redirect_url=self.__config.get_config()['amocrm_redirect_url'],
            storage=tokens.FileTokensStorage(directory_path='./amocrm_tokens'),  # by default FileTokensStorage
        )

    def user_is_existed(self, user_id):
        temp = list()
        users = AmoCrmLead.objects.all()
        for i in users:
            temp.append(i.tg_id)
        if user_id in temp:
            return True

    def send_email(self):
        pass

    def generate_tokens(self):
        tokens.default_token_manager.init(code=self.__config.get_config()['amocrm_temp_code'], skip_error=True)
        sys.exit("Token's succsessfully generated")

    def add_user(self, tg_id, tg_contact, user_photo, data):
        lead = AmoCrmLead.objects.create()
        lead.name = data[3]
        lead.tg_id = tg_id
        lead.telegram_contact = tg_contact
        lead.user_fio = data[3]
        lead.user_email = data[6]
        lead.user_birthdate = data[4]
        lead.user_city = data[5]
        lead.user_nick = data[0]
        lead.user_password = data[1]
        lead.user_photo = user_photo
        lead.user_employment = data[7]
        lead.user_category = data[8]
        lead.user_social_problem = data[9]
        lead.user_environmental_problem = data[10]
        lead.save()

    # def add_user(self, user_id, first_name, last_name, nick_name):
    #     if not self.user_is_existed(user_id):
    #         if user_id in self.__config.get_config()['admins']:
    #             is_admin = True
    #         else:
    #             is_admin = False
    #         self.__db.db_write('INSERT INTO users (user_id, first_name, last_name, nick_name, is_admin) VALUES (?, ?, ?, ?, ?)', (user_id, first_name, last_name, nick_name, is_admin))
    #
    # def user_is_existed(self, user_id):
    #     data = self.__db.db_read('SELECT count(*) FROM users WHERE user_id = ?', (user_id, ))
    #     if len(data) > 0:
    #         if data[0][0] > 0:
    #             status = True
    #         else:
    #             status = False
    #         return status
    #
    # def user_is_admin(self, user_id):
    #     data = self.__db.db_read('SELECT is_admin FROM users WHERE user_id = ?', (user_id, ))
    #     if len(data) > 0:
    #         if data[0][0] == 1:
    #             status = True
    #         else:
    #             status = False
    #         return status
    #
    # def check_statistic_existed(self, user_id):
    #     data = self.__db.db_read('SELECT COUNT(*) FROM statistic WHERE user_id = ?', (user_id, ))
    #     if len(data[0]) > 0:
    #         if data[0][0] > 0:
    #             return True
    #
    # def write_statistic(self, balls, user_id):
    #     if self.check_statistic_existed(user_id):
    #         self.__db.db_write('UPDATE statistic SET balls = ? WHERE user_id = ?', (balls, user_id))
    #     else:
    #         self.__db.db_write('INSERT INTO statistic (user_id, balls) VALUES(?, ?)', (balls, user_id))
