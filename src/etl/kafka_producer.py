from confluent_kafka import Producer, KafkaError
import json
from datetime import datetime
import os
from src.database.connection_pool import get_mysql_client
from src.database.models import EmployeMySQL

class EmployeProducer:
    def __init__(self):
        bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        self.producer = Producer({'bootstrap.servers': bootstrap_servers})
        self.topic = 'employes-sync'

    def sync_all_employes(self):
        mysql_client = get_mysql_client()
        with mysql_client.get_session() as session:
            employes = session.query(EmployeMySQL).all()
            for employe in employes:
                message = {
                    'id': employe.id,
                    'nom': employe.nom,
                    'prenom': employe.prenom,
                    'email': employe.email,
                    'poste': employe.poste,
                    'salaire': float(employe.salaire),
                    'department': employe.department,
                    'date_embauche': employe.date_embauche.isoformat(),
                    'operation': 'SYNC',
                    'timestamp': datetime.utcnow().isoformat()
                }
                self.producer.produce(self.topic, json.dumps(message))
            self.producer.flush()
