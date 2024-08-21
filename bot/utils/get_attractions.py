import requests

from bot.data.settings import settings


def get_attractions(lat: str, lon: str) -> str:
    try:
        response = requests.get(
            f"https://catalog.api.2gis.com/3.0/items"
            f"?q=Достопримечательности"
            f"&sort_point={lon},{lat}"
            f"&key={settings.bots.api_2gis}"
            f"&sort=distance"
        )
        message = "Достопримечательности рядом:\r\n\n"
        if response.status_code == 200 and len(response.json()["result"]["items"]) > 0:
            for index, place in enumerate(response.json()["result"]["items"]):
                if "name" in place.keys():
                    message += f"{index + 1}. 🗿{place["name"]}\r\n\n"
                elif "full_name" in place.keys():
                    message += f"{index + 1}. 🗿{place["full_name"]}\r\n\n"
            return message
        return "😔Не найдено достопимечательностей рядом"
    except:
        return "😔Не найдено достопимечательностей рядом"
