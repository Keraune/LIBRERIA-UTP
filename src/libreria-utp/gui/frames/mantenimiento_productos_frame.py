import tkinter as tk
from tkinter import ttk, messagebox
from models.product import Producto, Categoria
from services import data_manager
from services.logic_rules import is_low_stock 

class MantenimientoProductosFrame(tk.Frame):
    """Vista/Frame para gestionar las operaciones CRUD de Productos y Categorías."""
    def __init__(self, parent_container, app_controller, productos_data, categorias_data):
        super().__init__(parent_container)
        self.app = app_controller
        # Referencias a las listas globales para asegurar la sincronización de datos
        self.productos = productos_data
        self.categorias = categorias_data
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")

        # Pestaña 1: Productos
        self.frame_productos = tk.Frame(self.notebook)
        self.notebook.add(self.frame_productos, text='Gestión de Productos')
        self.create_widgets_productos(self.frame_productos)
        self.load_productos_treeview() 

        # Pestaña 2: Categorías
        self.frame_categorias = tk.Frame(self.notebook)
        self.notebook.add(self.frame_categorias, text='Gestión de Categorías')
        self.create_widgets_categorias(self.frame_categorias)
        self.load_categorias_treeview() 
        
# --- MÉTODO PARA REFRESCAR LA VISTA DESDE EL EXTERIOR ---
    def refresh_view(self):
        """Refresca la vista de productos y categorías. Usado por el controlador principal."""
        self.load_productos_treeview()
        self.load_categorias_treeview()
        self.update_categoria_combobox()

