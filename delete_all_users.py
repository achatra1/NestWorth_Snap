"""
Script to delete all users from the MongoDB database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings

async def delete_all_users():
    """Delete all users from the database"""
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client.nestworth
    
    try:
        # Delete all documents from the users collection
        result = await db.users.delete_many({})
        print(f"✓ Successfully deleted {result.deleted_count} users from the database")
        
        # Also delete all profiles associated with users
        profile_result = await db.profiles.delete_many({})
        print(f"✓ Successfully deleted {profile_result.deleted_count} profiles from the database")
        
        # Delete all projections
        projection_result = await db.projections.delete_many({})
        print(f"✓ Successfully deleted {projection_result.deleted_count} projections from the database")
        
    except Exception as e:
        print(f"✗ Error deleting users: {e}")
    finally:
        client.close()
        print("\n✓ Database connection closed")

if __name__ == "__main__":
    print("Deleting all users, profiles, and projections from the database...")
    asyncio.run(delete_all_users())