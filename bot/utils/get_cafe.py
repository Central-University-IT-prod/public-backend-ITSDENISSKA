import requests

from bot.data.settings import settings


def get_cafe(lat: str, lon: str) -> str | None:
    try:
        response = requests.get(
            f"https://catalog.api.2gis.com/3.0/items"
            f"?q=Кафе, ресторан"
            f"&sort_point={lon},{lat}"
            f"&key={settings.bots.api_2gis}"
            f"&sort=distance"
        )
        message = "Кафе и рестораны рядом:\r\n\n"
        if response.status_code == 200 and len(response.json()["result"]["items"]) > 0:
            for index, place in enumerate(response.json()["result"]["items"]):
                cafe = requests.get(
                    f"https://catalog.api.2gis.com/3.0/items/byid"
                    f"?id={place["id"]}"
                    f"&locale=ru_RU"
                    f"&key={settings.bots.api_2gis}"
                )
                print(cafe.json())
                message += (f"{index + 1}. 📍{place["name"]}\r\n"
                            f"Адрес: {place["address_name"]}\r\n\n")

            return message
        return "😔Не найдено кафе и ресторанов рядом"
    except:
        return "😔Не найдено кафе и ресторанов рядом"

