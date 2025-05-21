# shared/database.py
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://<user>:<pass>@cluster.mongodb.net/")
DB_NAME = os.getenv("DB_NAME", "hydration_db")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

async def coach_exists(full_name: str) -> bool:
    coach = await db["users"].find_one({
        "full_name": full_name.strip(),
        "role": "coach"
    })
    return coach is not None
