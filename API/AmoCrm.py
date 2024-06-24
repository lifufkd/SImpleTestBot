#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import sys
from amocrm.v2 import tokens, Lead as _Lead, custom_field
from datetime import datetime
#####################################


class AmoCrmLead(_Lead):
    telegram_id = custom_field.NumericCustomField("telegram_id")
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
    user_most_important_problem = custom_field.TextCustomField("user_most_important_problem")
    from_group = custom_field.TextCustomField("from_group")
    from_chanel = custom_field.TextCustomField("from_chanel")
    registration_date = custom_field.TextCustomField("registration_date")
    WOND_tokens = custom_field.NumericCustomField("WOND_tokens")


def get_lead_by_custom_field(custom_field_id, custom_field_value):
    pass
    # leads = _Lead.find(
    #     query={
    #         'custom_fields': {
    #             'id': custom_field_id,
    #             'values': [custom_field_value]
    #         }
    #     }
    # )


class AmoCrm:
    def __init__(self, config):
        super(AmoCrm, self).__init__()
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

    def generate_tokens(self):
        tokens.default_token_manager.init(code=self.__config.get_config()['amocrm_temp_code'], skip_error=True)
        sys.exit("Token's succsessfully generated")

    def update_tokens_by_user_id(self, data, user_id):
        lead = get_lead_by_custom_field(359911, user_id)
        lead.WOND_tokens = data
        lead.save()

    def add_application(self, tg_id, tg_contact, user_photo, group_info, data):
        compare = {True: "Да", False: "Нет"}
        lead = AmoCrmLead.objects.create()
        lead.name = data[3]
        lead.WOND_tokens = 3
        lead.telegram_id = tg_id
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
        lead.user_most_important_problem = data[11]
        lead.from_group = compare[group_info[0]]
        lead.from_chanel = compare[group_info[1]]
        lead.registration_date = datetime.today().strftime('%Y-%m-%d %H:%M')
        lead.save()

    # def user_is_existed(self, user_id):
    #     temp = list()
    #     users = AmoCrmLead.objects.all()
    #     for i in users:
    #         temp.append(int(i.telegram_id))
    #     print(temp)
    #     if user_id in temp:
    #         return True