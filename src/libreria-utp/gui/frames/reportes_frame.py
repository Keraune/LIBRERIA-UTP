import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from services import data_manager
from models.order import Pedido
from models.client import Cliente
from datetime import datetime

class ReportesFrame(tk.Frame):
    """Vista/Frame para generar consultas y reportes utilizando Pandas (Ciencia de Datos)."""
    def __init__(self, parent_container, app_controller, data):
        super().__init__(parent_container)
        self.app = app_controller
        # Las listas se inicializan, pero se obtendrán "frescas" del controlador en get_pedidos_dataframe()
        self.clientes = data.get('clientes', [])
        self.pedidos = data.get('pedidos', [])
        self.productos = data.get('productos', [])
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")

        # Pestaña 1: Búsqueda de Pedidos (por Cliente/Fecha)
        self.frame_busqueda = tk.Frame(self.notebook)
        self.notebook.add(self.frame_busqueda, text='Búsqueda por Cliente/Fecha')
        self.create_widgets_busqueda(self.frame_busqueda)

        # Pestaña 2: Reporte de Delivery / Pandas
        self.frame_reporte_delivery = tk.Frame(self.notebook)
        self.notebook.add(self.frame_reporte_delivery, text='Reporte de Delivery (Pandas)')
        self.create_widgets_reporte_delivery(self.frame_reporte_delivery)
        
        # Disparar la recarga y la búsqueda inicial al cambiar de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    # --- Pestaña 1: Búsqueda de Pedidos ---
    def create_widgets_busqueda(self, parent):
        search_frame = tk.LabelFrame(parent, text="Criterios de Búsqueda", padx=10, pady=10)
        search_frame.pack(padx=10, pady=10, fill="x")

        # Configuración de los campos de búsqueda (Nombre y Rango de Fechas)
        tk.Label(search_frame, text="Nombre/Apellido Cliente:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.name_search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.name_search_var, width=25).grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(search_frame, text="Rango de Fechas (AAAA-MM-DD):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        tk.Label(search_frame, text="Desde:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.date_from_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.date_from_var, width=12).grid(row=2, column=1, padx=5, pady=2)

        tk.Label(search_frame, text="Hasta:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.date_to_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.date_to_var, width=12).grid(row=3, column=1, padx=5, pady=2)
        
        ttk.Button(search_frame, text="Buscar Pedidos", command=self.ejecutar_busqueda_pedidos).grid(row=0, column=2, padx=10, pady=5, rowspan=4, sticky='ns')

        # Treeview para resultados de búsqueda
        tree_frame = tk.Frame(parent)
        tree_frame.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ("Nro. Pedido", "Fecha Pedido", "Cliente", "Total", "Estado", "Delivery DNI")
        self.tree_search = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree_search.heading(col, text=col, anchor=tk.W)
            self.tree_search.column(col, width=100)
        
        self.tree_search.bind('<<TreeviewSelect>>', self.item_selected_pedido)
        
        self.tree_search.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_search.yview)
        vsb.pack(side='right', fill='y')
        self.tree_search.configure(yscrollcommand=vsb.set)
        
        # Área de detalles del pedido
        detail_frame = tk.LabelFrame(parent, text="Detalles del Pedido Seleccionado", padx=10, pady=10)
        detail_frame.pack(padx=10, pady=10, fill="x")
        
        self.detail_text = tk.Text(detail_frame, height=5, width=80, state='disabled')
        self.detail_text.pack(fill="x", expand=True)


    def item_selected_pedido(self, event):
        """Muestra los detalles completos del pedido seleccionado, incluyendo el detalle de productos."""
        selected_items = self.tree_search.selection()
        if not selected_items: return

        item = self.tree_search.item(selected_items[0])
        nro_pedido = item['values'][0]

        # Buscar el objeto Pedido en la lista maestra para acceder a los detalles
        pedido_obj = next((p for p in self.pedidos if p.nro_pedido == nro_pedido), None)

        self.detail_text.config(state='normal')
        self.detail_text.delete('1.0', tk.END)
        
        if pedido_obj:
            cliente_nombre = next((c.get_full_name() for c in self.clientes if c.dni == pedido_obj.cliente_dni), "N/A")
            
            details_str = f"Nro. Pedido: {pedido_obj.nro_pedido}\n"
            details_str += f"Cliente: {cliente_nombre} (DNI: {pedido_obj.cliente_dni})\n"
            details_str += f"Fecha Pedido: {pedido_obj.fecha_pedido}\n"
            details_str += f"Estado: {pedido_obj.get_estado()}"
            if pedido_obj.fecha_entrega:
                details_str += f" (Entregado: {pedido_obj.fecha_entrega})"
            details_str += f"\nTotal: S/ {pedido_obj.total_a_pagar:.2f}\n"
            details_str += "-------------------------------\n"
            details_str += "Detalle de Productos:\n"
            
            for detalle in pedido_obj.detalles:
                producto_nombre = detalle.producto.nombre if detalle.producto else "Producto No Disponible"
                unit_price = detalle.producto.precio if detalle.producto else 0.0
                
                details_str += f"  - {producto_nombre} x {detalle.cantidad} (S/ {unit_price:.2f} c/u)\n"
            
            self.detail_text.insert(tk.END, details_str)
        else:
            self.detail_text.insert(tk.END, f"No se pudo encontrar el objeto Pedido {nro_pedido}.")

        self.detail_text.config(state='disabled')


    def get_pedidos_dataframe(self):
        """Convierte la lista de pedidos en un DataFrame de Pandas."""
        # Asegurar usar la lista de pedidos y clientes más fresca de la aplicación
        self.pedidos = self.app.global_data.get('pedidos', self.pedidos)
        self.clientes = self.app.global_data.get('clientes', self.clientes)
        
        # Retornar DataFrame vacío si no hay pedidos (previene KeyError)
        if not self.pedidos:
             return pd.DataFrame(columns=['nro_pedido', 'personal_delivery_dni',
                                          'cliente_nombre', 'fecha_pedido_dt',
                                          'fecha_entrega_dt', 'fecha_entrega',
                                          'fecha_pedido', 'total_a_pagar'])
        
        pedidos_dicts = []
        for p in self.pedidos:
            cliente = next((c for c in self.clientes if c.dni == p.cliente_dni), None)
            
            p_dict = p.to_dict()
            
            # Añadir y limpiar campos necesarios para Pandas
            p_dict['fecha_entrega'] = p.fecha_entrega
            p_dict['cliente_nombre'] = cliente.get_full_name() if cliente else "N/A"
            # Convertir a objetos datetime de Pandas
            p_dict['fecha_pedido_dt'] = pd.to_datetime(p.fecha_pedido, errors='coerce')
            p_dict['fecha_entrega_dt'] = pd.to_datetime(p.fecha_entrega, errors='coerce')
            
            pedidos_dicts.append(p_dict)

        return pd.DataFrame(pedidos_dicts)

    def ejecutar_busqueda_pedidos(self):
        """Filtra pedidos por Cliente/Fecha usando programación funcional de Pandas."""
        df = self.get_pedidos_dataframe()

        name_term = self.name_search_var.get().strip().lower()
        date_from = self.date_from_var.get().strip()
        date_to = self.date_to_var.get().strip()

        # Determinar si el usuario ingresó algún criterio de búsqueda.
        has_search_criteria = bool(name_term or date_from or date_to)

        # Limpiar Treeview y detalles
        for item in self.tree_search.get_children(): self.tree_search.delete(item)
        self.detail_text.config(state='normal'); self.detail_text.delete('1.0', tk.END); self.detail_text.config(state='disabled')

        # Caso de inicio del programa: Si no hay pedidos Y no hay criterios, retornar silenciosamente.
        if df.empty and not has_search_criteria:
            return
            
        # Filtrado de datos (Ciencia de Datos - Pandas)
        
        # 1. Filtrar por Nombre/Apellido (Pandas: str.contains)
        if name_term:
            df = df[df['cliente_nombre'].str.lower().str.contains(name_term, na=False)]
            
        # 2. Filtrar por Rango de Fechas (Pandas: operadores de comparación de fechas)
        try:
            if date_from:
                date_from_dt = pd.to_datetime(date_from, errors='coerce')
                df = df[df['fecha_pedido_dt'] >= date_from_dt]
            if date_to:
                # Incluir el final del día de la fecha 'Hasta'
                date_to_dt = pd.to_datetime(date_to, errors='coerce') + pd.Timedelta(days=1)
                df = df[df['fecha_pedido_dt'] < date_to_dt]
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha incorrecto. Use AAAA-MM-DD.")
            return

        # Manejo de resultados vacíos
        
        if df.empty:
            # Solo mostrar el mensaje adecuado según si se usaron criterios o si el sistema está vacío.
            if has_search_criteria:
                messagebox.showinfo("Búsqueda", "No se encontraron pedidos con los criterios ingresados.")
            else:
                 # Si llega aquí sin criterios, es que el sistema está completamente vacío (o se vació ahora).
                 messagebox.showinfo("Búsqueda", "No se encontraron pedidos en el sistema.")
            return
            
        # Cargar resultados en Treeview
        for index, row in df.iterrows():
            total = float(row['total_a_pagar']) if row['total_a_pagar'] else 0.0
            self.tree_search.insert('', tk.END, values=(
                row['nro_pedido'],
                row['fecha_pedido'],
                row['cliente_nombre'],
                f"S/ {total:.2f}",
                # Determinar estado: ENTREGADO si hay fecha_entrega, PENDIENTE si es nulo
                "ENTREGADO" if pd.notna(row['fecha_entrega']) else "PENDIENTE",
                row['personal_delivery_dni']
            ))

    # --- Pestaña 2: Reporte de Delivery (Pandas) ---
    def create_widgets_reporte_delivery(self, parent):
        
        control_frame = tk.Frame(parent)
        control_frame.pack(padx=10, pady=10, fill="x")
        ttk.Button(control_frame, text="Generar Reporte de Entregas por Personal", command=self.generar_reporte_delivery).pack(pady=5)
        
        self.report_label = tk.Label(parent, text="Reporte de Entregas por Delivery:", font=('Arial', 10, 'bold'))
        self.report_label.pack(padx=10, pady=5, anchor="w")

        # Treeview para el reporte
        tree_frame = tk.Frame(parent)
        tree_frame.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ("DNI Delivery", "Nombre Delivery", "Total Entregas")
        self.tree_report = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree_report.heading(col, text=col, anchor=tk.W)
            self.tree_report.column(col, width=150)
        
        self.tree_report.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_report.yview)
        vsb.pack(side='right', fill='y')
        self.tree_report.configure(yscrollcommand=vsb.set)

    def generar_reporte_delivery(self):
        """Genera el reporte de pedidos entregados por personal de delivery usando Pandas (Agrupación y Conteo)."""
        df = self.get_pedidos_dataframe()

        # 1. Filtrar solo pedidos entregados (donde la columna de fecha de entrega NO es NaT/nula)
        df_entregados = df[df['fecha_entrega_dt'].notna()]
        
        # Limpiar Treeview
        for item in self.tree_report.get_children(): self.tree_report.delete(item)
        
        if df_entregados.empty:
            messagebox.showinfo("Reporte", "No hay pedidos entregados para generar el reporte.")
            return

        # 2. Agrupar por DNI del Delivery y contar el número de pedidos (Ciencia de Datos: groupby + count)
        reporte = df_entregados.groupby('personal_delivery_dni')['nro_pedido'].count().reset_index()
        reporte.columns = ['DNI Delivery', 'Total Entregas']

        # 3. Mapear DNI a Nombre (Programación Funcional)
        dni_to_name = {c.dni: c.get_full_name() for c in self.clientes}
        # Agregar el nombre correspondiente al DNI del delivery
        reporte['Nombre Delivery'] = reporte['DNI Delivery'].apply(lambda dni: dni_to_name.get(dni, "N/A") if pd.notna(dni) else "SIN ASIGNAR")

        # 4. Cargar Treeview
        for index, row in reporte.iterrows():
            self.tree_report.insert('', tk.END, values=(
                row['DNI Delivery'],
                row['Nombre Delivery'],
                row['Total Entregas']
            ))
            
    def on_tab_change(self, event):
        """Recarga la información cuando se cambia de pestaña para asegurar que los datos estén frescos."""
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        
        # Sincronizar datos globales
        self.pedidos = self.app.global_data.get('pedidos', [])
        self.clientes = self.app.global_data.get('clientes', [])
        
        if selected_tab == 'Búsqueda por Cliente/Fecha':
            # Ejecutar la búsqueda con criterios vacíos para mostrar todos los pedidos
            self.ejecutar_busqueda_pedidos()
        elif selected_tab == 'Reporte de Delivery (Pandas)':
            # Generar el reporte automáticamente
            self.generar_reporte_delivery()