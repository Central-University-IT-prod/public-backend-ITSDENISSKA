import datetime

import requests

from bot.data.settings import settings
from bot.utils.get_city_code import get_city_code


def format_text(data) -> dict:
    month = {
        'Dec': 'Декабрь',
        'Jan': 'Январь',
        'Mar': 'Март',
        'Apr': 'Апрель',
        'May': 'Май',
        'Jun': 'Июнь',
        'Jul': 'Июль',
        'Aug': 'Август',
        'Sep': 'Сентябрь',
        'Oct': 'Остябрь',
        'Nov': 'Ноябрь'
    }

    date = datetime.datetime.strptime(data['departure_at'].split('+')[0], '%Y-%m-%dT%X')
    message = (f'🛫Удалось найти билеты на самолёт:\r\n\n'
               f'Авиаоператор: {data['airline']}\r\n'
               f'Дата отправления: {str(date.day).rjust(2, "0")}.{str(date.month).rjust(2, "0")}.'
               f'{str(date.year).rjust(2, "0")}\r\n'
               f'Время отправления: {str(date.hour).rjust(2, "0")}:{str(date.minute).rjust(2, "0")}\r\n'
               f'Длительность полета: {str(data['duration'] // 60).rjust(2, "0")}:'
               f'{str(data['duration'] % 60).rjust(2, "0")}\r\n'
               f'Стоимость билета: {data['price']} ₽\r\n\n'
               f'* Билеты подбираются от вашего текущего местоположения❗\r\n'
               f'Вы можете изменить его в профиле❗')
    return {'message': message, 'link': 'https://www.aviasales.com' + data['link']}


def get_tickets(origin: str, destination: str, date: str) -> dict:
    try:
        departure_time = datetime.datetime.strptime(date, "%d.%m.%Y").date()
        origin_code = get_city_code(origin)
        destination_code = get_city_code(destination)
        if origin_code == "error":
            return {"message": "❗Ошибка с местоположением", "link": None}
        elif destination_code == "error":
            return {"message": "❗Ошибка с точкой назначения", "link": None}
        response = requests.get(
            f"https://api.travelpayouts.com/aviasales/v3/prices_for_dates?"
            f"origin={origin_code}&"''
            f"destination={destination_code}&"
            f"departure_at={departure_time.year}-{str(departure_time.month).rjust(2, '0')}-{departure_time.day}&"
            f"token={settings.bots.api_tickets}"
        )
        if response.status_code == 200:
            if len(response.json()["data"]) > 0:
                return format_text(response.json()['data'][0])
            return {"message": "😔Не удалось найти билеты на самолёт на дату начала вашего путешествия\r\n\n"
                               "* Билеты подбираются от вашего текущего местоположения❗\r\n"
                               f"Вы можете изменить его в профиле или изменить дату посещения этого места❗",
                    "link": None}
        return {"message": "😔Не удалось найти билеты на самолёт\r\n\n"
                           "* Билеты подбираются от вашего текущего местоположения❗\r\n"
                           f"Вы можете изменить его в профиле или изменить дату посещения этого места❗",
                "link": None}
    except:
        return {"message": "😔Не удалось найти билеты на самолёт\r\n\n"
                           "* Билеты подбираются от вашего текущего местоположения❗\r\n"
                           f"Вы можете изменить его в профиле или изменить дату посещения этого места❗",
                "link": None}
