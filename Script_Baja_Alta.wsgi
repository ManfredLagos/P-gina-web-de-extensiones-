import sys
import os

from pathlib import Path

# Añadir la ruta de la aplicación
sys.path.insert(0, str(Path(__file__).resolve().parent))

os.environ['FLASK_APP'] = 'conexiónDB'

from conexiónDB import conexiónDB as application  # Reemplaza 'app' con el nombre de tu aplicación Flask
