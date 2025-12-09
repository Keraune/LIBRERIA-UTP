import csv
import os
from models.client import Cliente
from models.product import Producto, Categoria
from models.order import Pedido
from models.order import DetallePedido

# --- Configuración de Archivos ---
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- Funciones Generales de Persistencia ---

def save_data(filename, data_list, fieldnames):
    """Guarda una lista de objetos que tienen método to_dict() en un archivo CSV."""
    file_path = os.path.join(DATA_DIR, filename)
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in data_list:
                writer.writerow(item.to_dict())
    except Exception as e:
        print(f"Error al guardar datos en {filename}: {e}")

def load_data(filename, class_type, *args):
    """
    Carga datos desde un archivo CSV y los convierte a objetos usando from_dict().
    Maneja excepciones para omitir registros corruptos o incompletos.
    """
    file_path = os.path.join(DATA_DIR, filename)
    data_list = []
    
    if not os.path.exists(file_path):
        return data_list

    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Intenta crear la instancia. Los args adicionales son para Pedido (lista de productos).
                    instance = class_type.from_dict(row, *args)
                    data_list.append(instance)
                except Exception as e:
                    # Omite el registro si está corrupto (ej: ID de producto faltante en Pedido)
                    print(f"Advertencia: No se pudo cargar un registro de '{filename}' (Tipo: {class_type.__name__}). Motivo: {e}")
                    continue
            
        return data_list
    except Exception as e:
        print(f"Error fatal al cargar datos de {filename}: {e}")
        return []

# --- Funciones Específicas del Proyecto (CRUD de Archivos) ---

## CLIENTES
def load_clientes():
    return load_data('clientes.csv', Cliente)

def save_clientes(clientes_list):
    fieldnames = ['dni', 'nombres', 'apellidos', 'direccion', 'distrito', 'correo', 'celular']
    save_data('clientes.csv', clientes_list, fieldnames)

## PRODUCTOS
def load_productos():
    return load_data('productos.csv', Producto)

def save_productos(productos_list):
    fieldnames = ['nro_serie', 'nombre', 'descripcion', 'precio', 'stock', 'categoria', 'color', 'dimensiones']
    save_data('productos.csv', productos_list, fieldnames)

## CATEGORIAS
def load_categorias():
    return load_data('categorias.csv', Categoria)

def save_categorias(categorias_list):
    fieldnames = ['nombre', 'descripcion']
    save_data('categorias.csv', categorias_list, fieldnames)

## PEDIDOS
def load_pedidos(productos_list):
    """Necesita la lista de productos para reconstruir los DetallePedido."""
    return load_data('pedidos.csv', Pedido, productos_list)

def save_pedidos(pedidos_list):
    fieldnames = ['nro_pedido', 'fecha_pedido', 'cliente_dni', 'personal_delivery_dni',
                  'fecha_entrega', 'observaciones', 'subtotal', 'igv', 'total_a_pagar', 'detalles']
    save_data('pedidos.csv', pedidos_list, fieldnames)