from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    
    def get_db(self):
        return self.client[settings.mongodb_db]

db = Database()

async def get_database() -> Database:
    return db

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.mongodb_uri)

async def close_mongo_connection():
    if db.client:
        db.client.close()
