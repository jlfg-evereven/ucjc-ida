# get_product.py
import json

# Simulación de base de datos de productos
products_db = [
    {
        "id": "1",
        "name": "Collar para perro",
        "description": "Collar ajustable de nylon",
        "price": 15.99,
        "category": "Accesorios",
        "stock": 100
    },
    {
        "id": "2",
        "name": "Pienso Premium",
        "description": "Alimento completo para perros adultos",
        "price": 29.99,
        "category": "Alimentación",
        "stock": 50
    },
    {
        "id": "3",
        "name": "Juguete para gatos",
        "description": "Ratón de peluche con sonido",
        "price": 7.99,
        "category": "Juguetes",
        "stock": 75
    }
]

def main(context=None):
    try:
        # Si hay context, podemos usar los parámetros
        if context and hasattr(context, 'request') and hasattr(context.request, 'query'):
            product_id = context.request.query.get('id', None)
            if product_id:
                product = next((p for p in products_db if p["id"] == product_id), None)
                if product:
                    return {
                        "status": 200,
                        "body": json.dumps(product)
                    }
                else:
                    return {
                        "status": 404,
                        "body": json.dumps({"error": "Producto no encontrado"})
                    }
        
        # Si no hay context o no hay ID, devolvemos todos los productos
        return {
            "status": 200,
            "body": json.dumps(products_db)
        }
            
    except Exception as e:
        return {
            "status": 500,
            "body": json.dumps({"error": str(e)})
        }