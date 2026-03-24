import os
import bcrypt
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt

# Configuration
DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "users.json"))
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

SECRET_KEY = os.getenv("SECRET_KEY", "SAAS_SECRET_NEURAL_FLEET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

def _load_users():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def _save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

async def create_user(username: str, email: str, password: str) -> bool:
    users = _load_users()
    for u in users:
        if u["username"] == username or u["email"] == email:
            return False
            
    hashed = hash_password(password)
    user_doc = {
        "username": username,
        "email": email,
        "hashed_password": hashed,
        "created_at": datetime.utcnow().isoformat()
    }
    users.append(user_doc)
    _save_users(users)
    return True

async def get_user(username: str):
    users = _load_users()
    for u in users:
        if u["username"] == username:
            return u
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

# Seed a default user for local development if empty
def _seed_default():
    users = _load_users()
    if not users:
        print("🌱 Seeding default user 'aathi'...")
        hashed = hash_password("admin")
        user_doc = {
            "username": "aathi",
            "email": "aathisankar22@gmail.com",
            "hashed_password": hashed,
            "created_at": datetime.utcnow().isoformat()
        }
        users.append(user_doc)
        _save_users(users)

_seed_default()

