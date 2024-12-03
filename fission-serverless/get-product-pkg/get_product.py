# get_product.py
import json
import psycopg2
import logging
from datetime import datetime
from decimal import Decimal
from psycopg2.extras import RealDictCursor
from flask import request

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la base de datos
DB_CONFIG = {
    'dbname': 'petstore',
    'user': 'postgres',
    'password': 'your_password',
    'host': 'postgres.default.svc.cluster.local',
    'port': '5432'
}

# Clase para manejar la serialización JSON de tipos especiales
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(CustomEncoder, self).default(obj)

def test_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Conexión a base de datos exitosa")
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {str(e)}")
        return False

def main():
    logger.info("Función de obtención de productos iniciada")
    conn = None
    
    try:
        # Obtener parámetros de la query
        product_id = request.args.get('id')
        category = request.args.get('category')
        logger.info(f"Búsqueda por ID: {product_id}, Categoría: {category}")

        # Verificar conexión a BD
        if not test_connection():
            return {
                "status": 500,
                "body": json.dumps({
                    "error": "No se puede conectar a la base de datos"
                })
            }

        # Conectar a la base de datos
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Construir query según los parámetros
        if product_id:
            # Buscar por ID
            query = "SELECT * FROM products WHERE id = %s"
            cur.execute(query, (product_id,))
            result = cur.fetchone()
            
            if not result:
                return {
                    "status": 404,
                    "body": json.dumps({
                        "error": f"Producto con ID {product_id} no encontrado"
                    })
                }
            
            products = dict(result)
            
        elif category:
            # Buscar por categoría
            query = "SELECT * FROM products WHERE category = %s"
            cur.execute(query, (category,))
            results = cur.fetchall()
            products = [dict(row) for row in results]
            
        else:
            # Obtener todos los productos
            query = "SELECT * FROM products"
            cur.execute(query)
            results = cur.fetchall()
            products = [dict(row) for row in results]

        # Cerrar conexión
        cur.close()
        conn.close()

        return {
            "status": 200,
            "body": json.dumps({
                "products": products
            }, cls=CustomEncoder)
        }

    except psycopg2.Error as e:
        logger.error(f"Error de base de datos: {str(e)}")
        if conn:
            conn.close()
        return {
            "status": 500,
            "body": json.dumps({
                "error": "Error de base de datos",
                "details": str(e)
            })
        }
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        logger.error(f"Tipo de error: {type(e)}")
        if conn:
            conn.close()
        return {
            "status": 500,
            "body": json.dumps({
                "error": "Error interno",
                "details": str(e)
            })
        }