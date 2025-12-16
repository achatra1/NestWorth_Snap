from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

# Global MongoDB client
mongodb_client: AsyncIOMotorClient = None


async def connect_to_mongo():
    """Connect to MongoDB Atlas."""
    global mongodb_client
    try:
        mongodb_client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        # Test the connection
        await mongodb_client.admin.command('ping')
        logger.info("Successfully connected to MongoDB Atlas")
        
        # Create indexes for efficient queries
        await create_indexes()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.warning("Server will start but database operations will fail")
        # Don't raise - allow server to start even if DB connection fails


async def create_indexes():
    """Create database indexes for efficient queries."""
    try:
        db = get_database()
        
        # Index for projections collection
        # Compound index on user_id and profile_id for fast lookups
        await db.projections.create_index([("user_id", 1), ("profile_id", 1)], unique=True)
        logger.info("Created index on projections collection")
        
        # Index for profiles collection (if not already exists)
        await db.profiles.create_index([("user_id", 1)])
        logger.info("Created index on profiles collection")
        
    except Exception as e:
        logger.warning(f"Failed to create indexes (may already exist): {e}")


async def close_mongo_connection():
    """Close MongoDB connection."""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("Closed MongoDB connection")


def get_database():
    """Get the database instance."""
    return mongodb_client.nestworth


async def ping_database() -> bool:
    """Ping the database to check connectivity."""
    try:
        await mongodb_client.admin.command('ping')
        return True
    except Exception as e:
        logger.error(f"Database ping failed: {e}")
        return False