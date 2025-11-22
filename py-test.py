import os
from dotenv import load_dotenv
from pathlib import Path
from google import genai
from google.genai.errors import APIError

# 1. Definir la ruta del archivo .env.
# Esto busca el .env en el directorio actual (donde ejecutas poetry run).
# Se recomienda usar la ruta absoluta.
dotenv_path = Path(__file__).resolve().parent / '.env'

# 2. Forzar la carga de las variables de entorno desde esa ruta.
# 'override=True' asegura que si ya existía una variable, se sobreescriba.
load_dotenv(dotenv_path=dotenv_path, override=True)

# 3. Verificar si la clave se cargó
gemini_key = os.getenv("GEMINI_API_KEY")
print(f"Clave cargada: {gemini_key[:5]}..." if gemini_key else "Clave cargada: None")

if gemini_key:
    try:
        # 4. Intentar inicializar el cliente
        client = genai.Client()
        print("Cliente de Gemini inicializado con éxito. ¡TODO LISTO!")
    except Exception as e:
        print(f"Error al inicializar el cliente (revisar restricciones de la clave): {e}")
else:
    print("Error: GEMINI_API_KEY no se cargó en el entorno después de load_dotenv.")