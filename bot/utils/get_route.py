import io
import typing

import httpx
from staticmap import staticmap, CircleMarker


class RouteRepository:
    def __init__(self: typing.Self, client: httpx.AsyncClient) -> None:
        self.client = client

    async def create_car_route(
        self: typing.Self, *args: tuple[float, float]
    ) -> list[tuple[float, float]]:
        coords = ";".join([f"{coord[1]},{coord[0]}" for coord in args])
        response = await self.client.get(
            f"https://router.project-osrm.org/route/v1/car/{coords}.json",
            params={
                "geometries": "geojson",
                "overview": "simplified",
            },
        )
        if not response.is_success:
            raise RuntimeError("Failed to fetch route data")
        return response.json()["routes"][0]["geometry"]["coordinates"]


async def get_route(coords: list[tuple[str]]):
    async with httpx.AsyncClient() as client:
        repository = RouteRepository(client)
        try:
            route = await repository.create_car_route(*coords)
            route_map = staticmap.StaticMap(1024, 1024)
            route_map.add_line(staticmap.Line(route, "blue", 3))
            for coord in coords:
                marker_outline = CircleMarker((coord[1], coord[0]), "white", 18)
                marker = CircleMarker((coord[1], coord[0]), "#0036FF", 12)
                route_map.add_marker(marker_outline)
                route_map.add_marker(marker)
            image = route_map.render()

            with io.BytesIO() as fp:
                image.save(fp, format="png", optimize=True)
                fp.seek(0)
                image_bytes = fp.read()

            return image_bytes

        except:
            return None
