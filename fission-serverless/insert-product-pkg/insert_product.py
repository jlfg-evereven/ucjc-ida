# insert_product.py
import json
import psycopg2
import logging
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

# Clase para manejar la serialización JSON de Decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

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
    logger.info("Función iniciada")
    conn = None
    
    try:
        # Obtener datos JSON del request de Flask
        product_data = request.get_json(force=True)
        logger.info(f"Datos recibidos: {product_data}")

        if not product_data:
            return {
                "status": 400,
                "body": json.dumps({
                    "error": "No se recibieron datos del producto"
                })
            }

        # Validar campos requeridos
        required_fields = ['name', 'price', 'category', 'stock']
        missing_fields = [field for field in required_fields if field not in product_data]
        
        if missing_fields:
            return {
                "status": 400,
                "body": json.dumps({
                    "error": "Faltan campos requeridos",
                    "missing_fields": missing_fields
                })
            }

        # Asegurar que description tenga un valor por defecto
        if 'description' not in product_data:
            product_data['description'] = ''

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

        # Construir la query dinámicamente
        fields = list(product_data.keys())
        placeholders = [f"%({field})s" for field in fields]
        
        insert_query = f"""
            INSERT INTO products ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
            RETURNING id, name, description, price, category, stock;
        """

        logger.info(f"Query a ejecutar: {insert_query}")
        logger.info(f"Datos a insertar: {product_data}")

        # Ejecutar la inserción
        cur.execute(insert_query, product_data)
        new_product = dict(cur.fetchone())
        
        # Commit y cerrar conexión
        conn.commit()
        cur.close()
        conn.close()

        logger.info("Producto insertado exitosamente")
        return {
            "status": 201,
            "body": json.dumps({
                "message": "Producto creado exitosamente",
                "product": new_product
            }, cls=DecimalEncoder)
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