from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


class Database:
    client: AsyncIOMotorClient = None

    def get_db(self):
        return self.client[settings.mongodb_db]

db = Database()

async def get_database():
    return db.get_db()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.mongodb_uri)

async def close_mongo_connection():
    if db.client:
        db.client.close()


async def get_database_sync():
    """Get database connection for use in sync contexts (like Celery tasks)"""
    if not db.client:
        await connect_to_mongo()

    return db.get_db()
