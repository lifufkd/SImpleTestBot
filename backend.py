#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import json
from datetime import datetime
#####################################


class TempUserData:
    def __init__(self):
        super(TempUserData, self).__init__()
        self.__user_data = {}

    def temp_data(self, user_id):
        if user_id not in self.__user_data.keys():
            self.__user_data.update({user_id: [None, None, None, [], None, None, None, None, None, None, None, None, None, None, None, None, None, None, [None, None], None]}) #3/0 - никнейм, 4 - капча, 5 - адрес емэйл, 6 - код отправленный на емэйл, 7 - bs64 аватарка, 8 - пароль, 9 - день рождения, 10 - город проживания
        return self.__user_data


class DbAct:
    def __init__(self, config, db):
        super(DbAct, self).__init__()
        self.__db = db
        self.__config = config

    def update_groups(self, name, msg_indexes, row_id):
        self.__db.db_write('UPDATE groups SET name = ?, message_id = ? WHERE row_id = ?',
                           (name, json.dumps(msg_indexes), row_id))

    def get_group_index_by_user_id(self, user_id):
        return self.__db.db_read('SELECT `group` FROM users WHERE row_id = ?', (user_id, ))[0][0]

    def get_group_info_by_user_id(self, user_id):
        row_id = self.get_group_index_by_user_id(user_id)
        return self.__db.db_read('SELECT `name`, `group`, `chanel` FROM groups WHERE row_id = ?', (row_id, ))[0]

    def add_group(self, chat_id, is_group):
        if is_group:
            group = True
            chanel = False
        else:
            group = False
            chanel = True
        self.__db.db_write('INSERT INTO groups (chat_id, `group`, chanel) VALUES(?, ?, ?)', (chat_id, group, chanel))
        last_index = int(self.__db.db_read('SELECT MAX(row_id) FROM groups', ())[0][0])
        return last_index

    def group_already_added(self, chat_id):
        out = list()
        data = self.__db.db_read('SELECT chat_id FROM groups', ())
        for i in data:
            out.append(i[0])
        if chat_id in out:
            return True

    def get_groups(self):
        return self.__db.db_read('SELECT chat_id, message_id, row_id FROM groups', ())

    def update_group(self, chat_id, message_id):
        self.__db.db_write('UPDATE groups SET message_id = ? WHERE chat_id = ?', (json.dumps(message_id), chat_id))

    def add_user_local(self, user_id, first_name, last_name, nick_name, group):
        if not self.user_is_existed_local(user_id):
            if user_id in self.__config.get_config()['admins']:
                is_admin = True
            else:
                is_admin = False

            self.__db.db_write('INSERT INTO users (user_id, token_balance, first_name, last_name, nick_name, is_admin, `group`) VALUES (?, ?, ?, ?, ?, ?, ?)', (user_id, 3, first_name, last_name, nick_name, is_admin, group))

    def get_balance(self, user_id):
        return float(self.__db.db_read('SELECT token_balance FROM users WHERE user_id = ?', (user_id, ))[0][0])

    def update_balance(self, balance, user_id):
        old_balance = self.get_balance(user_id)
        self.__db.db_write('UPDATE users SET token_balance = ? WHERE user_id = ?', (float(balance) + old_balance, user_id))
        return float(balance) + old_balance

    def user_is_existed_local(self, user_id):
        data = self.__db.db_read('SELECT count(*) FROM users WHERE user_id = ?', (user_id, ))
        if len(data) > 0:
            if data[0][0] > 0:
                status = True
            else:
                status = False
            return status

    def add_admin_application(self, user_id, content):
        self.__db.db_write('INSERT INTO applications_to_admin (user_id, content, status, time) VALUES(?, ?, ?, ?)', (user_id, content, False, datetime.today().strftime('%Y-%m-%d %H:%M')))

    def get_admin_application(self, user_id):
        return self.__db.db_read('SELECT content, time, status FROM applications_to_admin WHERE user_id = ?', (user_id, ))

    def user_is_authorized(self, data):
        data = self.__db.db_read('SELECT user_id FROM applications WHERE user_nick = ? AND user_password = ?', (data[0], data[1]))
        if len(data) > 0:
            return True

    def get_admins(self):
        temp = list()
        data = self.__db.db_read('SELECT user_id FROM users WHERE is_admin = 1', ())
        for i in data:
            temp.append(i[0])
        return temp

    def user_is_admin_local(self, user_id):
        data = self.__db.db_read('SELECT is_admin FROM users WHERE user_id = ?', (user_id, ))
        if len(data) > 0:
            if data[0][0] == 1:
                status = True
            else:
                status = False
            return status

    def get_all_application(self):
        return self.__db.db_read('SELECT user_id, user_fio, date_airdrop_wond FROM applications', ())

    def update_date_airdrop_wond(self, date_airdrop_wond, user_id):
        self.__db.db_write('UPDATE applications SET date_airdrop_wond = ? WHERE user_id = ?', (date_airdrop_wond.strftime("%Y-%m-%d %H:%M"), user_id))

    def add_application_local(self, user_id, photo, data):
        social_networks = json.dumps({})
        self.__db.db_write('INSERT INTO applications '
                           '(user_id, user_photo, user_nick, user_password, user_fio, user_birthday, '
                           'user_city, user_email, user_employment, user_category, '
                           'user_social_problem, user_environmental_problem, user_most_important_problem, '
                           'social_networks, date_airdrop_wond, date_registration'
                           f') VALUES("{user_id}", "{photo}", "{data[0]}", "{data[1]}", "{data[3]}", "{data[4]}", '
                           f'"{data[5]}", "{data[6]}", "{data[7]}", "{data[8]}", "{data[9]}", "{data[10]}", '
                           f'"{data[11]}", "{social_networks}", {datetime.today().strftime("%Y-%m-%d %H:%M")}, '
                           f'{datetime.today().strftime("%Y-%m-%d %H:%M")})', ())

    def get_social_networks(self, user_id):
        return json.loads(self.__db.db_read('SELECT social_networks FROM applications WHERE user_id = ?', (user_id, ))[0][0])

    def update_social_networks(self, user_id, name, value):
        old = self.__db.db_read('SELECT social_networks FROM applications WHERE user_id = ?', (user_id, ))[0][0]
        old = json.loads(old)
        old.update({name: value})
        self.__db.db_write('UPDATE applications SET social_networks = ? WHERE user_id = ?', (json.dumps(old), user_id))

    def user_id_registered(self, user_id):
        data = self.__db.db_read('SELECT user_id FROM applications WHERE user_id = ?', (user_id, ))
        if len(data) > 0:
            return True
        else:
            return False

    def get_user_info(self, user_id):
        return self.__db.db_read('SELECT token_balance, first_name, last_name, nick_name, is_admin '
                                 'FROM users WHERE user_id = ?',
                                 (user_id,))[0]

    def get_application_by_user_id(self, user_id):
        return self.__db.db_read('SELECT user_photo, user_nick, user_password, user_fio, user_birthday,'
                                 'user_city, user_email, user_employment, user_category, user_social_problem,'
                                 'user_environmental_problem, user_most_important_problem FROM applications WHERE user_id = ?', (user_id, ))[0]

