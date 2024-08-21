import requests


def get_city_code(city: str) -> str:
    try:
        city = city.split(",")[0]
        response = requests.post(
            f"https://autocomplete.travelpayouts.com/places2?locale=en&types[]=airport&types[]=city&term={city}"
        )
        if response.status_code == 200 and response.json():
            return response.json()[0]["code"]
        else:
            return "error"
    except:
        return "error"
