from src.database.connection_pool import mysql_client, postgres_client

if __name__ == "__main__":
    mysql_client.create_tables()
    postgres_client.create_tables()
    print('✅ Tables initialisées')
