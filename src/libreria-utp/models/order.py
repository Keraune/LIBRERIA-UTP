from models.product import Producto

class DetallePedido:
    """Representa una línea de producto dentro de un pedido."""
    def __init__(self, producto: Producto, cantidad: int):
        self.producto = producto
        self.cantidad = max(1, int(cantidad))
        self.subtotal_linea = self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} | S/ {self.subtotal_linea:.2f}"
    
    def to_dict(self):
        return {
            'nro_serie': self.producto.nro_serie,
            'cantidad': str(self.cantidad)
        }
    
class Pedido:
    """Representa la transacción de un Pedido en el sistema."""
    
    IGV_TASA = 0.18 # Tasa del Impuesto General a las Ventas (IGV) en Perú

    def __init__(self, nro_pedido, fecha_pedido, cliente_dni, personal_delivery_dni, fecha_entrega=None, observaciones="", subtotal=0.0, igv=0.0, total_a_pagar=0.0):
        self.nro_pedido = nro_pedido # Clave única del pedido
        self.fecha_pedido = fecha_pedido
        self.cliente_dni = cliente_dni # DNI del cliente que realiza la compra
        self.personal_delivery_dni = personal_delivery_dni # DNI del personal de delivery
        self.fecha_entrega = fecha_entrega # Puede ser None si aún no se entrega
        self.observaciones = observaciones
        self.detalles = [] # Lista de objetos DetallePedido
        
        self.subtotal = float(subtotal)
        self.igv = float(igv)
        self.total_a_pagar = float(total_a_pagar)

    def agregar_detalle(self, detalle: DetallePedido):
        """Añade un DetallePedido y recalcula los totales."""
        self.detalles.append(detalle)
        self.calcular_totales()

    def calcular_totales(self):
        """Recalcula Subtotal, IGV y Total a Pagar en base a los detalles."""
        self.subtotal = sum(d.subtotal_linea for d in self.detalles)
        self.igv = round(self.subtotal * self.IGV_TASA, 2)
        self.total_a_pagar = round(self.subtotal + self.igv, 2)

    def registrar_entrega(self, fecha_entrega, observaciones=""):
        """Marca el pedido como entregado y registra la fecha."""
        self.fecha_entrega = fecha_entrega
        self.observaciones = observaciones
    
    def get_estado(self):
        return "ENTREGADO" if self.fecha_entrega else "PENDIENTE"

    def to_dict(self):
        """Convierte el objeto Pedido a un diccionario para ser guardado."""
        detalles_str = "|".join([f"{d.producto.nro_serie}-{d.cantidad}" for d in self.detalles])
        
        return {
            'nro_pedido': self.nro_pedido,
            'fecha_pedido': self.fecha_pedido,
            'cliente_dni': self.cliente_dni,
            'personal_delivery_dni': self.personal_delivery_dni,
            'fecha_entrega': self.fecha_entrega if self.fecha_entrega else '',
            'observaciones': self.observaciones,
            'subtotal': str(self.subtotal),
            'igv': str(self.igv),
            'total_a_pagar': str(self.total_a_pagar),
            'detalles': detalles_str
        }

    @classmethod
    def from_dict(cls, data, productos_list):
        """Reconstruye un objeto Pedido desde un diccionario (requiere la lista de productos)."""
        pedido = cls(
            nro_pedido=data['nro_pedido'],
            fecha_pedido=data['fecha_pedido'],
            cliente_dni=data['cliente_dni'],
            personal_delivery_dni=data['personal_delivery_dni'],
            fecha_entrega=data.get('fecha_entrega') if data.get('fecha_entrega') else None,
            observaciones=data.get('observaciones', ''),
            subtotal=data.get('subtotal', '0.0'),
            igv=data.get('igv', '0.0'),
            total_a_pagar=data.get('total_a_pagar', '0.0')
        )
        
        detalles_raw = data.get('detalles', '').split('|')
        
        for detalle_item in detalles_raw:
            if not detalle_item:
                continue
            
            try:
                nro_serie, cantidad_str = detalle_item.split('-')
                cantidad = int(cantidad_str)
            except ValueError:
                continue
            
            producto_encontrado = next((p for p in productos_list if p.nro_serie == nro_serie), None)
            
            if producto_encontrado:
                detalle = DetallePedido(producto_encontrado, cantidad)
                # Al cargar, solo agregamos el detalle para su estructura
                pedido.detalles.append(detalle)
                
        return pedido