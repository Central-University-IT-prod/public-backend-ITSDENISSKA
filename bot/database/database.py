import motor.motor_asyncio
from bson import ObjectId

from bot.data.settings import settings
from bot.utils.generate_unique_travel_id import generate_unique_id


class Database:
    def __init__(self, host: str, port: int, db_name: str) -> None:
        self.host = host
        self.port = port
        self.db_name = db_name
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.host, self.port)
        self.db = self.client[self.db_name]

    async def create_user(
        self,
        telegram_id: int,
        age: int,
        city: str,
        bio: str,
    ) -> dict:
        user = {
            "telegram_id": telegram_id,
            "age": age,
            "city": city,
            "bio": bio,
        }
        await self.db.users.insert_one(user)
        return user

    async def update_users_age_by_telegram_id(self, telegram_id: int, age: int) -> None:
        await self.db.users.update_one(
            {"telegram_id": telegram_id}, {"$set": {"age": age}}
        )

    async def update_users_city_by_telegram_id(
        self, telegram_id: int, city: str
    ) -> None:
        await self.db.users.update_one(
            {"telegram_id": telegram_id}, {"$set": {"city": city}}
        )

    async def update_users_bio_by_telegram_id(self, telegram_id: int, bio: str) -> None:
        await self.db.users.update_one(
            {"telegram_id": telegram_id}, {"$set": {"bio": bio}}
        )

    async def get_user_by_telegram_id(self, telegram_id: int) -> dict:
        return await self.db.users.find_one({"telegram_id": telegram_id})

    async def update_user(self, telegram_id: int, update_data: dict) -> None:
        await self.db.users.update_one(
            {"telegram_id": telegram_id}, {"$set": update_data}
        )

    async def delete_user(self, telegram_id: int) -> None:
        await self.db.users.delete_one({"telegram_id": telegram_id})

    async def create_travel(
        self,
        author_telegram_id: int,
        travel_name: str,
    ) -> dict:
        existing_travels_ids = await self.get_all_travels_ids()
        travel_id = await generate_unique_id(existing_travels_ids)
        travel = {
            "author_telegram_id": author_telegram_id,
            "travel_id": travel_id,
            "travel_name": travel_name,
            "latitude": "",
            "longitude": "",
            "travel_points": list(),
            "users": list(),
        }
        await self.db.travels.insert_one(travel)

        await self.db.notes.insert_one(
            {
                "travel_id": travel_id,
                "photos": list(),
                "files": list(),
            }
        )

        return travel

    async def get_all_travels_ids(self):
        return await self.db.travels.distinct("travel_id")

    async def get_travels_by_telegram_id(self, author_telegram_id: int) -> list[dict]:
        return await self.db.travels.find(
            {"author_telegram_id": author_telegram_id}
        ).to_list(length=None)

    async def get_travel_by_travel_id(self, travel_id: str) -> dict:
        return await self.db.travels.find_one({"travel_id": travel_id})

    async def update_travel(self, travel_id: str, update_data: dict) -> None:
        await self.db.travels.update_one(
            {"travel_id": travel_id}, {"$set": update_data}
        )

    async def delete_travel(self, travel_id: str) -> None:
        await self.db.travels.delete_one({"travel_id": travel_id})

    async def add_travel_point_to_travel_by_travel_id(
        self,
        travel_id: str,
        travel_point_id: str,
    ) -> None:
        travel = await self.db.travels.find_one({"travel_id": travel_id})
        travel["travel_points"].append(travel_point_id)
        await self.db.travels.update_one(
            {"travel_id": travel_id},
            {"$set": {"travel_points": travel["travel_points"]}},
        )

    async def add_travel_point_by_travel_id(
        self,
        travel_id: str,
        travel_point_name: str,
        latitude: str,
        longitude: str,
        start_date: str,
        end_date: str,
    ) -> dict:
        await self.db.travels_points.insert_one(
            {
                "travel_id": travel_id,
                "travel_point_name": travel_point_name,
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start_date,
                "end_date": end_date,
            },
        )

        travel_point = await self.db.travels_points.find_one(
            {
                "travel_id": travel_id,
                "travel_point_name": travel_point_name,
                "start_date": start_date,
                "end_date": end_date,
            },
        )

        await self.add_travel_point_to_travel_by_travel_id(
            travel_id=travel_id,
            travel_point_id=str(travel_point["_id"]),
        )

        return travel_point

    async def get_travel_point_by_travel_point_id(self, travel_point_id: str) -> dict:
        return await self.db.travels_points.find_one({"_id": ObjectId(travel_point_id)})

    async def get_travel_points_by_travel_id(self, travel_id: str) -> list[dict]:
        return await self.db.travels_points.find({"travel_id": travel_id}).to_list(
            length=None
        )

    async def delete_travel_point(self, travel_point_id: str) -> None:
        travel_point = await self.get_travel_point_by_travel_point_id(
            travel_point_id=travel_point_id
        )
        await self.db.travels_points.delete_one({"_id": ObjectId(travel_point_id)})
        travel = await self.db.travels.find_one(
            {"travel_id": travel_point.get("travel_id", "unknown")}
        )
        travel["travel_points"].remove(travel_point_id)
        await self.db.travels.update_one(
            {"travel_id": travel.get("travel_id", "unknown")},
            {"$set": travel},
        )

    async def update_travel_point_name_by_travel_point_id(
        self,
        travel_point_id: str,
        travel_point_name: str,
    ) -> None:
        await self.db.travels_points.update_one(
            {"_id": ObjectId(travel_point_id)},
            {"$set": {"travel_point_name": travel_point_name}},
        )

    async def update_travel_point_start_date_by_travel_point_id(
        self,
        travel_point_id: str,
        start_date: str,
    ) -> None:
        await self.db.travels_points.update_one(
            {"_id": ObjectId(travel_point_id)},
            {"$set": {"start_date": start_date}},
        )

    async def update_travel_point_end_date_by_travel_point_id(
        self,
        travel_point_id: str,
        end_date: str,
    ) -> None:
        await self.db.travels_points.update_one(
            {"_id": ObjectId(travel_point_id)},
            {"$set": {"end_date": end_date}},
        )

    async def delete_travel_by_travel_id(self, travel_id: str) -> None:
        travel = await self.db.travels.find_one({"travel_id": travel_id})
        for travel_point in travel.get("travel_points", "unknown"):
            await self.delete_travel_point(travel_point_id=str(travel_point))
        await self.db.travels.delete_one({"travel_id": travel_id})

    async def add_photo_to_travel_note(self, travel_id: str, photo: str) -> None:
        notes = await self.db.notes.find_one({"travel_id": travel_id})
        notes["photos"].append(photo)
        await self.db.notes.update_one({"travel_id": travel_id}, {"$set": notes})

    async def add_file_to_travel_note(self, travel_id: str, file: str) -> None:
        notes = await self.db.notes.find_one({"travel_id": travel_id})
        notes["files"].append(file)
        await self.db.notes.update_one({"travel_id": travel_id}, {"$set": notes})

    async def get_notes_by_travel_id(self, travel_id: str) -> None:
        return await self.db.notes.find_one({"travel_id": travel_id})


db = Database(
    host=settings.bots.mongodb_host,
    port=settings.bots.mongodb_port,
    db_name=settings.bots.mongodb_name,
)
