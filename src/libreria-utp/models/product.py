class Categoria:
    """Representa una categoría de producto."""
    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion

    def __str__(self):
        return f"Categoría: {self.nombre}"

    def to_dict(self):
        return {
            'nombre': self.nombre,
            'descripcion': self.descripcion
        }

    @staticmethod
    def from_dict(data):
        return Categoria(
            nombre=data['nombre'],
            descripcion=data['descripcion']
        )

class Producto:
    """Representa un producto en el sistema."""
    def __init__(self, nro_serie, nombre, descripcion, precio, stock, categoria, color, dimensiones):
        self.nro_serie = nro_serie
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = float(precio)
        self.stock = int(stock)
        self.categoria = categoria # Nombre de la Categoria
        self.color = color
        self.dimensiones = dimensiones

    def __str__(self):
        return f"[{self.nro_serie}] {self.nombre} | S/ {self.precio:.2f} | Stock: {self.stock}"

    def to_dict(self):
        return {
            'nro_serie': self.nro_serie,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': str(self.precio),
            'stock': str(self.stock),
            'categoria': self.categoria,
            'color': self.color,
            'dimensiones': self.dimensiones
        }

    @staticmethod
    def from_dict(data):
        return Producto(
            nro_serie=data['nro_serie'],
            nombre=data['nombre'],
            descripcion=data['descripcion'],
            precio=data['precio'],
            stock=data['stock'],
            categoria=data['categoria'],
            color=data['color'],
            dimensiones=data['dimensiones']
        )