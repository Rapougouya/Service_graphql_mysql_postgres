from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.settings import settings
from src.database.models import BaseMysql, EmployeMySQL

class MySQLClient:
    def __init__(self):
        user = quote(settings.mysql_user, safe='')
        password = quote(settings.mysql_password, safe='')
        
        self.engine = create_engine(
            f"mysql+mysqlconnector://{user}:{password}@"
            f"{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}"
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        BaseMysql.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()

    def create_tables(self):
        BaseMysql.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()

