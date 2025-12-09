import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models.order import Pedido, DetallePedido
from models.product import Producto
from services import data_manager
from services.logic_rules import is_cliente_vip, get_next_nro_pedido

class RegistroPedidoFrame(tk.Frame):
    """Vista/Frame para registrar nuevos pedidos."""
    def __init__(self, parent_container, app_controller, data):
        super().__init__(parent_container)
        self.app = app_controller
        self.clientes = data['clientes']
        # self.productos y self.pedidos se usan como referencia, sincronizadas con global_data
        self.productos = data['productos']
        self.pedidos = data['pedidos']
        self.detalle_actual = [] # Lista temporal de DetallePedido para el pedido en curso

        self.create_widgets()
        self.limpiar_campos()

    def update_product_list(self):
        """
        Sincroniza el Combobox de productos con la lista global
        para reflejar el stock actual disponible.
        """
        # Sincronizar self.productos con la lista maestra global
        self.productos = self.app.global_data.get('productos', [])
        
        # Crear formato para Combobox: [Nro. Serie] Nombre (Stock: X)
        product_values = [f"[{p.nro_serie}] {p.nombre} (Stock: {p.stock})" for p in self.productos]
        self.prod_search_entry['values'] = product_values
        self.prod_search_entry.set('') # Limpiar selección
        
    def create_widgets(self):
        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # 1. Cabecera y Cliente
        header_frame = tk.LabelFrame(main_frame, text="Datos del Pedido y Cliente", padx=10, pady=10)
        header_frame.pack(padx=5, pady=5, fill="x")

        # Nro Pedido (Generado automáticamente) y Fechas
        tk.Label(header_frame, text="Nro. Pedido:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.nro_pedido_var = tk.StringVar()
        tk.Label(header_frame, textvariable=self.nro_pedido_var, font=('Arial', 10, 'bold')).grid(row=0, column=1, sticky="w", padx=5, pady=2)

        tk.Label(header_frame, text="Fecha Pedido (Hoy):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.fecha_pedido_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Label(header_frame, textvariable=self.fecha_pedido_var).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # DNI Cliente
        tk.Label(header_frame, text="DNI Cliente:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.cliente_dni_entry = tk.Entry(header_frame, width=15)
        self.cliente_dni_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        ttk.Button(header_frame, text="Buscar Cliente", command=self.buscar_cliente).grid(row=2, column=2, padx=5, pady=2)

        # Nombre Cliente (Mostrar) y DNI Delivery
        tk.Label(header_frame, text="Cliente:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.cliente_nombre_var = tk.StringVar(value="---")
        tk.Label(header_frame, textvariable=self.cliente_nombre_var).grid(row=3, column=1, sticky="w", padx=5, pady=2, columnspan=2)
        
        tk.Label(header_frame, text="DNI Personal Delivery:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.delivery_dni_entry = tk.Entry(header_frame, width=15)
        self.delivery_dni_entry.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        
        # Fecha de Entrega (solo se usa en la vista de registro de entrega, se mantiene para consistencia)
        tk.Label(header_frame, text="Fecha Entrega (YYYY-MM-DD):").grid(row=0, column=3, sticky="w", padx=5, pady=2)
        self.fecha_entrega_entry = tk.Entry(header_frame, width=15)
        self.fecha_entrega_entry.grid(row=0, column=4, sticky="w", padx=5, pady=2)


        # 2. Detalles del Producto
        detail_frame = tk.LabelFrame(main_frame, text="Detalles del Producto", padx=10, pady=10)
        detail_frame.pack(padx=5, pady=5, fill="x")

        tk.Label(detail_frame, text="Nro. Serie/Nombre Producto:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.prod_search_entry = ttk.Combobox(detail_frame, width=40, state="readonly")
        self.prod_search_entry['values'] = [f"[{p.nro_serie}] {p.nombre}" for p in self.productos] 
        self.prod_search_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        tk.Label(detail_frame, text="Cantidad:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.cantidad_entry = tk.Entry(detail_frame, width=10)
        self.cantidad_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        ttk.Button(detail_frame, text="Agregar Producto", command=self.agregar_producto).grid(row=1, column=2, padx=5, pady=2)

        # 3. Treeview de Detalles
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(padx=10, pady=5, fill="both", expand=True)

        columns = ("Nro. Serie", "Producto", "Precio Unitario", "Cantidad", "Subtotal Línea")
        self.tree_det = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree_det.heading(col, text=col, anchor=tk.W)
            self.tree_det.column(col, width=100)
        self.tree_det.column("Producto", width=150)
        
        self.tree_det.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_det.yview)
        vsb.pack(side='right', fill='y')
        self.tree_det.configure(yscrollcommand=vsb.set)


        # 4. Totales y Botón de Registro
        footer_frame = tk.LabelFrame(main_frame, text="Resumen y Totales", padx=10, pady=10)
        footer_frame.pack(padx=5, pady=5, fill="x")

        # Variables de Totales (Subtotal, IGV, Total)
        self.subtotal_var = tk.StringVar(value="0.00")
        self.igv_var = tk.StringVar(value="0.00")
        self.total_var = tk.StringVar(value="0.00")
        self.obs_var = tk.StringVar()

        tk.Label(footer_frame, text="Subtotal: S/").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        tk.Label(footer_frame, textvariable=self.subtotal_var, font=('Arial', 10, 'bold')).grid(row=0, column=1, sticky="e", padx=5, pady=2)

        tk.Label(footer_frame, text="IGV (18%): S/").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        tk.Label(footer_frame, textvariable=self.igv_var, font=('Arial', 10, 'bold')).grid(row=1, column=1, sticky="e", padx=5, pady=2)

        tk.Label(footer_frame, text="Total a Pagar: S/").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        tk.Label(footer_frame, textvariable=self.total_var, font=('Arial', 12, 'bold', 'underline'), foreground='blue').grid(row=2, column=1, sticky="e", padx=5, pady=2)
        
        tk.Label(footer_frame, text="Observaciones:").grid(row=0, column=2, sticky="w", padx=5, pady=2, rowspan=2)
        tk.Entry(footer_frame, textvariable=self.obs_var, width=40).grid(row=0, column=3, sticky="w", padx=5, pady=2, rowspan=2)

        ttk.Button(footer_frame, text="✅ REGISTRAR PEDIDO", command=self.registrar_pedido, style='TButton', padding=10).grid(row=3, column=0, columnspan=4, pady=10)

    def buscar_cliente(self):
        """Busca el cliente por DNI y aplica la regla de negocio VIP."""
        dni = self.cliente_dni_entry.get().strip()
        cliente = next((c for c in self.clientes if c.dni == dni), None)
        
        if cliente:
            self.cliente_nombre_var.set(cliente.get_full_name())
            
            # Aplicación de Regla Lógica: Verificar si es VIP
            if is_cliente_vip(dni, self.pedidos):
                 messagebox.showinfo("Cliente Encontrado", f"Cliente: {cliente.get_full_name()}. ¡Cliente VIP! 🎉")
            else:
                 messagebox.showinfo("Cliente Encontrado", f"Cliente: {cliente.get_full_name()}.")
        else:
            self.cliente_nombre_var.set("Cliente no encontrado. Registre al cliente.")
            messagebox.showerror("Error", "Cliente no encontrado.")

    def agregar_producto(self):
        """
        Agrega un producto al detalle del pedido, validando stock y restándolo
        inmediatamente para simular la reserva (regla de negocio).
        """
        if not self.cliente_nombre_var.get() or self.cliente_nombre_var.get() == "---":
            messagebox.showerror("Error", "Primero debe buscar y validar el DNI del Cliente.")
            return

        prod_text = self.prod_search_entry.get()
        cantidad_str = self.cantidad_entry.get()
        
        if not prod_text or not cantidad_str:
            messagebox.showerror("Error", "Debe seleccionar un producto y la cantidad.")
            return

        try:
            # Extraer Nro. Serie del Combobox: "[Nro. Serie] Nombre..."
            nro_serie = prod_text.split(']')[0][1:]
            cantidad = int(cantidad_str)
            if cantidad <= 0:
                raise ValueError("Cantidad debe ser positiva.")
        except (IndexError, ValueError):
            messagebox.showerror("Error", "Cantidad inválida o formato de producto incorrecto.")
            return

        # Sincronizar productos antes de verificar stock
        self.productos = self.app.global_data.get('productos', self.productos)
        producto = next((p for p in self.productos if p.nro_serie == nro_serie), None)
        
        if not producto:
            messagebox.showerror("Error", "Producto no encontrado.")
            return

        # Validación de stock (Regla de Negocio)
        if cantidad > producto.stock:
            messagebox.showerror("Error", f"Stock insuficiente. Solo quedan {producto.stock} unidades.")
            return

        # Restar del stock global (reserva inmediata)
        producto.stock -= cantidad
        
        # Refrescar Combobox para mostrar stock reducido
        self.update_product_list()
        
        detalle = DetallePedido(producto, cantidad)
        self.detalle_actual.append(detalle)
        self.load_detalles_treeview()
        self.calcular_totales_ui()
        
        self.cantidad_entry.delete(0, tk.END)

    def load_detalles_treeview(self):
        """Carga los detalles del pedido temporal (detalle_actual) en el Treeview."""
        for item in self.tree_det.get_children():
            self.tree_det.delete(item)

        for detalle in self.detalle_actual:
            self.tree_det.insert('', tk.END, values=(
                detalle.producto.nro_serie,
                detalle.producto.nombre,
                f"S/ {detalle.producto.precio:.2f}",
                detalle.cantidad,
                f"S/ {detalle.subtotal_linea:.2f}"
            ))

    def calcular_totales_ui(self):
        """Calcula y actualiza los totales (Subtotal, IGV, Total) en la interfaz."""
        subtotal = sum(d.subtotal_linea for d in self.detalle_actual)
        igv = round(subtotal * Pedido.IGV_TASA, 2)
        total = round(subtotal + igv, 2)

        self.subtotal_var.set(f"{subtotal:.2f}")
        self.igv_var.set(f"{igv:.2f}")
        self.total_var.set(f"{total:.2f}")

    def registrar_pedido(self):
        """
        Crea el objeto Pedido final, lo añade a la lista global,
        guarda los pedidos y el stock modificado en disco y limpia la UI.
        """
        cliente_dni = self.cliente_dni_entry.get().strip()
        personal_delivery_dni = self.delivery_dni_entry.get().strip()

        if not cliente_dni or not personal_delivery_dni:
            messagebox.showerror("Error", "Debe ingresar el DNI del Cliente y DNI del Personal Delivery.")
            return
        
        # 1. Validación de DNI de Cliente
        self.clientes = self.app.global_data.get('clientes', self.clientes)
        cliente = next((c for c in self.clientes if c.dni == cliente_dni), None)
        if not cliente:
            messagebox.showerror("Error", "DNI de Cliente no válido. Debe existir en el sistema.")
            return
            
        # 2. Validación de DNI de Personal Delivery (usamos la misma lista de clientes como fuente)
        delivery_person = next((c for c in self.clientes if c.dni == personal_delivery_dni), None)
        if not delivery_person:
            messagebox.showerror("Error", "DNI de Personal Delivery no válido.")
            return
            
        if not self.detalle_actual:
            messagebox.showerror("Error", "El pedido debe contener al menos un producto.")
            return

        # 3. Creación del objeto Pedido
        nro_pedido = self.nro_pedido_var.get()
        
        nuevo_pedido = Pedido(
            nro_pedido=nro_pedido,
            fecha_pedido=self.fecha_pedido_var.get(),
            # fecha_entrega se omite, por lo que el estado será PENDIENTE.
            cliente_dni=cliente_dni,
            personal_delivery_dni=personal_delivery_dni,
            observaciones=self.obs_var.get(),
        )
        
        # Asignar detalles y recalcular totales (por si acaso)
        nuevo_pedido.detalles = self.detalle_actual
        nuevo_pedido.calcular_totales()
        
        # 4. Guardar datos y sincronizar
        self.pedidos.append(nuevo_pedido)
        data_manager.save_pedidos(self.pedidos)
        data_manager.save_productos(self.productos) # Guardar stock modificado
        
        # Sincronizar las listas maestras globales del controlador
        self.app.global_data['productos'] = self.productos
        self.app.global_data['pedidos'] = self.pedidos

        messagebox.showinfo("Registro Exitoso", f"Pedido {nro_pedido} registrado por un total de S/ {nuevo_pedido.total_a_pagar:.2f}. Estado: PENDIENTE.")
        self.limpiar_campos()

    def limpiar_campos(self):
        """Prepara la interfaz para el registro del siguiente pedido."""
        self.detalle_actual = []
        
        # Generar nuevo Nro. de Pedido
        self.nro_pedido_var.set(get_next_nro_pedido(self.pedidos))
        self.fecha_pedido_var.set(datetime.now().strftime("%Y-%m-%d"))
        
        # Limpiar campos de cabecera
        self.cliente_dni_entry.delete(0, tk.END)
        self.delivery_dni_entry.delete(0, tk.END)
        self.fecha_entrega_entry.delete(0, tk.END)
        self.cliente_nombre_var.set("---")
        self.obs_var.set("")
        
        # Limpiar detalles y totales de la UI
        self.load_detalles_treeview()
        self.calcular_totales_ui()
        
        # Asegurar que el Combobox de productos muestra el stock correcto para el siguiente pedido
        self.update_product_list()