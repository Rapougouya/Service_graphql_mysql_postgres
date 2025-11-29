# main.py - Version complète avec métriques HTTP
from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter
import strawberry
import threading
import logging
import time
import asyncio
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, Gauge
from sqlalchemy import text

from src.graphql.schema import Query, Mutation
from src.etl.kafka_consumer import EmployeConsumer
from src.database.connection_pool import get_mysql_client, get_postgres_client
from src.database.models import EmployePostgreSQL
from src.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Créer le schema strawberry
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

# Application FastAPI
app = FastAPI(title="Service GraphQL Employés", version="1.0.0")
app.include_router(graphql_app, prefix="/graphql")

# ==================== MÉTRIQUES HTTP ====================
HTTP_REQUESTS = Counter(
    'fastapi_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

HTTP_REQUEST_DURATION = Histogram(
    'fastapi_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Middleware pour capturer toutes les requêtes HTTP
@app.middleware("http")
async def capture_http_metrics(request: Request, call_next):
    start_time = time.time()
    method = request.method
    endpoint = request.url.path
    
    # Ignorer l'endpoint /metrics lui-même
    if endpoint == "/metrics":
        return await call_next(request)
    
    try:
        response = await call_next(request)
        status_code = str(response.status_code)
        
        # Enregistrer les métriques
        HTTP_REQUESTS.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        duration = time.time() - start_time
        HTTP_REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        return response
        
    except Exception as e:
        # Capturer les erreurs aussi
        HTTP_REQUESTS.labels(
            method=method,
            endpoint=endpoint,
            status_code="500"
        ).inc()
        raise e

# Endpoint Prometheus
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ==================== MÉTRIQUES BUSINESS ====================
GRAPHQL_REQUESTS = Counter('graphql_requests_total', 'Total GraphQL requests', ['operation', 'status'])
GRAPHQL_DURATION = Histogram('graphql_duration_seconds', 'GraphQL request duration', ['operation'])
EMPLOYES_TOTAL = Gauge('entreprise_employes_total', 'Total employees')
EMPLOYES_BY_DEPARTMENT = Gauge('entreprise_employes_par_department', 'Employees by department', ['department'])
DB_CONNECTIONS = Gauge('database_connections', 'DB connections', ['database'])
DB_QUERY_DURATION = Histogram('database_query_duration_seconds', 'DB query duration', ['database', 'operation'])
DB_ERRORS = Counter('database_errors_total', 'DB errors', ['database', 'error_type'])
DB_HEALTH = Gauge('database_health', 'Database health status', ['database'])

# ==================== FONCTIONS HEALTH CHECK ====================
def check_postgresql_health():
    """Vérifier la santé de PostgreSQL"""
    try:
        start_time = time.time()
        postgres_client = get_postgres_client()
        
        if hasattr(postgres_client, 'health_check') and postgres_client.health_check():
            query_time = time.time() - start_time
            DB_QUERY_DURATION.labels(database='postgresql', operation='health_check').observe(query_time)
            DB_HEALTH.labels(database='postgresql').set(1)
            
            with postgres_client.get_session() as session:
                result = session.execute(text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"))
                active_conns = result.scalar()
                DB_CONNECTIONS.labels(database='postgresql').set(active_conns)
            
            logger.info("✅ PostgreSQL health check successful")
            return True
        else:
            DB_HEALTH.labels(database='postgresql').set(0)
            return False
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL health check failed: {e}")
        DB_HEALTH.labels(database='postgresql').set(0)
        DB_ERRORS.labels(database='postgresql', error_type='connection').inc()
        return False

def check_mysql_health():
    """Vérifier la santé de MySQL"""
    try:
        start_time = time.time()
        mysql_client = get_mysql_client()
        
        if hasattr(mysql_client, 'health_check') and mysql_client.health_check():
            query_time = time.time() - start_time
            DB_QUERY_DURATION.labels(database='mysql', operation='health_check').observe(query_time)
            DB_HEALTH.labels(database='mysql').set(1)
            
            with mysql_client.get_session() as session:
                result = session.execute(text("SHOW STATUS LIKE 'Threads_connected'"))
                threads_info = result.fetchone()
                if threads_info:
                    active_conns = int(threads_info[1])
                    DB_CONNECTIONS.labels(database='mysql').set(active_conns)
            
            logger.info("✅ MySQL health check successful")
            return True
        else:
            DB_HEALTH.labels(database='mysql').set(0)
            return False
        
    except Exception as e:
        logger.error(f"❌ MySQL health check failed: {e}")
        DB_HEALTH.labels(database='mysql').set(0)
        DB_ERRORS.labels(database='mysql', error_type='connection').inc()
        return False

def update_business_metrics():
    """Mettre à jour les métriques business"""
    try:
        postgres_client = get_postgres_client()
        with postgres_client.get_session() as session:
            result = session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'employes'
                )
            """))
            table_exists = result.scalar()
            
            if table_exists:
                result = session.execute(text("SELECT COUNT(*) FROM employes"))
                total = result.scalar()
                EMPLOYES_TOTAL.set(total)
                
                result = session.execute(text("SELECT department, COUNT(*) FROM employes GROUP BY department"))
                departments_data = result.fetchall()
                
                for dept, count in departments_data:
                    EMPLOYES_BY_DEPARTMENT.labels(department=dept).set(count)
            else:
                logger.warning("⚠️ Table 'employes' n'existe pas encore")
                
    except Exception as e:
        logger.error(f"❌ Error updating business metrics: {e}")

def update_database_metrics():
    """Mettre à jour toutes les métriques bases de données"""
    try:
        check_postgresql_health()
        check_mysql_health()
    except Exception as e:
        logger.error(f"❌ Error updating database metrics: {e}")

# ==================== ÉVÉNEMENTS APPLICATION ====================
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Démarrage de l'application...")
    
    # Initialisation bases de données
    try:
        mysql_client = get_mysql_client()
        mysql_client.create_tables()
        logger.info("✅ Tables MySQL créées")
    except Exception as e:
        logger.error(f"❌ Erreur MySQL: {e}")

    try:
        postgres_client = get_postgres_client()
        postgres_client.create_tables()
        logger.info("✅ Tables PostgreSQL créées")
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL non disponible: {e}")

    # Tâches de métriques
    async def metrics_updater():
        while True:
            try:
                update_business_metrics()
                update_database_metrics()
            except Exception as e:
                logger.error(f"Error in metrics updater: {e}")
            await asyncio.sleep(30)
    
    asyncio.create_task(metrics_updater())
    logger.info("✅ Mise à jour des métriques démarrée")

    # Kafka (si disponible)
    def start_kafka_consumer():
        try:
            consumer = EmployeConsumer()
            consumer.start_consuming()
        except Exception as e:
            logger.warning(f"⚠️ Kafka non disponible: {e}")

    kafka_thread = threading.Thread(target=start_kafka_consumer, daemon=True)
    kafka_thread.start()
    logger.info("✅ Consommateur Kafka démarré")

# ==================== ENDPOINTS ====================
@app.get("/")
async def root():
    return {"message": "Service GraphQL Employés", "status": "running"}

@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy", 
        "service": "graphql-api",
        "timestamp": time.time(),
        "databases": {
            "postgresql": "healthy" if check_postgresql_health() else "unhealthy",
            "mysql": "healthy" if check_mysql_health() else "unhealthy"
        }
    }
    
    if any(status == "unhealthy" for status in health_status["databases"].values()):
        health_status["status"] = "degraded"
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port, reload=True)