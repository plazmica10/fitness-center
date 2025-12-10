from pymongo import MongoClient, ASCENDING
from config import settings

client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB_NAME]

# Collections
users_collection = db["users"]


def init_db():
    """Initialize database with indexes and constraints"""
    # Create unique index on email
    users_collection.create_index([("email", ASCENDING)], unique=True)
    
    # Create index on username
    users_collection.create_index([("username", ASCENDING)], unique=True)
    
    print("Database initialized successfully")