# --- PESTAÑA 1: GESTIÓN DE PRODUCTOS ---
    def create_widgets_productos(self, parent):
        input_frame = tk.LabelFrame(parent, text="Datos del Producto", padx=10, pady=10)
        input_frame.pack(padx=10, pady=10, fill="x")

        self.fields_prod = {}
        labels = ['Número de Serie', 'Nombre', 'Descripción', 'Precio', 'Stock', 'Color', 'Dimensiones']
        
        for i, label_text in enumerate(labels):
            tk.Label(input_frame, text=f"{label_text}:").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            entry = tk.Entry(input_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.fields_prod[label_text] = entry

        # Campo Categoría (Combobox)
        tk.Label(input_frame, text="Categoría:").grid(row=7, column=0, sticky="w", padx=5, pady=2)
        self.categoria_var = tk.StringVar()
        self.categoria_combobox = ttk.Combobox(input_frame, textvariable=self.categoria_var, state='readonly', width=38)
        self.categoria_combobox.grid(row=7, column=1, padx=5, pady=2)
        self.update_categoria_combobox()

        # Panel de Botones
        button_frame = tk.Frame(parent)
        button_frame.pack(padx=10, pady=5, fill="x")

        ttk.Button(button_frame, text="Registrar Producto", command=self.registrar_producto).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Modificar Producto", command=self.modificar_producto).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Eliminar Producto", command=self.eliminar_producto).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.limpiar_campos_productos).pack(side="left", padx=5)

        # Treeview de Productos
        tree_frame = tk.Frame(parent)
        tree_frame.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ("Nro. Serie", "Nombre", "Precio", "Stock", "Categoría", "Color")
        self.tree_prod = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree_prod.heading(col, text=col, anchor=tk.W)
            self.tree_prod.column(col, width=100)

        self.tree_prod.bind('<<TreeviewSelect>>', self.item_selected_producto)
        
        self.tree_prod.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_prod.yview)
        vsb.pack(side='right', fill='y')
        self.tree_prod.configure(yscrollcommand=vsb.set)

    def update_categoria_combobox(self):
        """Actualiza la lista de categorías disponibles para el Combobox de Producto."""
        categorias_frescas = self.app.global_data.get('categorias', self.categorias)
        nombres_categorias = [c.nombre for c in categorias_frescas]
        self.categoria_combobox['values'] = nombres_categorias
        if nombres_categorias and not self.categoria_var.get():
            self.categoria_combobox.set(nombres_categorias[0])

    def load_productos_treeview(self):
        """Carga los datos al Treeview. Sincroniza con los datos globales para reflejar cambios de stock."""
        
        # Sincronizar la lista de productos con la lista maestra global (App Controller)
        self.productos = self.app.global_data.get('productos', self.productos)
        productos_frescos = self.productos
        
        for item in self.tree_prod.get_children():
            self.tree_prod.delete(item)
            
        for prod in productos_frescos:
            # Aplicación de Regla Lógica: Marca el producto si el stock es bajo
            tag = 'low_stock' if is_low_stock(prod.stock) else ''
            
            self.tree_prod.insert('', tk.END, tags=(tag,), values=(
                prod.nro_serie,
                prod.nombre,
                f"S/ {prod.precio:.2f}",
                prod.stock,
                prod.categoria,
                prod.color
            ))
        
        # Estilo para stock bajo
        self.tree_prod.tag_configure('low_stock', background='salmon', foreground='black')

    def item_selected_producto(self, event):
        """Carga los datos del producto seleccionado en los campos de entrada."""
        selected_items = self.tree_prod.selection()
        if not selected_items: return
        
        # Sincronización previa
        self.productos = self.app.global_data.get('productos', self.productos)

        item = self.tree_prod.item(selected_items[0])
        nro_serie = item['values'][0]
        producto = next((p for p in self.productos if p.nro_serie == nro_serie), None)

        if producto:
            self.limpiar_campos_productos()
            self.fields_prod['Número de Serie'].insert(0, producto.nro_serie)
            # Bloquear la edición del Nro. Serie (clave primaria)
            self.fields_prod['Número de Serie'].config(state='readonly') 
            self.fields_prod['Nombre'].insert(0, producto.nombre)
            self.fields_prod['Descripción'].insert(0, producto.descripcion)
            self.fields_prod['Precio'].insert(0, str(producto.precio))
            self.fields_prod['Stock'].insert(0, str(producto.stock))
            self.fields_prod['Color'].insert(0, producto.color)
            self.fields_prod['Dimensiones'].insert(0, producto.dimensiones)
            self.categoria_combobox.set(producto.categoria)

    def limpiar_campos_productos(self):
        """Limpia todos los campos de entrada de la pestaña Producto y desbloquea el Nro. Serie."""
        for entry in self.fields_prod.values():
            entry.config(state='normal')
            entry.delete(0, tk.END)
        self.fields_prod['Número de Serie'].config(state='normal')
        if self.categoria_combobox['values']:
            self.categoria_combobox.set(self.categoria_combobox['values'][0])
        
    def registrar_producto(self):
        self.productos = self.app.global_data.get('productos', self.productos)
        
        data = {key: entry.get() for key, entry in self.fields_prod.items()}
        nro_serie = data['Número de Serie']
        
        if not all(data.values()):
            messagebox.showerror("Error", "Todos los campos deben estar llenos.")
            return
        
        if next((p for p in self.productos if p.nro_serie == nro_serie), None):
            messagebox.showerror("Error", "Ya existe un producto con ese Número de Serie.")
            return

        try:
            nuevo_prod = Producto(
                nro_serie=nro_serie,
                nombre=data['Nombre'],
                descripcion=data['Descripción'],
                precio=float(data['Precio']),
                stock=int(data['Stock']),
                categoria=self.categoria_var.get(),
                color=data['Color'],
                dimensiones=data['Dimensiones']
            )
            self.productos.append(nuevo_prod)
            
            # Persistencia y actualización global
            data_manager.save_productos(self.productos)
            self.app.global_data['productos'] = self.productos
            
            self.load_productos_treeview() 
            self.limpiar_campos_productos()
            
            messagebox.showinfo("Registro", "Producto registrado exitosamente.")
        except ValueError:
            messagebox.showerror("Error", "Precio y Stock deben ser números válidos.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar: {e}")

    def modificar_producto(self):
        self.productos = self.app.global_data.get('productos', self.productos)
        
        nro_serie = self.fields_prod['Número de Serie'].get()
        producto = next((p for p in self.productos if p.nro_serie == nro_serie), None)
        
        if not producto:
            messagebox.showerror("Error", "Seleccione un producto para modificar.")
            return
        
        data = {key: entry.get() for key, entry in self.fields_prod.items()}
        try:
            # Actualizar atributos del objeto Producto
            producto.nombre = data['Nombre']
            producto.descripcion = data['Descripción']
            producto.precio = float(data['Precio'])
            producto.stock = int(data['Stock'])
            producto.categoria = self.categoria_var.get()
            producto.color = data['Color']
            producto.dimensiones = data['Dimensiones']
            
            # Persistencia y actualización global
            data_manager.save_productos(self.productos)
            self.app.global_data['productos'] = self.productos
            
            self.load_productos_treeview()
            self.limpiar_campos_productos()
            
            messagebox.showinfo("Modificación", "Producto modificado exitosamente.")
        except ValueError:
            messagebox.showerror("Error", "Precio y Stock deben ser números válidos.")

    def eliminar_producto(self):
        self.productos = self.app.global_data.get('productos', self.productos)
        
        nro_serie = self.fields_prod['Número de Serie'].get()
        if not nro_serie:
            messagebox.showerror("Error", "Seleccione un producto para eliminar.")
            return
        
        if messagebox.askyesno("Confirmar Eliminación", f"¿Eliminar Producto {nro_serie}?"):
            # Eliminar el producto de la lista
            self.productos[:] = [p for p in self.productos if p.nro_serie != nro_serie]
            
            # Persistencia y actualización global
            data_manager.save_productos(self.productos)
            self.app.global_data['productos'] = self.productos
            
            self.load_productos_treeview()
            self.limpiar_campos_productos()
            
            messagebox.showinfo("Eliminación", "Producto eliminado exitosamente.")

