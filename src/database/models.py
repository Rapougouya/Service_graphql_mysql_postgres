from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
import datetime

# Deux bases séparées
BaseMysql = declarative_base()
BasePostgres = declarative_base()

class EmployeMySQL(BaseMysql):
    __tablename__ = "employes"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    poste = Column(String(100), nullable=False)
    salaire = Column(Float, nullable=False)
    department = Column(String(100), nullable=False)
    date_embauche = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class EmployePostgreSQL(BasePostgres):
    __tablename__ = "employes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(50))
    prenom = Column(String(50))
    email = Column(String(100))
    poste = Column(String(50))
    salaire = Column(Float)
    department = Column(String(50))
    date_embauche = Column(DateTime)
    synced_at = Column(DateTime, default=datetime.datetime.utcnow)