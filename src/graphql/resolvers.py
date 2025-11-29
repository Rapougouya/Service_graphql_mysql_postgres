import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.database.connection_pool import mysql_client, postgres_client
from src.database.models import EmployeMySQL, EmployePostgreSQL
from src.etl.kafka_producer import EmployeProducer

logger = logging.getLogger(__name__)


class EmployeResolvers:

    # =========================================================
    #                       QUERIES
    # =========================================================

    @staticmethod
    def get_all_employes() -> List[EmployePostgreSQL]:
        """Lire tous les employés dans PostgreSQL"""
        try:
            with postgres_client.get_session() as session:
                employes = session.query(EmployePostgreSQL).order_by(EmployePostgreSQL.id).all()
                return employes
        except Exception as e:
            logger.error(f"❌ Erreur PostgreSQL : {e}")
            return EmployeResolvers._get_all_employes_mysql_fallback()

    @staticmethod
    def _get_all_employes_mysql_fallback():
        with mysql_client.get_session() as session:
            return session.query(EmployeMySQL).order_by(EmployeMySQL.id).all()

    @staticmethod
    def get_employe_by_id(id: int):
        try:
            with postgres_client.get_session() as session:
                emp = session.query(EmployePostgreSQL).filter_by(id=id).first()
                if emp:
                    return emp
        except:
            pass

        return EmployeResolvers._get_employe_by_id_mysql_fallback(id)

    @staticmethod
    def _get_employe_by_id_mysql_fallback(id: int):
        with mysql_client.get_session() as session:
            return session.query(EmployeMySQL).filter_by(id=id).first()

    @staticmethod
    def get_employes_by_department(department: str):
        try:
            with postgres_client.get_session() as session:
                return session.query(EmployePostgreSQL).filter_by(department=department).all()
        except:
            return EmployeResolvers._get_employes_by_department_mysql_fallback(department)

    @staticmethod
    def _get_employes_by_department_mysql_fallback(department: str):
        with mysql_client.get_session() as session:
            return session.query(EmployeMySQL).filter_by(department=department).all()

    # =========================================================
    #                       MUTATIONS
    # =========================================================

    @staticmethod
    def create_employe(nom, prenom, email, poste, salaire, department):
        """Créer l'employé dans MySQL puis synchroniser"""
        try:
            with mysql_client.get_session() as session:

                exists = session.query(EmployeMySQL).filter_by(email=email).first()
                if exists:
                    raise Exception(f"L'email {email} existe déjà")

                emp = EmployeMySQL(
                    nom=nom,
                    prenom=prenom,
                    email=email,
                    poste=poste,
                    salaire=salaire,
                    department=department,
                )

                session.add(emp)
                session.flush()  # obtenir l’ID après insertion

                # Trigger Kafka sync
                EmployeResolvers._trigger_kafka_sync()

                return emp

        except Exception as e:
            logger.error(f"❌ Erreur création MySQL : {e}")
            raise

    @staticmethod
    def _trigger_kafka_sync():
        try:
            producer = EmployeProducer()
            producer.sync_all_employes()
        except Exception as e:
            logger.warning(f"⚠ Kafka ERREUR : {e}")

    # =========================================================
    #                 STATISTIQUES & SYNCHRO
    # =========================================================

    @staticmethod
    def trigger_sync():
        try:
            producer = EmployeProducer()
            producer.sync_all_employes()
            return "Synchronisation Kafka exécutée."
        except Exception as e:
            logger.error(f"❌ Sync erreur : {e}")
            raise

    @staticmethod
    def get_database_stats() -> Dict[str, Any]:
        try:
            with mysql_client.get_session() as s:
                mysql_count = s.query(EmployeMySQL).count()

            with postgres_client.get_session() as s:
                postgres_count = s.query(EmployePostgreSQL).count()

            return {
                "mysql_count": mysql_count,
                "postgres_count": postgres_count,
                "sync_status": "OK" if mysql_count == postgres_count else "DESYNC",
            }

        except Exception as e:
            logger.error(f"❌ Stats erreur : {e}")
            return {"mysql": 0, "postgres": 0, "sync_status": "ERROR"}


# Instance unique exportée
employe_resolvers = EmployeResolvers()

@staticmethod
def create_employe(nom: str, prenom: str, email: str, poste: str, salaire: float, department: str):
    try:
        client = get_mysql_client()
        with client.get_session() as session:

            # Vérifier doublon email
            existing = session.query(EmployeMySQL).filter_by(email=email).first()
            if existing:
                raise Exception(f"L'email {email} est déjà utilisé")

            nouvel_employe = EmployeMySQL(
                nom=nom,
                prenom=prenom,
                email=email,
                poste=poste,
                salaire=salaire,
                department=department
            )

            session.add(nouvel_employe)
            session.flush()  # récupérer l’ID
            session.refresh(nouvel_employe)  # IMPORTANT

            # === Détacher l’instance avant fermeture session ===
            session.expunge(nouvel_employe)

        # Lancer Kafka après fermeture session
        EmployeResolvers._trigger_kafka_sync()

        return nouvel_employe

    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de l'employé : {e}")
        raise
