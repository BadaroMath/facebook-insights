"""
Database configuration and connection management using Motor (async MongoDB driver).
Handles connection pooling, initialization, and cleanup.
"""

import asyncio
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie

from app.core.config import settings
from app.models.user import User
from app.models.facebook_page import FacebookPage
from app.models.facebook_post import FacebookPost
from app.models.analytics import Analytics
from app.models.report import Report


logger = logging.getLogger(__name__)


class Database:
    """Database connection manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None


# Global database instance
db = Database()


async def init_database():
    """Initialize database connection and setup."""
    try:
        logger.info("Connecting to MongoDB...")
        
        # Create MongoDB client
        db.client = AsyncIOMotorClient(
            settings.MONGO_URL,
            maxPoolSize=10,
            minPoolSize=1,
            maxIdleTimeMS=45000,
            connectTimeoutMS=10000,
            serverSelectionTimeoutMS=10000,
        )
        
        # Get database
        db.database = db.client[settings.MONGO_DB_NAME]
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info("✅ Successfully connected to MongoDB")
        
        # Initialize Beanie with document models
        await init_beanie(
            database=db.database,
            document_models=[
                User,
                FacebookPage,
                FacebookPost,
                Analytics,
                Report,
            ]
        )
        logger.info("✅ Beanie initialized with document models")
        
        # Create indexes
        await create_indexes()
        logger.info("✅ Database indexes created")
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise


async def close_database():
    """Close database connection."""
    if db.client:
        db.client.close()
        logger.info("✅ MongoDB connection closed")


async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    if not db.database:
        raise RuntimeError("Database not initialized")
    return db.database


async def create_indexes():
    """Create database indexes for better performance."""
    try:
        # User indexes
        await User.get_motor_collection().create_index("email", unique=True)
        await User.get_motor_collection().create_index("facebook_user_id", unique=True, sparse=True)
        
        # Facebook Page indexes
        await FacebookPage.get_motor_collection().create_index("page_id", unique=True)
        await FacebookPage.get_motor_collection().create_index("user_id")
        await FacebookPage.get_motor_collection().create_index([("user_id", 1), ("page_id", 1)])
        
        # Facebook Post indexes
        await FacebookPost.get_motor_collection().create_index("post_id", unique=True)
        await FacebookPost.get_motor_collection().create_index("page_id")
        await FacebookPost.get_motor_collection().create_index("created_time")
        await FacebookPost.get_motor_collection().create_index([("page_id", 1), ("created_time", -1)])
        
        # Analytics indexes
        await Analytics.get_motor_collection().create_index([("page_id", 1), ("date", -1)])
        await Analytics.get_motor_collection().create_index([("post_id", 1), ("date", -1)])
        await Analytics.get_motor_collection().create_index("date")
        
        # Report indexes
        await Report.get_motor_collection().create_index("user_id")
        await Report.get_motor_collection().create_index("created_at")
        await Report.get_motor_collection().create_index([("user_id", 1), ("created_at", -1)])
        
        logger.info("✅ All database indexes created successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {e}")
        # Don't raise here as indexes are not critical for basic functionality


async def ping_database() -> bool:
    """Check database connectivity."""
    try:
        if not db.client:
            return False
        await db.client.admin.command('ping')
        return True
    except Exception:
        return False


async def get_database_stats():
    """Get database statistics."""
    try:
        if not db.database:
            return None
            
        stats = await db.database.command("dbStats")
        
        # Get collection stats
        collections = await db.database.list_collection_names()
        collection_stats = {}
        
        for collection_name in collections:
            collection = db.database[collection_name]
            count = await collection.count_documents({})
            collection_stats[collection_name] = count
        
        return {
            "database_name": stats.get("db"),
            "collections": len(collections),
            "documents": collection_stats,
            "data_size": stats.get("dataSize", 0),
            "storage_size": stats.get("storageSize", 0),
            "indexes": stats.get("indexes", 0),
            "index_size": stats.get("indexSize", 0),
        }
        
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return None


# Health check function
async def database_health_check():
    """Perform database health check."""
    try:
        # Check connection
        is_connected = await ping_database()
        if not is_connected:
            return {"status": "unhealthy", "error": "Cannot connect to database"}
        
        # Get basic stats
        stats = await get_database_stats()
        
        return {
            "status": "healthy",
            "database": settings.MONGO_DB_NAME,
            "stats": stats
        }
        
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}