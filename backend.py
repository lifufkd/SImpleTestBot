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
            self.__user_data.update({user_id: [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]}) #3/0 - никнейм, 4 - капча, 5 - адрес емэйл, 6 - код отправленный на емэйл, 7 - bs64 аватарка, 8 - пароль, 9 - день рождения, 10 - город проживания
        return self.__user_data


class AmoCrmLead(_Lead):
    ffff = custom_field.TextCustomField("ffff")
    dddddd = custom_field.TextCustomField("dddddd")


class DbAct:
    def __init__(self, db, config):
        super(DbAct, self).__init__()
        self.__db = db
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

    def send_email(self):
        pass

    def generate_tokens(self):
        tokens.default_token_manager.init(code=self.__config.get_config()['amocrm_temp_code'], skip_error=True)
        sys.exit("Token's succsessfully generated")

    # def add_user(self):
    #     lead = AmoCrmLead.objects.create()
    #     lead.name = 'fwefwefweffwe'
    #     lead.ffff = '123'
    #     lead.dddddd = '321'
    #     lead.save()

    def add_user(self, user_id, first_name, last_name, nick_name):
        if not self.user_is_existed(user_id):
            if user_id in self.__config.get_config()['admins']:
                is_admin = True
            else:
                is_admin = False
            self.__db.db_write('INSERT INTO users (user_id, first_name, last_name, nick_name, is_admin) VALUES (?, ?, ?, ?, ?)', (user_id, first_name, last_name, nick_name, is_admin))

    def user_is_existed(self, user_id):
        data = self.__db.db_read('SELECT count(*) FROM users WHERE user_id = ?', (user_id, ))
        if len(data) > 0:
            if data[0][0] > 0:
                status = True
            else:
                status = False
            return status

    def user_is_admin(self, user_id):
        data = self.__db.db_read('SELECT is_admin FROM users WHERE user_id = ?', (user_id, ))
        if len(data) > 0:
            if data[0][0] == 1:
                status = True
            else:
                status = False
            return status

    def check_statistic_existed(self, user_id):
        data = self.__db.db_read('SELECT COUNT(*) FROM statistic WHERE user_id = ?', (user_id, ))
        if len(data[0]) > 0:
            if data[0][0] > 0:
                return True

    def write_statistic(self, balls, user_id):
        if self.check_statistic_existed(user_id):
            self.__db.db_write('UPDATE statistic SET balls = ? WHERE user_id = ?', (balls, user_id))
        else:
            self.__db.db_write('INSERT INTO statistic (user_id, balls) VALUES(?, ?)', (balls, user_id))
