"""
CertiNexus AI — MongoDB Atlas Database Connection & Lifecycle Manager

Uses official PyMongo driver with connection pooling and clean startup/shutdown hooks.
Maintains singleton MongoClient instance across the application.
Provides index creation and connectivity health checks without leaking credentials.
"""

import logging
from typing import Any, Dict, Optional, Tuple
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, PyMongoError

from app.core.config import settings

# Configure reliable DNS resolver fallback for MongoDB Atlas SRV resolution
try:
    import dns.resolver
    _resolver = dns.resolver.Resolver()
    default_ns = list(_resolver.nameservers)
    for ns in ["1.1.1.1", "8.8.8.8", "8.8.4.4"]:
        if ns not in default_ns:
            default_ns.append(ns)
    _resolver.nameservers = default_ns
    _resolver.timeout = 10.0
    _resolver.lifetime = 20.0
    dns.resolver.default_resolver = _resolver
except Exception:
    pass

logger = logging.getLogger("certinexus.database")


class MongoDBManager:
    """Singleton MongoDB Atlas Client and Database Manager."""

    _instance: Optional["MongoDBManager"] = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None
    _is_connected: bool = False
    _connection_error: Optional[str] = None

    def __new__(cls) -> "MongoDBManager":
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
        return cls._instance

    @property
    def client(self) -> Optional[MongoClient]:
        return self._client

    @property
    def db(self) -> Optional[Database]:
        return self._db

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def connection_error(self) -> Optional[str]:
        return self._connection_error

    def connect(self) -> bool:
        """Establish connection to MongoDB Atlas."""
        if not settings.is_mongodb_configured:
            self._is_connected = False
            self._connection_error = "MongoDB URI not configured or contains password placeholder (<db_password>)."
            logger.warning(f"MongoDB not connected: {self._connection_error}")
            return False

        try:
            logger.info("Connecting to MongoDB Atlas cluster...")
            server_api = ServerApi("1")
            self._client = MongoClient(
                settings.MONGODB_URI,
                server_api=server_api,
                maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
                connectTimeoutMS=5000,
                socketTimeoutMS=10000,
                appname="CertiNexusCluster",
            )

            # Test connection with ping
            self._client.admin.command("ping")
            self._db = self._client[settings.MONGODB_DATABASE]
            self._is_connected = True
            self._connection_error = None
            logger.info(f"Successfully connected to MongoDB Atlas database '{settings.MONGODB_DATABASE}'.")

            # Initialize indexes
            self.create_indexes()
            return True

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self._is_connected = False
            self._connection_error = f"MongoDB Atlas unreachable. Check network/IP allowlist: {type(e).__name__}"
            logger.warning(f"MongoDB connection failed: {self._connection_error}")
            return False
        except Exception as e:
            self._is_connected = False
            self._connection_error = f"MongoDB connection error: {type(e).__name__}"
            logger.error(f"Unexpected MongoDB connection error: {e}")
            return False

    def disconnect(self) -> None:
        """Close MongoDB connection gracefully."""
        if self._client:
            try:
                self._client.close()
                logger.info("MongoDB Atlas connection closed.")
            except Exception as e:
                logger.warning(f"Error closing MongoDB connection: {e}")
            finally:
                self._client = None
                self._db = None
                self._is_connected = False

    def ping(self) -> Tuple[bool, str]:
        """Perform a live ping check against the database."""
        if not self._is_connected or not self._client:
            return False, self._connection_error or "Not connected"
        try:
            self._client.admin.command("ping")
            return True, "Connected"
        except Exception as e:
            self._is_connected = False
            self._connection_error = str(e)
            return False, f"Ping failed: {type(e).__name__}"

    _last_connect_attempt: float = 0
    _reconnect_cooldown: float = 60.0

    def get_database(self) -> Optional[Database]:
        """Get the active database instance."""
        import time
        now = time.time()
        if not self._is_connected or self._db is None:
            # Only attempt lazy connect if cooldown has passed (avoids blocking requests)
            if settings.is_mongodb_configured and (now - self._last_connect_attempt > self._reconnect_cooldown):
                self._last_connect_attempt = now
                self.connect()
        return self._db if self._is_connected else None

    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """Get a specific collection from the active database."""
        db = self.get_database()
        if db is not None:
            return db[collection_name]
        return None

    def create_indexes(self) -> Dict[str, Any]:
        """Create required indexes across all logical collections."""
        if not self._is_connected or self._db is None:
            return {"status": "skipped", "reason": "database not connected"}

        index_results = {}
        try:
            # 1. users: unique email & unique username
            users_col = self._db["users"]
            users_col.create_index([("email", ASCENDING)], unique=True, sparse=True)
            users_col.create_index([("username", ASCENDING)], unique=True, sparse=True)
            index_results["users"] = "indexes created: email (unique), username (unique)"

            # 2. certificates: user_id, category, file.file_hash, created_at, processing_status
            certs_col = self._db["certificates"]
            certs_col.create_index([("user_id", ASCENDING)])
            certs_col.create_index([("category", ASCENDING)])
            certs_col.create_index([("created_at", DESCENDING)])
            certs_col.create_index([("file.file_hash", ASCENDING)], sparse=True)
            certs_col.create_index([("duplicate_hash", ASCENDING)], sparse=True)
            certs_col.create_index([("processing_status", ASCENDING)])
            index_results["certificates"] = "indexes created: user_id, category, created_at, file_hash, duplicate_hash"

            # 3. ocr_results: certificate_id
            ocr_col = self._db["ocr_results"]
            ocr_col.create_index([("certificate_id", ASCENDING)])
            index_results["ocr_results"] = "indexes created: certificate_id"

            # 4. extracted_entities: certificate_id, type
            entities_col = self._db["extracted_entities"]
            entities_col.create_index([("certificate_id", ASCENDING)])
            entities_col.create_index([("type", ASCENDING)])
            index_results["extracted_entities"] = "indexes created: certificate_id, type"

            # 5. classifications: certificate_id
            class_col = self._db["classifications"]
            class_col.create_index([("certificate_id", ASCENDING)])
            index_results["classifications"] = "indexes created: certificate_id"

            # 6. skills: user_id, skill_name
            skills_col = self._db["skills"]
            skills_col.create_index([("user_id", ASCENDING), ("skill_name", ASCENDING)])
            index_results["skills"] = "indexes created: user_id, skill_name"

            # 7. processing_jobs: certificate_id, status
            jobs_col = self._db["processing_jobs"]
            jobs_col.create_index([("certificate_id", ASCENDING)])
            jobs_col.create_index([("status", ASCENDING)])
            index_results["processing_jobs"] = "indexes created: certificate_id, status"

            # 8. model_predictions: certificate_id
            preds_col = self._db["model_predictions"]
            preds_col.create_index([("certificate_id", ASCENDING)])
            index_results["model_predictions"] = "indexes created: certificate_id"

            # 9. model_experiments: experiment_id
            exp_col = self._db["model_experiments"]
            exp_col.create_index([("experiment_id", ASCENDING)], unique=True, sparse=True)
            index_results["model_experiments"] = "indexes created: experiment_id (unique)"

            # 10. user_corrections: certificate_id, user_id
            corr_col = self._db["user_corrections"]
            corr_col.create_index([("certificate_id", ASCENDING)])
            corr_col.create_index([("user_id", ASCENDING)])
            index_results["user_corrections"] = "indexes created: certificate_id, user_id"

            # 11. verification_records: certificate_id
            verif_col = self._db["verification_records"]
            verif_col.create_index([("certificate_id", ASCENDING)])
            index_results["verification_records"] = "indexes created: certificate_id"

            # 12. portfolio_profiles: user_id
            portfolio_col = self._db["portfolio_profiles"]
            portfolio_col.create_index([("user_id", ASCENDING)], unique=True, sparse=True)
            index_results["portfolio_profiles"] = "indexes created: user_id (unique)"

            # 13. notifications: user_id, created_at
            notif_col = self._db["notifications"]
            notif_col.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
            index_results["notifications"] = "indexes created: user_id, created_at"

            logger.info("MongoDB Atlas indexes created successfully.")
            return {"status": "success", "indexes": index_results}

        except PyMongoError as e:
            logger.warning(f"Error creating indexes on MongoDB Atlas: {e}")
            return {"status": "error", "error": str(e)}


# Global database manager instance
db_manager = MongoDBManager()


def get_database() -> Optional[Database]:
    """Dependency helper: get active MongoDB database."""
    return db_manager.get_database()


def get_collection(name: str) -> Optional[Collection]:
    """Helper: get a MongoDB collection by name."""
    return db_manager.get_collection(name)


def check_mongodb_health() -> Dict[str, Any]:
    """
    Check MongoDB connection health for health endpoint.
    Returns status and connectivity without leaking credentials.
    """
    if not settings.is_mongodb_configured:
        return {
            "status": "degraded",
            "database": "disconnected",
            "reason": "MongoDB URI placeholder not configured",
            "database_name": settings.MONGODB_DATABASE,
        }

    is_ok, msg = db_manager.ping()
    if is_ok:
        return {
            "status": "ok",
            "database": "connected",
            "database_name": settings.MONGODB_DATABASE,
        }
    else:
        return {
            "status": "degraded",
            "database": "disconnected",
            "reason": msg,
            "database_name": settings.MONGODB_DATABASE,
        }
