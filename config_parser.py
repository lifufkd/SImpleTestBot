#####################################
#            Created by             #
#                SBR                #
#####################################
import json
import os
import sys
#####################################


class ConfigParser:
    def __init__(self, file_path, questions_path):
        super(ConfigParser, self).__init__()
        self.__file_path = file_path
        self.__questions_path = questions_path
        self.__default = {'tg_api': '', 'admins': []}
        self.__questions = {'test': [[], []]}
        self.__current_config_secrets = None
        self.__current_config_questions = None
        self.load_conf()
        self.load_questions()

    def load_conf(self):
        if os.path.exists(self.__file_path):
            with open(self.__file_path, 'r', encoding='utf-8') as file:
                self.__current_config_secrets = json.loads(file.read())
            if len(self.__current_config_secrets['tg_api']) == 0:
                sys.exit('config is invalid')
        else:
            self.create_conf(self.__file_path, self.__default)
            sys.exit('config is not existed')

    def load_questions(self):
        if os.path.exists(self.__questions_path):
            with open(self.__questions_path, 'r', encoding='utf-8') as file:
                self.__current_config_questions = json.loads(file.read())
        else:
            self.create_conf(self.__questions_path, self.__questions)
            sys.exit('config is not existed')

    def create_conf(self, path, config):
        with open(path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(config, sort_keys=True, indent=4))

    def get_config(self):
        return self.__current_config_secrets

    def get_questions(self):
        return self.__current_config_questions
