from services import data_manager
from models.client import Cliente
from models.product import Producto, Categoria
from models.order import Pedido
from gui.app import AplicacionLibreria
import os

# --- COLECCIONES GLOBALES DE DATOS ---
clientes = []
productos = []
categorias = []
pedidos = []

# --- Funciones de Inicialización ---
def inicializar_datos():
    """Carga todos los datos persistentes o crea ejemplos si no existen."""
    global clientes, productos, categorias, pedidos
    
    # 1. Cargar datos
    categorias = data_manager.load_categorias()
    productos = data_manager.load_productos()
    clientes = data_manager.load_clientes()
    pedidos = data_manager.load_pedidos(productos)
    
    # 2. Crear datos de prueba si no hay
    
    if not categorias:
        categorias.append(Categoria("Oficina", "Útiles generales de oficina"))
        categorias.append(Categoria("Arquitectura/Ingenierías", "Instrumentos de dibujo y medición"))
        data_manager.save_categorias(categorias) # Guardar
    
    if not productos:
        productos.append(Producto("A001", "Audifono Genius", "Noise Cancelling Blue", 39.90, 50, "Oficina", "Azul", "N/A"))
        productos.append(Producto("A002", "Mouse Genius", "NX-7000 WIRELESS", 30.90, 100, "Oficina", "Azul", "10x5x3"))
        data_manager.save_productos(productos) # Guardar
    
    if not clientes:
        clientes.append(Cliente("70123456", "Juan", "Pérez", "Av. Perú 123", "Lima", "juan@mail.com", "987654321"))
        clientes.append(Cliente("71234567", "Ana", "Gómez", "Calle Falsa 456", "Miraflores", "ana@mail.com", "998877665"))
        # Añadir un Delivery (usando el mismo modelo Cliente)
        clientes.append(Cliente("10000000", "Marco", "Delivery", "Movil", "Movil", "m.d@utp.pe", "900000000"))
        data_manager.save_clientes(clientes) # Guardar

    # 3. Recargar para asegurar que las listas globales contienen los datos
    categorias = data_manager.load_categorias()
    productos = data_manager.load_productos()
    clientes = data_manager.load_clientes()
    pedidos = data_manager.load_pedidos(productos)


def main():
    inicializar_datos()
    
    # Inicializar la aplicación principal con las colecciones de datos
    app = AplicacionLibreria(clientes, productos, categorias, pedidos)
    app.mainloop()

if __name__ == "__main__":
    main()