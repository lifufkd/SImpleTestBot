#####################################
#            Created by             #
#                SBR                #
#####################################
import os
import sqlite3
#####################################


class DB:
    def __init__(self, path, lock):
        super(DB, self).__init__()
        self.__lock = lock
        self.__db_path = path
        self.__cursor = None
        self.__db = None
        self.init()

    def init(self):
        if not os.path.exists(self.__db_path):
            self.__db = sqlite3.connect(self.__db_path, check_same_thread=False)
            self.__cursor = self.__db.cursor()
            self.__cursor.execute('''
            CREATE TABLE users(
                row_id INTEGER primary key autoincrement not null,
                user_id INTEGER,
                token_balance FLOAT,
                first_name TEXT,
                last_name TEXT,
                nick_name TEXT,
                is_admin BOOL,
                UNIQUE(user_id)
            )
            ''')
            self.__cursor.execute('''
            CREATE TABLE applications(
                row_id INTEGER primary key autoincrement not null,
                user_id INTEGER,
                user_fio TEXT,
                user_birthday TEXT,
                user_email TEXT,
                user_city TEXT,
                user_nick TEXT,
                user_password TEXT,
                user_photo TEXT,
                user_employment TEXT,
                user_category TEXT,
                user_social_problem TEXT,
                user_environmental_problem TEXT,
                user_most_important_problem TEXT,
                social_networks TEXT
            )
            ''')
            self.__cursor.execute('''
            CREATE TABLE groups(
                row_id INTEGER primary key autoincrement not null,
                chat_id INTEGER,
                message_id INTEGER
            )
            ''')
            self.__db.commit()
        else:
            self.__db = sqlite3.connect(self.__db_path, check_same_thread=False)
            self.__cursor = self.__db.cursor()

    def db_write(self, queri, args):
        with self.__lock:
            self.__cursor.execute(queri, args)
            self.__db.commit()

    def db_read(self, queri, args):
        with self.__lock:
            self.__cursor.execute(queri, args)
            return self.__cursor.fetchall()
