from requests import get


def get_locations(location: str) -> dict:
    try:
        url = f"https://nominatim.openstreetmap.org/search?format=json&limit=1&q={location}"
        response = get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                location = data[0]
                return {
                    "latitude": float(location["lat"]),
                    "longitude": float(location["lon"]),
                    "address": location["display_name"],
                }
        else:
            return {
                "latitude": "unknown",
                "longitude": "unknown",
                "address": "unknown",
            }
    except:
        return {
            "latitude": "unknown",
            "longitude": "unknown",
            "address": "unknown",
        }
