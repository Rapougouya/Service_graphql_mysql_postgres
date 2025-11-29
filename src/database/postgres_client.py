from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote
from src.config.settings import settings
from src.database.models import BasePostgres, EmployePostgreSQL

class PostgreSQLClient:
    def __init__(self):
        user = quote(settings.postgres_user, safe='')
        password = quote(settings.postgres_password, safe='')
        
        self.engine = create_engine(
            f"postgresql+psycopg://{user}:{password}@"
            f"{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_database}"
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        BasePostgres.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()

    def create_tables(self):
        BasePostgres.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()