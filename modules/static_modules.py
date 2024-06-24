#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import base64
import random
import requests
import smtplib
from random import choice
from email.mime.text import MIMEText
from captcha.image import ImageCaptcha
#####################################


def split_text_by_period(text, max_length=1024):
    """
    Разделяет текст на части, каждая из которых не превышает max_length символов, разделяя текст только по точкам.

    :param text: str, исходный текст
    :param max_length: int, максимальная длина части текста
    :return: list, список частей текста
    """
    if len(text) <= max_length:
        return [text]

    parts = []
    current_part = []

    for sentence in text.split('.'):
        sentence = sentence.strip() + '.'
        if len(' '.join(current_part) + sentence) > max_length:
            parts.append(' '.join(current_part).strip())
            current_part = [sentence.strip()]
        else:
            current_part.append(sentence.strip())

    # Добавляем последнюю часть, если она не пустая
    if current_part:
        parts.append(' '.join(current_part).strip())

    # Убираем последний символ '.' у последнего элемента списка
    if parts and parts[-1].endswith('.'):
        parts[-1] = parts[-1][:-1]

    return parts


def upload_image_to_imgur(image_base64, client_id):
    url = "https://api.imgur.com/3/upload"
    headers = {
        "Authorization": f"Client-ID {client_id}"
    }
    data = {
        "image": base64.b64decode(image_base64),
        "type": "file"
    }
    response = requests.post(url, headers=headers, files=data)

    if response.status_code == 200:
        response_data = response.json()
        return response_data["data"]["link"]
    else:
        raise Exception(f"Failed to upload image: {response.status_code} {response.text}")


def generate_captcha(user_id):
    alphavet = ['1', '2', '3', '4', '5', '6', '7', '8', 'a', 'b', 'd', 'e', 'g', 'h', 'i', 'j', 'n', 'q', 't', 'y', 'A',
                'D',
                'E', 'F', 'G', 'M', 'N', 'P', 'Q', 'R']
    pattern = str()
    for i in range(5):
        pattern += choice(alphavet)
    image_captcha = ImageCaptcha(width=300, height=200)
    image_captcha.write(pattern, 'captcha.png')
    return pattern


def send_email(email, config):
    sender = config.get_config()['email_login']
    password = config.get_config()['email_pass']
    code_in_msg = str(random.randint(a=111111, b=999999))
    message = str(f'Ваш код подтверждения: {code_in_msg}')
    msg = MIMEText(message)
    try:
        server = smtplib.SMTP_SSL("smtp.mail.ru", 465)
        server.login(sender, password)
        server.sendmail(sender, email, msg.as_string())
        return True, [code_in_msg, ]
    except:
        return False


def send_email_to_admin(user_nickname, user_input, config):
    sender = config.get_config()['email_login']
    password = config.get_config()['email_pass']
    dest = config.get_config()['email_for_applications']
    message = str(f'Пользователь @{user_nickname} оставил заявку!\n{user_input}')
    msg = MIMEText(message)
    try:
        server = smtplib.SMTP_SSL("smtp.mail.ru", 465)
        server.login(sender, password)
        server.sendmail(sender, dest, msg.as_string())
        return True
    except:
        return False

