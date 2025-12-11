"""
Vercel Serverless Function wrapper para SmartPlannerX
"""
import sys
from os.path import join, dirname, abspath

# Agregar el directorio raíz al path de Python
root_dir = abspath(join(dirname(__file__), '..'))
sys.path.insert(0, root_dir)

# Importar la aplicación Flask
from app import app as application

# Exportar para Vercel
app = application