# --- PESTAÑA 2: GESTIÓN DE CATEGORÍAS ---
    def create_widgets_categorias(self, parent):
        input_frame = tk.LabelFrame(parent, text="Datos de la Categoría", padx=10, pady=10)
        input_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(input_frame, text="Nombre:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.cat_nombre_entry = tk.Entry(input_frame, width=40)
        self.cat_nombre_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(input_frame, text="Descripción:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.cat_desc_entry = tk.Entry(input_frame, width=40)
        self.cat_desc_entry.grid(row=1, column=1, padx=5, pady=2)

        button_frame = tk.Frame(parent)
        button_frame.pack(padx=10, pady=5, fill="x")

        ttk.Button(button_frame, text="Registrar Categoría", command=self.registrar_categoria).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Modificar Categoría", command=self.modificar_categoria).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Eliminar Categoría", command=self.eliminar_categoria).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.limpiar_campos_categorias).pack(side="left", padx=5)

        tree_frame = tk.Frame(parent)
        tree_frame.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ("Nombre", "Descripción")
        self.tree_cat = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree_cat.heading(col, text=col, anchor=tk.W)
            self.tree_cat.column(col, width=200)

        self.tree_cat.bind('<<TreeviewSelect>>', self.item_selected_categoria)
        
        self.tree_cat.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_cat.yview)
        vsb.pack(side='right', fill='y')
        self.tree_cat.configure(yscrollcommand=vsb.set)

    def load_categorias_treeview(self):
        """Carga los datos al Treeview. Sincroniza con los datos globales."""
        self.categorias = self.app.global_data.get('categorias', self.categorias)

        for item in self.tree_cat.get_children():
            self.tree_cat.delete(item)
        for cat in self.categorias:
            self.tree_cat.insert('', tk.END, values=(cat.nombre, cat.descripcion))

    def item_selected_categoria(self, event):
        """Carga los datos de la categoría seleccionada y bloquea el Nombre (clave primaria)."""
        selected_items = self.tree_cat.selection()
        if not selected_items: return
        
        self.categorias = self.app.global_data.get('categorias', self.categorias)
        
        item = self.tree_cat.item(selected_items[0])
        nombre_cat = item['values'][0]

        self.limpiar_campos_categorias()
        self.cat_nombre_entry.insert(0, nombre_cat)
        self.cat_nombre_entry.config(state='readonly')
        
        categoria = next((c for c in self.categorias if c.nombre == nombre_cat), None)
        if categoria:
            self.cat_desc_entry.insert(0, categoria.descripcion)

    def limpiar_campos_categorias(self):
        """Limpia todos los campos de entrada de la pestaña Categoría y desbloquea el Nombre."""
        self.cat_nombre_entry.config(state='normal')
        self.cat_nombre_entry.delete(0, tk.END)
        self.cat_desc_entry.delete(0, tk.END)

    def registrar_categoria(self):
        self.categorias = self.app.global_data.get('categorias', self.categorias)
        
        nombre = self.cat_nombre_entry.get().strip()
        descripcion = self.cat_desc_entry.get().strip()

        if not nombre or not descripcion:
            messagebox.showerror("Error", "Nombre y Descripción son obligatorios.")
            return

        if next((c for c in self.categorias if c.nombre == nombre), None):
            messagebox.showerror("Error", f"Ya existe la categoría '{nombre}'.")
            return
        
        nueva_cat = Categoria(nombre, descripcion)
        self.categorias.append(nueva_cat)
        
        # Persistencia y actualización global
        data_manager.save_categorias(self.categorias)
        self.app.global_data['categorias'] = self.categorias
        
        self.load_categorias_treeview()
        self.update_categoria_combobox() # Actualiza el Combobox de Productos
        self.limpiar_campos_categorias()
        
        messagebox.showinfo("Registro", "Categoría registrada exitosamente.")
        
    def modificar_categoria(self):
        self.categorias = self.app.global_data.get('categorias', self.categorias)

        nombre = self.cat_nombre_entry.get().strip()
        categoria = next((c for c in self.categorias if c.nombre == nombre), None)

        if not categoria:
            messagebox.showerror("Error", "Seleccione una categoría para modificar.")
            return
            
        categoria.descripcion = self.cat_desc_entry.get().strip()
        
        # Persistencia y actualización global
        data_manager.save_categorias(self.categorias)
        self.app.global_data['categorias'] = self.categorias
        
        self.load_categorias_treeview()
        self.update_categoria_combobox()
        self.limpiar_campos_categorias()
        
        messagebox.showinfo("Modificación", "Categoría modificada exitosamente.")

    def eliminar_categoria(self):
        self.categorias = self.app.global_data.get('categorias', self.categorias)

        nombre = self.cat_nombre_entry.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Seleccione una categoría para eliminar.")
            return
        
        # Regla de negocio: Verificar si hay productos asociados antes de eliminar
        self.productos = self.app.global_data.get('productos', self.productos)
        productos_asociados = [p for p in self.productos if p.categoria == nombre]
        if productos_asociados:
            messagebox.showerror("Error", f"No se puede eliminar la categoría. Hay {len(productos_asociados)} productos asociados.")
            return

        if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar la categoría '{nombre}'?"):
            # Eliminar la categoría de la lista
            self.categorias[:] = [c for c in self.categorias if c.nombre != nombre]
            
            # Persistencia y actualización global
            data_manager.save_categorias(self.categorias)
            self.app.global_data['categorias'] = self.categorias
            
            self.load_categorias_treeview()
            self.update_categoria_combobox()
            self.limpiar_campos_categorias()
            
            messagebox.showinfo("Eliminación", "Categoría eliminada exitosamente.")