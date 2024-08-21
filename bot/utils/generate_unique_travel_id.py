import uuid


async def generate_unique_id(existing_travels_ids: list[str]) -> str:
    unique_id = str(uuid.uuid4().int)[:8]
    while unique_id in existing_travels_ids:
        unique_id = str(uuid.uuid4().int)[:8]
    return unique_id
