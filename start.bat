@echo off
chcp 65001 >nul
echo Demarrage du Projet Service GraphQL...

echo Demarrage des services Docker...
docker-compose up -d

echo Attente du demarrage des services...
timeout /t 20 /nobreak

echo Activation de l'environnement virtuel...
call venv311\Scripts\activate.bat

echo Initialisation des bases de donnees...
python -m src.init_db


echo Demarrage de l'application FastAPI...
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

pause
