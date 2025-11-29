@echo off
echo Création de l'environnement virtuel...
python -m venv venv311
call venv311\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
echo ✅ Environnement virtuel créé et dépendances installées
pause