import os
import bcrypt
import time
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

# Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "seo_saas"
SECRET_KEY = os.getenv("SECRET_KEY", "SAAS_SECRET_NEURAL_FLEET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

# Initialize Client
client = AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]
users_collection = db["users"]

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

async def create_user(username: str, email: str, password: str) -> bool:
    # Check if exists
    existing = await users_collection.find_one({"$or": [{"username": username}, {"email": email}]})
    if existing:
        return False
        
    hashed = hash_password(password)
    user_doc = {
        "username": username,
        "email": email,
        "hashed_password": hashed,
        "created_at": datetime.utcnow()
    }
    await users_collection.insert_one(user_doc)
    return True

async def get_user(username: str):
    user = await users_collection.find_one({"username": username})
    if user:
        user["id"] = str(user["_id"])
        return user
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None
