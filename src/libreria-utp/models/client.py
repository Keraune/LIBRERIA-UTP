class Cliente:
    """Representa un cliente en el sistema."""
    def __init__(self, dni, nombres, apellidos, direccion, distrito, correo, celular):
        self.dni = dni
        self.nombres = nombres
        self.apellidos = apellidos
        self.direccion = direccion
        self.distrito = distrito
        self.correo = correo
        self.celular = celular

    def __str__(self):
        return f"Cliente: {self.nombres} {self.apellidos} (DNI: {self.dni})"
    
    def get_full_name(self):
        return f"{self.nombres} {self.apellidos}"
    
    def to_dict(self):
        return {
            'dni': self.dni,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'direccion': self.direccion,
            'distrito': self.distrito,
            'correo': self.correo,
            'celular': self.celular
        }

    @staticmethod
    def from_dict(data):
        return Cliente(
            dni=data['dni'],
            nombres=data['nombres'],
            apellidos=data['apellidos'],
            direccion=data['direccion'],
            distrito=data['distrito'],
            correo=data['correo'],
            celular=data['celular']
        )