#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import json
#####################################


class TempUserData:
    def __init__(self):
        super(TempUserData, self).__init__()
        self.__user_data = {}

    def temp_data(self, user_id):
        if user_id not in self.__user_data.keys():
            self.__user_data.update({user_id: [None, [], None]})
        return self.__user_data


class DbAct:
    def __init__(self, db, config):
        super(DbAct, self).__init__()
        self.__db = db
        self.__config = config

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