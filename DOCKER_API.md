# Service GraphQL Employés - Documentation

## 📋 Vue d'ensemble

Votre projet est une **API FastAPI GraphQL** avec:
- **Framework**: FastAPI + Strawberry GraphQL
- **Bases de données**: PostgreSQL + MySQL
- **Message Queue**: Kafka (ETL)
- **Monitoring**: Prometheus + Metrics

## 🚀 Architecture

```
┌─────────────────────────────────────────────┐
│        GraphQL API (FastAPI)                │
│        Port: 8000                           │
├──────────────┬──────────────┬───────────────┤
│   PostgreSQL │    MySQL     │     Kafka     │
│   Port 5432  │  Port 3306   │   Port 9092   │
└──────────────┴──────────────┴───────────────┘
```

## 🐳 Créer et déployer avec Docker

### 1. **Construire l'image Docker**

```bash
# Dans le répertoire du projet
docker build -t graphql-api:latest .

# Ou avec docker-compose
docker-compose build graphql-api
```

### 2. **Démarrer l'application avec Docker**

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f graphql-api

# Arrêter les services
docker-compose down
```

### 3. **Variables d'environnement**

Les variables suivantes sont définies dans `docker-compose.yml`:

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=entreprise

MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DB=entreprise

KAFKA_BOOTSTRAP_SERVERS=kafka:9092
API_HOST=0.0.0.0
API_PORT=8000
```

## 📡 Endpoints de l'API

### GraphQL
- **Endpoint**: `http://localhost:8000/graphql`
- **Playground**: `http://localhost:8000/graphql` (interface interactive)

### API REST
- **Health Check**: `http://localhost:8000/health`
- **Root**: `http://localhost:8000/`
- **Docs**: `http://localhost:8000/docs` (Swagger)

## 🔧 Détails de l'implémentation

### Fichier principal: `src/main.py`

L'API démarre les services suivants au startup:

1. **Initialisation des bases de données** (PostgreSQL + MySQL)
2. **Démarrage du consommateur Kafka** (dans un thread séparé)
3. **Exposition du schéma GraphQL**

### Schéma GraphQL: `src/graphql/schema.py`

Définit les requêtes (`Query`) et mutations (`Mutation`) disponibles.

### Database Clients: `src/database/connection_pool.py`

Gère les connexions aux bases de données:
- `MySQLClient`: Connexion MySQL avec SQLAlchemy
- `PostgreSQLClient`: Connexion PostgreSQL avec SQLAlchemy

### ETL Kafka: `src/etl/`

- `kafka_consumer.py`: Consomme les messages des employés
- `kafka_producer.py`: Produit les messages
- `transformers.py`: Transforme les données

## 🐛 Dépannage

### Erreur de connexion PostgreSQL

Si vous avez une erreur `psycopg2.OperationalError`:

1. Vérifiez que PostgreSQL est en cours d'exécution:
   ```bash
   docker-compose ps postgres
   ```

2. Testez la connexion:
   ```bash
   psql -U postgres -h localhost -d entreprise
   ```

3. Consultez les logs:
   ```bash
   docker-compose logs postgres
   ```

### Erreur Kafka

Si le consommateur Kafka ne démarre pas:

```bash
docker-compose logs kafka
```

## 📦 Structure du projet

```
├── src/
│   ├── main.py                 # Point d'entrée FastAPI
│   ├── config/settings.py      # Configuration
│   ├── database/
│   │   ├── connection_pool.py  # Clients MySQL/PostgreSQL
│   │   ├── models.py           # Modèles SQLAlchemy
│   │   └── ...
│   ├── graphql/
│   │   ├── schema.py           # Schéma Strawberry
│   │   └── ...
│   ├── etl/
│   │   ├── kafka_consumer.py   # Consommateur Kafka
│   │   └── ...
│   └── monitoring/
│       └── metrics.py          # Métriques Prometheus
├── docker-compose.yml          # Configuration Docker
├── Dockerfile                  # Image Docker pour l'API
├── requirements.txt            # Dépendances Python
└── README.md                   # Cette documentation
```

## 🔐 Configuration de production

Pour la production, modifiez:

1. **Dockerfile**: Changez `CMD` pour ne pas utiliser `--reload`
2. **docker-compose.yml**: Utilisez des secrets pour les mots de passe
3. **Environnement**: Utilisez un fichier `.env.production`

### Exemple pour production

```dockerfile
# Dans Dockerfile
CMD ["gunicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "-w", "4"]
```

Vous devriez installer gunicorn:
```bash
pip install gunicorn
```

## 📊 Monitoring

### Prometheus

Accédez à: `http://localhost:9090`

### Métriques disponibles

Les métriques sont exposées sur `/metrics` (via Prometheus client).

## 🎯 Prochaines étapes

1. Configurer les authentifications (JWT, OAuth)
2. Ajouter les tests unitaires et d'intégration
3. Mettre en place le CI/CD (GitHub Actions)
4. Optimiser les performances avec du caching
5. Ajouter de la documentation API (OpenAPI)

