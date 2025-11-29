from src.database.connection_pool import get_mysql_client, get_postgres_client

def init_databases():
    print("👉 Creation des tables MySQL...")
    try:
        get_mysql_client().create_tables()  # ← Appel direct
        print("✅ Tables MySQL créées")
    except Exception as e:
        print(f"❌ Erreur MySQL: {e}")

    print("👉 Creation des tables PostgreSQL...")
    try:
        get_postgres_client().create_tables()  # ← Appel direct
        print("✅ Tables PostgreSQL créées")
    except Exception as e:
        print(f"⚠️ PostgreSQL non disponible: {e}")
        print("➡️ Continuation sans PostgreSQL...")