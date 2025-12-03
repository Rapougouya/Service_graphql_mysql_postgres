FROM python:3.11-slim

WORKDIR /app

# Copier requirements depuis le contexte racine
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code source
COPY src/ ./src/

CMD ["python", "-m", "src.etl.kafka_consumer"]
