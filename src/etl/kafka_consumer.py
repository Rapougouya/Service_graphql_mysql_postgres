# src/etl/kafka_consumer.py
import json
import logging
from kafka import KafkaConsumer
from sqlalchemy import text

from src.database.connection_pool import get_mysql_client, get_postgres_client
from src.config.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class EmployeConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            settings.kafka_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='employe-sync-group'
        )
        self.mysql_client = get_mysql_client()
        self.postgres_client = get_postgres_client()

    def sync_to_mysql(self, employe_data):
        """Synchroniser vers MySQL"""
        try:
            with self.mysql_client.get_session() as session:
                session.execute(text("""
                    INSERT INTO employes (id, nom, prenom, email, department, poste, salaire, date_embauche)
                    VALUES (:id, :nom, :prenom, :email, :department, :poste, :salaire, :date_embauche)
                    ON DUPLICATE KEY UPDATE
                        nom = VALUES(nom),
                        prenom = VALUES(prenom),
                        email = VALUES(email),
                        department = VALUES(department),
                        poste = VALUES(poste),
                        salaire = VALUES(salaire),
                        date_embauche = VALUES(date_embauche)
                """), employe_data)
                session.commit()
                logger.info(f"✅ Synchronisation MySQL réussie pour employé ID {employe_data['id']}")
        except Exception as e:
            logger.error(f"❌ Erreur synchronisation MySQL: {e}")

    def sync_to_postgresql(self, employe_data):
        """Synchroniser vers PostgreSQL"""
        try:
            with self.postgres_client.get_session() as session:
                session.execute(text("""
                    INSERT INTO employes (id, nom, prenom, email, department, poste, salaire, date_embauche)
                    VALUES (:id, :nom, :prenom, :email, :department, :poste, :salaire, :date_embauche)
                    ON CONFLICT (id) DO UPDATE SET
                        nom = EXCLUDED.nom,
                        prenom = EXCLUDED.prenom,
                        email = EXCLUDED.email,
                        department = EXCLUDED.department,
                        poste = EXCLUDED.poste,
                        salaire = EXCLUDED.salaire,
                        date_embauche = EXCLUDED.date_embauche
                """), employe_data)
                session.commit()
                logger.info(f"✅ Synchronisation PostgreSQL réussie pour employé ID {employe_data['id']}")
        except Exception as e:
            logger.error(f"❌ Erreur synchronisation PostgreSQL: {e}")

    def process_message(self, message):
        """Traiter un message Kafka"""
        try:
            employe_data = message.value
            logger.info(f"📥 Message reçu: {employe_data}")
            
            # Synchroniser vers MySQL et PostgreSQL
            self.sync_to_mysql(employe_data)
            self.sync_to_postgresql(employe_data)
            
            logger.info("✅ Synchronisation terminée pour ce message")
        except Exception as e:
            logger.error(f"❌ Erreur traitement message: {e}")

    def start_consuming(self):
        """Démarrer la consommation des messages"""
        logger.info("🎯 Démarrage du consommateur Kafka...")
        for message in self.consumer:
            self.process_message(message)

if __name__ == "__main__":
    consumer = EmployeConsumer()
    consumer.start_consuming()
