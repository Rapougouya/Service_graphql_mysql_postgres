# metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import time
import threading
from kafka import KafkaConsumer, KafkaProducer
import json
from datetime import datetime

# ==================== MÉTRIQUES GRAPHQL ====================

GRAPHQL_REQUESTS = Counter(
    'graphql_requests_total',
    'Nombre total de requêtes GraphQL',
    ['operation', 'success']
)

GRAPHQL_RESPONSE_TIME = Histogram(
    'graphql_response_time_seconds',
    'Temps de réponse pour les requêtes GraphQL',
    ['operation']
)

# ==================== MÉTRIQUES KAFKA ====================

KAFKA_MESSAGES_SENT = Counter(
    'kafka_messages_sent_total',
    'Nombre de messages envoyés à Kafka',
    ['topic']
)

KAFKA_MESSAGES_RECEIVED = Counter(
    'kafka_messages_received_total',
    'Nombre de messages reçus de Kafka',
    ['topic']
)

KAFKA_PRODUCER_ERRORS = Counter(
    'kafka_producer_errors_total',
    'Nombre d\'erreurs du producteur Kafka',
)

# ==================== MÉTRIQUES EMPLOYÉS ====================

EMPLOYEES_BY_DEPARTMENT = Gauge(
    'employees_by_department',
    'Nombre d\'employés par département',
    ['department']
)

# ==================== MÉTRIQUES TEMPS RÉPONSE API ====================

API_RESPONSE_TIME = Histogram(
    'api_response_time_seconds',
    'Temps de réponse pour les points de terminaison API',
    ['endpoint', 'method']
)

# ==================== FONCTIONS UTILITAIRES ====================

def record_graphql_metrics(operation_name, success, duration):
    """Enregistrer les métriques GraphQL"""
    GRAPHQL_REQUESTS.labels(operation=operation_name, success=success).inc()
    GRAPHQL_RESPONSE_TIME.labels(operation=operation_name).observe(duration)

def record_kafka_message_sent(topic):
    """Enregistrer l'envoi d'un message Kafka"""
    KAFKA_MESSAGES_SENT.labels(topic=topic).inc()

def record_kafka_message_received(topic):
    """Enregistrer la réception d'un message Kafka"""
    KAFKA_MESSAGES_RECEIVED.labels(topic=topic).inc()

def record_kafka_producer_error():
    """Enregistrer une erreur producteur Kafka"""
    KAFKA_PRODUCER_ERRORS.inc()

def record_api_response_time(endpoint, method, duration):
    """Enregistrer le temps de réponse API"""
    API_RESPONSE_TIME.labels(endpoint=endpoint, method=method).observe(duration)

def update_employees_metrics_demo():
    """Mettre à jour les métriques employés (données de démonstration)"""
    try:
        # Données simulées pour les tests
        departments_data = {
            'IT': 15,
            'HR': 8, 
            'Finance': 12,
            'Marketing': 10,
            'Sales': 9
        }
        
        for department, count in departments_data.items():
            EMPLOYEES_BY_DEPARTMENT.labels(department=department).set(count)
            
        print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Demo employee metrics updated")
            
    except Exception as e:
        print(f"❌ Error updating demo employee metrics: {e}")

# ==================== COLLECTEUR DE MÉTRIQUES DE DÉMO ====================

def demo_metrics_collector():
    """Collecteur de démonstration pour générer des données de test"""
    while True:
        try:
            # Générer des métriques de démonstration
            update_employees_metrics_demo()
            
            # Simuler quelques messages Kafka
            record_kafka_message_sent('employes-sync')
            record_kafka_message_received('employes-sync')
            
        except Exception as e:
            print(f"❌ Demo metrics collector error: {e}")
        
        # Attendre 30 secondes entre les mises à jour
        time.sleep(30)

# Démarrer le collecteur de démonstration en arrière-plan
def start_demo_metrics():
    """Démarrer le collecteur de métriques de démonstration"""
    try:
        demo_thread = threading.Thread(target=demo_metrics_collector, daemon=True)
        demo_thread.start()
        print("🚀 Demo metrics collector started...")
    except Exception as e:
        print(f"❌ Failed to start demo metrics collector: {e}")

# Démarrer automatiquement au chargement du module
start_demo_metrics()