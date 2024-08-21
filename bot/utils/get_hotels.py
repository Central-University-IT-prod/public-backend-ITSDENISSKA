import requests

from bot.data.settings import settings


def get_hotels(lat: str, lon: str) -> str:
    try:
        response = requests.get(
            f"https://catalog.api.2gis.com/3.0/items"
            f"?q=Отель, хостел, гостиница"
            f"&sort_point={lon},{lat}"
            f"&key={settings.bots.api_2gis}"
            f"&sort=distance"
        )
        message = "Отели и гостиницы рядом:\r\n\n"
        if response.status_code == 200 and len(response.json()["result"]["items"]) > 0:
            for index, place in enumerate(response.json()["result"]["items"]):
                if "name" in place.keys():
                    message += (f"{index + 1}. 🛏️{place["name"]}\r\n"
                                f"Адрес: {place["address_name"]}\r\n\n")
                elif "full_name" in place.keys():
                    message += (f"{index + 1}. 🛏️{place["full_name"]}\r\n"
                                f"Адрес: {place["address_name"]}\r\n\n")

            return message
        return "😔Не найдено отелей и гостиниц рядом"
    except:
        "😔Не найдено отелей и гостиниц рядом"