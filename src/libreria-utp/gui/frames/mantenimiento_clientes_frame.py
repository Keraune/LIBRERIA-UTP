import tkinter as tk
from tkinter import ttk, messagebox
from models.client import Cliente
from services import data_manager

class MantenimientoClientesFrame(tk.Frame):
    """Vista/Frame para gestionar las operaciones CRUD de Clientes."""
    def __init__(self, parent_container, app_controller, clientes_data):
        super().__init__(parent_container)
        self.app = app_controller
        self.clientes = clientes_data
        
        self.create_widgets()
        self.load_clientes_treeview()

    def validate_dni_input(self, text):
        """Permite solo hasta 8 dígitos y verifica que sean numéricos (validación de Entry)."""
        if text.isdigit() or text == "":
            if len(text) <= 8:
                return True
        return False

    def create_widgets(self):
        vcmd = (self.register(self.validate_dni_input), '%P')
        
        # 1. Panel de Entrada de Datos
        input_frame = tk.LabelFrame(self, text="Datos del Cliente", padx=10, pady=10)
        input_frame.pack(padx=10, pady=10, fill="x")

        # Configuración de Labels y Entradas (incluye validación de DNI)
        self.fields = {}
        labels = ['DNI', 'Nombres', 'Apellidos', 'Dirección', 'Distrito', 'Correo', 'Celular']
        
        for i, label_text in enumerate(labels):
            tk.Label(input_frame, text=f"{label_text}:").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            entry = tk.Entry(input_frame, width=40)
            
            if label_text == 'DNI':
                entry.config(validate='key', validatecommand=vcmd) # Aplica la validación de 8 dígitos
            
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.fields[label_text] = entry

        # 2. Panel de Botones
        button_frame = tk.Frame(self)
        button_frame.pack(padx=10, pady=5, fill="x")

        ttk.Button(button_frame, text="Registrar Cliente", command=self.registrar_cliente).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Modificar Cliente", command=self.modificar_cliente).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Eliminar Cliente", command=self.eliminar_cliente).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Limpiar Campos", command=self.limpiar_campos).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🔍 Buscar", command=self.filtrar_clientes).pack(side="right", padx=5)
        
        # Campo de Búsqueda
        self.search_var = tk.StringVar()
        tk.Entry(button_frame, textvariable=self.search_var, width=20).pack(side="right", padx=5)
        tk.Label(button_frame, text="Buscar por DNI/Nombre:").pack(side="right")


        # 3. Panel de Visualización (Treeview)
        tree_frame = tk.Frame(self)
        tree_frame.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ("DNI", "Nombres", "Apellidos", "Dirección", "Distrito", "Correo", "Celular")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Definir encabezados y vincular evento de selección
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.W)
            self.tree.column(col, width=100)

        self.tree.bind('<<TreeviewSelect>>', self.item_selected)
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

    # --- Métodos de Control ---
    
    def load_clientes_treeview(self, clientes_a_mostrar=None):
        """Carga los datos al Treeview. Recibe una lista filtrada opcional."""
        clientes_source = clientes_a_mostrar if clientes_a_mostrar is not None else self.clientes
        
        # Limpiar datos previos
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for cliente in clientes_source:
            # Insertar los valores en el Treeview
            self.tree.insert('', tk.END, values=(
                cliente.dni,
                cliente.nombres,
                cliente.apellidos,
                cliente.direccion,
                cliente.distrito,
                cliente.correo,
                cliente.celular
            ))

    def filtrar_clientes(self):
        """Implementa la lógica de búsqueda por DNI o Nombre/Apellido."""
        search_term = self.search_var.get().strip().lower()
        if not search_term:
            self.load_clientes_treeview(self.clientes)
            return

        # Filtrado de clientes (búsqueda insensible a mayúsculas/minúsculas)
        clientes_filtrados = [
            c for c in self.clientes
            if search_term in c.dni.lower()
            or search_term in c.nombres.lower()
            or search_term in c.apellidos.lower()
        ]
        
        self.load_clientes_treeview(clientes_filtrados)
        if not clientes_filtrados:
              messagebox.showinfo("Búsqueda", "No se encontraron clientes con el criterio ingresado.")


    def item_selected(self, event):
        """Carga los datos del cliente seleccionado en los campos de entrada."""
        selected_items = self.tree.selection()
        if not selected_items: return

        item = self.tree.item(selected_items[0])
        values = item['values']
        
        labels = ['DNI', 'Nombres', 'Apellidos', 'Dirección', 'Distrito', 'Correo', 'Celular']
        
        self.limpiar_campos(keep_search=True)
        
        for i, label in enumerate(labels):
            self.fields[label].insert(0, values[i])
            # Bloquear la edición del DNI para asegurar la clave primaria
            if label == 'DNI':
                self.fields[label].config(state='readonly')
                
    def limpiar_campos(self, keep_search=False):
        """Limpia todos los campos de entrada y desbloquea el DNI."""
        for entry in self.fields.values():
            entry.config(state='normal')
            entry.delete(0, tk.END)
        self.fields['DNI'].config(state='normal')
        
        if not keep_search:
            self.search_var.set("")
            self.load_clientes_treeview()

    def registrar_cliente(self):
        # 1. Obtener y mapear los datos de la UI al modelo Cliente
        ui_data = {key: entry.get() for key, entry in self.fields.items()}
        key_mapping = {
            'DNI': 'dni', 'Nombres': 'nombres', 'Apellidos': 'apellidos',
            'Dirección': 'direccion', 'Distrito': 'distrito',
            'Correo': 'correo', 'Celular': 'celular'
        }
        data = {key_mapping[ui_key]: ui_data[ui_key] for ui_key in ui_data}
        dni = data['dni']

        if not all(ui_data.values()): 
            messagebox.showerror("Error", "Todos los campos deben estar llenos.")
            return
        
        # 2. Validaciones de DNI
        if len(dni) != 8:
             messagebox.showerror("Error", "El DNI debe tener exactamente 8 dígitos.")
             return
             
        if next((c for c in self.clientes if c.dni == dni), None):
            messagebox.showerror("Error", f"Ya existe un cliente con DNI {dni}.")
            return

        try:
            nuevo_cliente = Cliente(**data)
            self.clientes.append(nuevo_cliente)
            self.load_clientes_treeview()
            self.limpiar_campos()
            data_manager.save_clientes(self.clientes) # Persistencia de datos
            messagebox.showinfo("Registro", "Cliente registrado exitosamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el cliente: {e}")

    def modificar_cliente(self):
        dni = self.fields['DNI'].get()
        cliente = next((c for c in self.clientes if c.dni == dni), None)
        
        if not cliente:
            messagebox.showerror("Error", "Debe seleccionar un cliente del listado para modificar.")
            return

        data = {key: entry.get() for key, entry in self.fields.items()}
        
        try:
            # Actualizar directamente los atributos del objeto Cliente
            cliente.nombres = data['Nombres']
            cliente.apellidos = data['Apellidos']
            cliente.direccion = data['Dirección']
            cliente.distrito = data['Distrito']
            cliente.correo = data['Correo']
            cliente.celular = data['Celular']
            
            self.load_clientes_treeview()
            self.limpiar_campos()
            data_manager.save_clientes(self.clientes)
            messagebox.showinfo("Modificación", "Cliente modificado exitosamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar el cliente: {e}")

    def eliminar_cliente(self):
        dni = self.fields['DNI'].get()
        if not dni:
            messagebox.showerror("Error", "Seleccione un cliente para eliminar.")
            return

        if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar el cliente con DNI {dni}?"):
            # Eliminar el cliente usando list comprehension (actualiza la lista en su lugar)
            self.clientes[:] = [c for c in self.clientes if c.dni != dni]
            
            self.load_clientes_treeview()
            self.limpiar_campos()
            data_manager.save_clientes(self.clientes)
            messagebox.showinfo("Eliminación", "Cliente eliminado exitosamente.")