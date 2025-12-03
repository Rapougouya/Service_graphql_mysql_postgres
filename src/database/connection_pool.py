# src/database/connection_pool.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class DatabaseClient:
    def __init__(self, database_url: str, base_class=None):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.base_class = base_class
        self.SessionLocal = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )
    
    def get_session(self):
        return self.SessionLocal()
    
    def create_tables(self):
        if self.base_class is None:
            logger.warning("⚠️ Pas de base_class défini pour créer les tables")
            return
        try:
            self.base_class.metadata.create_all(bind=self.engine)
            logger.info("✅ Tables créées avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur création tables: {e}")
            raise
    
    def health_check(self):
        """Vérification de santé de la base de données"""
        try:
            with self.get_session() as session:
                result = session.execute(text("SELECT 1"))
                result.scalar()
                return True
        except SQLAlchemyError as e:
            logger.error(f"❌ Erreur session {self.__class__.__name__} : {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur inattendue {self.__class__.__name__} : {e}")
            return False

class MySQLClient(DatabaseClient):
    def __init__(self):
        from src.config.settings import settings
        from src.database.models import BaseMysql
        super().__init__(settings.mysql_url, base_class=BaseMysql)

class PostgreSQLClient(DatabaseClient):
    def __init__(self):
        from src.config.settings import settings
        from src.database.models import BasePostgres
        super().__init__(settings.postgres_url, base_class=BasePostgres)

# Clients globaux
_mysql_client = None
_postgres_client = None

def get_mysql_client():
    global _mysql_client
    if _mysql_client is None:
        _mysql_client = MySQLClient()
    return _mysql_client

def get_postgres_client():
    global _postgres_client
    if _postgres_client is None:
        _postgres_client = PostgreSQLClient()
    return _postgres_client
