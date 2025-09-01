from datetime import datetime
from typing import Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.security import get_password_hash, verify_password
from app.models.user import UserCreate, UserInDB, UserUpdate


async def get_user(db: AsyncIOMotorDatabase, user_id: str) -> Optional[UserInDB]:
    if user := await db.users.find_one({"_id": ObjectId(user_id)}):
        return UserInDB(**user)
    return None


async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[UserInDB]:
    if user := await db.users.find_one({"email": email}):
        return UserInDB(**user)
    return None


async def create_user(db: AsyncIOMotorDatabase, user: UserCreate) -> UserInDB:
    hashed_password = get_password_hash(user.password)
    
    # Create user document for MongoDB
    user_doc = {
        "email": user.email,
        "name": user.name,
        "hashed_password": hashed_password,
        "deriv_token": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    return UserInDB(**user_doc)


async def update_user(
    db: AsyncIOMotorDatabase, user_id: str, user_update: UserUpdate
) -> Optional[UserInDB]:
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    update_data["updated_at"] = datetime.utcnow()
    
    if result := await db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
        return_document=True,
    ):
        return UserInDB(**result)
    return None


async def authenticate_user(
    db: AsyncIOMotorDatabase, email: str, password: str
) -> Optional[UserInDB]:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
