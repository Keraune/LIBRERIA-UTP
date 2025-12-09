from models.order import Pedido
from typing import List

def is_cliente_vip(cliente_dni: str, pedidos_list: List[Pedido]) -> bool:
    """
    REGLA LÓGICA: Determina si un cliente es VIP (cliente frecuente).
    Un cliente es VIP si tiene más de 5 pedidos completados (ENTREGADOS).
    """
    pedidos_completados = [
        p for p in pedidos_list
        if p.cliente_dni == cliente_dni and p.get_estado() == "ENTREGADO"
    ]
    
    return len(pedidos_completados) > 5

def is_low_stock(producto_stock: int) -> bool:
    """
    REGLA LÓGICA: Determina si un producto tiene bajo stock.
    Stock bajo es si la cantidad es menor a 10.
    """
    return producto_stock < 10

def get_next_nro_pedido(pedidos_list: List[Pedido]) -> str:
    """Genera el siguiente número de pedido de forma secuencial (P001, P002...)."""
    if not pedidos_list:
        return "P001"
    
    # Obtener el último número y extraer la parte numérica.
    ultimo_pedido = max(pedidos_list, key=lambda p: int(p.nro_pedido[1:]) if p.nro_pedido.startswith('P') else 0)
    
    try:
        # Extraer el número, convertir a entero, sumar 1
        ultimo_num = int(ultimo_pedido.nro_pedido[1:])
        siguiente_num = ultimo_num + 1
    except:
        # En caso de error de formato, empezar de 1
        siguiente_num = 1
        
    # Formatear a 'P' seguido de 3 dígitos (ej: P005)
    return f"P{siguiente_num:03d}"