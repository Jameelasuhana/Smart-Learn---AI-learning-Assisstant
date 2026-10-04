import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    client: AsyncIOMotorClient = None
    db = None

db_manager = DatabaseManager()

async def connect_to_mongo():
    logger.info("Connecting to MongoDB Atlas...")
    try:
        db_manager.client = AsyncIOMotorClient(settings.MONGODB_URI)
        db_manager.db = db_manager.client[settings.MONGODB_DATABASE]
        
        # Verify connection
        await db_manager.client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB database: {settings.MONGODB_DATABASE}")
        
        # Create database indexes for performance and constraints
        await create_indexes()
    except Exception as e:
        logger.warning(f"MongoDB connection warning: {e}. App will start, but DB features require a valid MONGODB_URI.")

async def close_mongo_connection():
    if db_manager.client:
        db_manager.client.close()
        logger.info("Closed MongoDB connection.")

def get_database():
    return db_manager.db

async def create_indexes():
    if db_manager.db is not None:
        try:
            # Index users collection by email (unique)
            await db_manager.db["users"].create_index("email", unique=True)
            # Index tests by user_id
            await db_manager.db["tests"].create_index("user_id")
            # Index attempts by user_id and test_id
            await db_manager.db["attempts"].create_index([("user_id", 1), ("test_id", 1)])
            logger.info("MongoDB indexes verified/created successfully.")
        except Exception as e:
            logger.warning(f"Could not create MongoDB indexes: {e}")
