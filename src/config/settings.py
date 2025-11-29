# src/config/settings.py
try:
    # pydantic v2: pydantic-settings provides BaseSettings
    from pydantic_settings import BaseSettings
except Exception:
    # fallback for pydantic v1 where BaseSettings is in pydantic
    from pydantic import BaseSettings

from pydantic import validator
import os
from typing import Optional


class Settings(BaseSettings):
    # Database MySQL
    mysql_host: str = "mysql"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "root"
    mysql_database: str = "entreprise"
    
    # Database PostgreSQL
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_database: str = "entreprise"
    
    # Connection Pools
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600
    
    # Kafka
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic: str = "employes-sync"
    kafka_group_id: str = "employe-sync-group"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_max_requests: int = 1000
    
    # Monitoring
    prometheus_port: int = 9090
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
       env_file = ".env"
       env_file_encoding = "utf-8"  # Forcer l'encodage UTF-8
       case_sensitive = False
    
    @property
    def mysql_url(self) -> str:
        return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
    
    @property
    def postgres_url(self) -> str:
        return f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"


# Crée une instance globale des settings
settings = Settings()


