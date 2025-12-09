import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from services import data_manager
from models.order import Pedido
from typing import List

class RegistroEntregaFrame(tk.Frame):
    """Vista/Frame para registrar la entrega de un pedido."""

    def __init__(self, parent_container, app_controller, data):
        super().__init__(parent_container)
        self.app = app_controller
        self.clientes = data['clientes']
        self.pedidos = [] # Se cargará con pedidos PENDIENTES en reset_filter()
        self.pedido_seleccionado: Pedido = None

        self.create_widgets()
        self.reset_filter() # Carga inicial de pedidos PENDIENTES al iniciar

    def create_widgets(self):
        
        # 1. Panel de Búsqueda
        search_frame = tk.LabelFrame(self, text="Buscar Pedido PENDIENTE", padx=10, pady=10)
        search_frame.pack(padx=10, pady=10, fill="x")
        
        tk.Label(search_frame, text="Buscar por:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        self.search_by_var = tk.StringVar(value="DNI Cliente")
        ttk.Combobox(search_frame, textvariable=self.search_by_var, values=["DNI Cliente", "DNI Delivery"], state='readonly', width=15).grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(search_frame, text="Valor:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.search_value_entry = tk.Entry(search_frame, width=20)
        self.search_value_entry.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Button(search_frame, text="Filtrar", command=self.filtrar_pedidos).grid(row=1, column=2, padx=10, pady=5)
        ttk.Button(search_frame, text="Mostrar Todos", command=self.reset_filter).grid(row=1, column=3, padx=10, pady=5)


        # 2. Treeview de Pedidos Pendientes
        tree_frame = tk.Frame(self)
        tree_frame.pack(padx=10, pady=5, fill="both", expand=True)

        columns = ("Nro. Pedido", "Fecha Pedido", "Cliente DNI", "Cliente Nombre", "Total", "Delivery DNI", "Estado")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.W)
            self.tree.column(col, width=100)
        
        self.tree.bind('<<TreeviewSelect>>', self.item_selected)
        self.tree.pack(side="left", fill="both", expand=True)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        # 3. Panel de Registro de Entrega
        delivery_frame = tk.LabelFrame(self, text="Registrar Entrega", padx=10, pady=10)
        delivery_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(delivery_frame, text="Pedido Seleccionado:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.selected_pedido_var = tk.StringVar(value="---")
        tk.Label(delivery_frame, textvariable=self.selected_pedido_var, font=('Arial', 10, 'bold')).grid(row=0, column=1, sticky="w", padx=5, pady=2, columnspan=3)

        tk.Label(delivery_frame, text="Fecha de Entrega (AAAA-MM-DD):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.fecha_entrega_entry = tk.Entry(delivery_frame, width=20)
        # Establecer la fecha actual por defecto
        self.fecha_entrega_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) 
        self.fecha_entrega_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        tk.Label(delivery_frame, text="Observaciones:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.obs_entry = tk.Entry(delivery_frame, width=40)
        self.obs_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2, columnspan=2)

        ttk.Button(delivery_frame, text="✅ CONFIRMAR ENTREGA", command=self.confirmar_entrega, style='TButton', padding=10).grid(row=3, column=0, columnspan=4, pady=10)

    # --- Métodos de Control ---

    def load_pedidos_treeview(self, pedidos_source: List[Pedido]):
        """Carga los datos de la lista de pedidos (filtrados o todos) al Treeview, mostrando SOLO PENDIENTES."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filtrar solo pedidos pendientes
        pedidos_pendientes = [p for p in pedidos_source if p.get_estado() == "PENDIENTE"]
        
        for pedido in pedidos_pendientes:
            cliente = next((c for c in self.clientes if c.dni == pedido.cliente_dni), None)
            cliente_nombre = cliente.get_full_name() if cliente else "N/A"
            
            self.tree.insert('', tk.END, iid=pedido.nro_pedido, values=(
                pedido.nro_pedido,
                pedido.fecha_pedido,
                pedido.cliente_dni,
                cliente_nombre,
                f"S/ {pedido.total_a_pagar:.2f}",
                pedido.personal_delivery_dni,
                pedido.get_estado()
            ))


    def filtrar_pedidos(self):
        """Busca pedidos pendientes por DNI Cliente o DNI Delivery en la lista completa de pedidos."""
        search_by = self.search_by_var.get()
        search_value = self.search_value_entry.get().strip()

        if not search_value:
            messagebox.showerror("Error", "Ingrese un valor para buscar.")
            return

        # Recargar la lista de pedidos desde disco para asegurar que está fresca
        productos_frescos = data_manager.load_productos()
        self.pedidos = data_manager.load_pedidos(productos_frescos)
        
        # Filtrar por el criterio de búsqueda
        if search_by == "DNI Cliente":
            pedidos_filtrados = [p for p in self.pedidos if p.cliente_dni == search_value]
        else: # DNI Delivery
            pedidos_filtrados = [p for p in self.pedidos if p.personal_delivery_dni == search_value]

        if not pedidos_filtrados:
             messagebox.showinfo("Búsqueda", f"No se encontraron pedidos para el DNI {search_value}.")

        # load_pedidos_treeview se encarga de mostrar solo los PENDIENTES de esta lista filtrada.
        self.load_pedidos_treeview(pedidos_filtrados)


    def reset_filter(self):
        """Muestra todos los pedidos pendientes y limpia la selección. FUERZA RECARGA TOTAL DESDE DISCO."""
        self.search_value_entry.delete(0, tk.END)
        
        # Sincronización de datos clave: Recargar Productos y Pedidos desde el disco
        productos_frescos = data_manager.load_productos()
        self.pedidos = data_manager.load_pedidos(productos_frescos)
        
        # Sincronizar las listas maestras en el controlador global (buena práctica MVC/MVP)
        self.app.global_data['pedidos'] = self.pedidos
        self.app.global_data['productos'] = productos_frescos

        self.load_pedidos_treeview(self.pedidos)
        self.selected_pedido_var.set("---")
        self.pedido_seleccionado = None
        self.obs_entry.delete(0, tk.END)


    def item_selected(self, event):
        """Carga el objeto Pedido seleccionado para su registro de entrega en la UI inferior."""
        selected_items = self.tree.selection()
        if not selected_items:
            self.pedido_seleccionado = None
            self.selected_pedido_var.set("---")
            return

        nro_pedido = selected_items[0]
        # Buscar el objeto Pedido en la lista maestra (self.pedidos)
        self.pedido_seleccionado = next((p for p in self.pedidos if p.nro_pedido == nro_pedido), None)
        
        if self.pedido_seleccionado:
            self.selected_pedido_var.set(f"{nro_pedido} (Total: S/ {self.pedido_seleccionado.total_a_pagar:.2f})")
            # Cargar y pre-rellenar observaciones
            self.obs_entry.delete(0, tk.END)
            self.obs_entry.insert(0, self.pedido_seleccionado.observaciones or "")
        else:
            self.selected_pedido_var.set("---")


    def confirmar_entrega(self):
        """Actualiza el estado del pedido a ENTREGADO, guarda en disco y refresca la vista."""
        if not self.pedido_seleccionado:
            messagebox.showerror("Error", "Debe seleccionar un pedido pendiente del listado.")
            return

        fecha_entrega = self.fecha_entrega_entry.get().strip()
        observaciones = self.obs_entry.get().strip()
        
        if not fecha_entrega:
            messagebox.showerror("Error", "La fecha de entrega es obligatoria.")
            return

        try:
            # Validación de formato de fecha (AAAA-MM-DD)
            datetime.strptime(fecha_entrega, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha de entrega inválido. Use AAAA-MM-DD.")
            return

        # Actualizar las propiedades del objeto Pedido seleccionado (cambia el estado a ENTREGADO)
        self.pedido_seleccionado.fecha_entrega = fecha_entrega
        self.pedido_seleccionado.observaciones = observaciones
        
        # Persistencia: Guardar la lista completa de pedidos actualizada
        data_manager.save_pedidos(self.pedidos)
        
        messagebox.showinfo("Entrega Registrada", f"El Pedido {self.pedido_seleccionado.nro_pedido} ha sido registrado como ENTREGADO.")

        # Recargar la lista para que el pedido entregado desaparezca del Treeview
        self.reset_filter()