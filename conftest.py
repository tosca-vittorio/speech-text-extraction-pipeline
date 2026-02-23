import sys
import os

# Ottengo il path assoluto della root del progetto
PROJECT_ROOT = os.path.dirname(__file__)
# Punto a src/ che contiene il tuo package
SRC_PATH = os.path.join(PROJECT_ROOT, "src")

# Inserisco src/ in testa a sys.path così import package.* funziona
sys.path.insert(0, SRC_PATH)
