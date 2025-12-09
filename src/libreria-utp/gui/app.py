import tkinter as tk
from tkinter import messagebox
from services import data_manager
from gui.frames.mantenimiento_clientes_frame import MantenimientoClientesFrame
from gui.frames.mantenimiento_productos_frame import MantenimientoProductosFrame
from gui.frames.registro_pedido_frame import RegistroPedidoFrame
from gui.frames.registro_entrega_frame import RegistroEntregaFrame
from gui.frames.reportes_frame import ReportesFrame

class AplicacionLibreria(tk.Tk):
    """Clase principal de la aplicación GUI (Ventana Tkinter). Actúa como Controlador Central."""
    def __init__(self, clientes_data, productos_data, categorias_data, pedidos_data):
        super().__init__()
        self.title("Librería Virtual UTP - Sistema Supervisor")
        self.geometry("1200x800")
        
        self.clientes = clientes_data
        self.productos = productos_data
        self.categorias = categorias_data
        self.pedidos = pedidos_data
        
        self.global_data = {
            'clientes': self.clientes,
            'productos': self.productos,
            'categorias': self.categorias,
            'pedidos': self.pedidos,
        }
        
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        self.show_auth_window()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_menu_bar(self):
        """Barra de menú superior para la navegación principal."""
        menubar = tk.Menu(self)
        
        mantenimiento_menu = tk.Menu(menubar, tearoff=0)
        mantenimiento_menu.add_command(label="Clientes", command=lambda: self.show_frame("Clientes"))
        mantenimiento_menu.add_command(label="Productos y Categorías", command=lambda: self.show_frame("Productos"))
        menubar.add_cascade(label="Mantenimiento", menu=mantenimiento_menu)

        pedidos_menu = tk.Menu(menubar, tearoff=0)
        pedidos_menu.add_command(label="Registrar Nuevo Pedido", command=lambda: self.show_frame("RegistroPedido"))
        pedidos_menu.add_command(label="Registrar Entrega", command=lambda: self.show_frame("RegistroEntrega"))
        pedidos_menu.add_separator()
        pedidos_menu.add_command(label="Consultas/Reportes", command=lambda: self.show_frame("Reportes"))
        menubar.add_cascade(label="Pedidos", menu=pedidos_menu)

        menubar.add_command(label="Guardar y Salir", command=self.on_closing)

        self.config(menu=menubar)

    def show_auth_window(self):
        """Muestra la ventana de autenticación al inicio."""
        AuthWindow(self)

    def show_main_interface(self):
        """Carga los frames principales después de la autenticación."""
        self.create_menu_bar()
        container = self.container
        
        self.frames["Clientes"] = MantenimientoClientesFrame(container, self, self.clientes)
        self.frames["Productos"] = MantenimientoProductosFrame(container, self, self.productos, self.categorias)
        
        self.frames["RegistroPedido"] = RegistroPedidoFrame(container, self, self.global_data)
        self.frames["RegistroEntrega"] = RegistroEntregaFrame(container, self, self.global_data)
        self.frames["Reportes"] = ReportesFrame(container, self, self.global_data)
        
        for frame_name in self.frames:
            self.frames[frame_name].grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("Clientes")

    def on_closing(self):
        """Función ejecutada al cerrar la ventana, guarda los datos y cierra la aplicación."""
        if messagebox.askyesno("Salir", "¿Desea guardar los cambios y salir del sistema?"):
            data_manager.save_clientes(self.clientes)
            data_manager.save_productos(self.productos)
            data_manager.save_categorias(self.categorias)
            data_manager.save_pedidos(self.pedidos)
            self.destroy()

    def reload_data_from_disk(self):
        """Recarga los datos de Pedidos y Productos desde el disco y actualiza global_data."""
        self.productos = data_manager.load_productos()
        self.pedidos = data_manager.load_pedidos(self.productos)
        
        self.global_data['productos'] = self.productos
        self.global_data['pedidos'] = self.pedidos

    def show_frame(self, page_name):
        """Muestra un frame específico y asegura que los datos estén frescos."""
        frame = self.frames.get(page_name)
        if frame:
            
            if page_name in ["RegistroPedido", "RegistroEntrega", "Reportes", "Productos"]:
                self.reload_data_from_disk()

            if page_name == "Clientes":
                pass
            
            elif page_name == "Productos":
                if hasattr(frame, 'refresh_view'):
                    frame.refresh_view()
                else:
                    if hasattr(frame, 'load_productos_treeview'):
                        frame.load_productos_treeview()
                    if hasattr(frame, 'update_categoria_combobox'):
                        frame.update_categoria_combobox()
                
            elif page_name == "RegistroPedido":
                if hasattr(frame, 'update_product_list'):
                    frame.update_product_list()
                if hasattr(frame, 'limpiar_campos'):
                    frame.limpiar_campos()
                
            elif page_name == "RegistroEntrega":
                if hasattr(frame, 'reset_filter'):
                    frame.reset_filter()
            
            elif page_name == "Reportes":
                if hasattr(frame, 'refresh_data_and_ui'):
                    frame.refresh_data_and_ui()

            frame.tkraise()
        else:
            messagebox.showinfo("Error", f"La vista de '{page_name}' no se pudo cargar.")


class AuthWindow(tk.Toplevel):
    """Ventana emergente para la Autenticación del Supervisor."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Autenticación Requerida")
        self.geometry("300x150")
        self.resizable(False, False)
        
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.parent.on_closing)

        tk.Label(self, text="🔒 Usuario:").pack(pady=5)
        self.user_entry = tk.Entry(self)
        self.user_entry.pack(pady=2)
        
        tk.Label(self, text="Contraseña:").pack(pady=5)
        self.pass_entry = tk.Entry(self, show="*")
        self.pass_entry.pack(pady=2)

        tk.Button(self, text="Ingresar", command=self.authenticate).pack(pady=10)

        self.user_entry.focus_set()

    def authenticate(self):
        user = self.user_entry.get()
        password = self.pass_entry.get()
        
        USER_VALIDO = "admin"
        PASS_VALIDA = "1234"
        
        if user == USER_VALIDO and password == PASS_VALIDA:
            messagebox.showinfo("Éxito", "Autenticación exitosa.")
            self.parent.show_main_interface()
            self.destroy()
        else:
            messagebox.showerror("Error", "Usuario o Contraseña incorrectos.")
            self.user_entry.delete(0, tk.END)
            self.pass_entry.delete(0, tk.END)