import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

class FileSearchApp:
    def __init__(self, master):
        self.master = master
        master.title("Buscador de Archivos - BlueSearch")
        master.configure(bg="#2c3e50")
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Variables de búsqueda
        self.search_params = {
            "filename": tk.StringVar(),
            "extension": tk.StringVar(),
            "min_size": tk.StringVar(),
            "max_size": tk.StringVar(),
            "modified_after": tk.StringVar(),
            "content": tk.StringVar()
        }
        
        # Crear widgets
        self.create_widgets()
        
    def configure_styles(self):
        self.style.configure('TFrame', background='#3498db')
        self.style.configure('TLabel', background='#3498db', foreground='white', font=('Arial', 10))
        self.style.configure('TButton', background='#2980b9', foreground='white', font=('Arial', 10))
        self.style.map('TButton', background=[('active', '#1f618d')])
        self.style.configure('TEntry', fieldbackground='white', font=('Arial', 10))
        self.style.configure('TCombobox', fieldbackground='white', font=('Arial', 10))
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.master, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos de búsqueda
        ttk.Label(main_frame, text="Nombre del archivo:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.search_params["filename"], width=30).grid(row=0, column=1, padx=5)
        
        ttk.Label(main_frame, text="Extensión:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.search_params["extension"], width=30).grid(row=1, column=1, padx=5)
        
        ttk.Label(main_frame, text="Tamaño (MB):").grid(row=2, column=0, sticky=tk.W, pady=5)
        size_frame = ttk.Frame(main_frame)
        size_frame.grid(row=2, column=1, sticky=tk.W)
        ttk.Combobox(size_frame, values=['>', '<', '='], width=3).grid(row=0, column=0)
        ttk.Entry(size_frame, textvariable=self.search_params["min_size"], width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(main_frame, text="Modificado después de:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.search_params["modified_after"], width=30).grid(row=3, column=1, padx=5)
        
        ttk.Label(main_frame, text="Contenido:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.search_params["content"], width=30).grid(row=4, column=1, padx=5)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Seleccionar Directorio", command=self.select_directory).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Buscar", command=self.start_search).pack(side=tk.LEFT, padx=10)
        
        # Resultados
        self.results_list = tk.Listbox(main_frame, width=80, height=20, bg='white', fg='#2c3e50')
        self.results_list.grid(row=6, column=0, columnspan=2, pady=10)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.results_list.yview)
        scrollbar.grid(row=6, column=2, sticky=tk.NS)
        self.results_list.config(yscrollcommand=scrollbar.set)
        
        # Etiqueta de estado
        self.status_label = ttk.Label(main_frame, text="", foreground="white")
        self.status_label.grid(row=7, column=0, columnspan=2)
        
    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.search_directory = directory
            self.status_label.config(text=f"Directorio seleccionado: {directory}")
        
    def start_search(self):
        if not hasattr(self, 'search_directory'):
            messagebox.showerror("Error", "Selecciona un directorio primero")
            return
            
        self.results_list.delete(0, tk.END)
        self.status_label.config(text="Buscando...")
        
        try:
            for root, dirs, files in os.walk(self.search_directory):
                for file in files:
                    filepath = os.path.join(root, file)
                    if self.matches_all_criteria(filepath):
                        self.results_list.insert(tk.END, filepath)
            
            self.status_label.config(text=f"Búsqueda completada. {self.results_list.size()} resultados encontrados.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        
    def matches_all_criteria(self, filepath):
        try:
            # Verificar nombre
            filename = self.search_params["filename"].get().lower()
            if filename and filename not in os.path.basename(filepath).lower():
                return False
                
            # Verificar extensión
            ext = self.search_params["extension"].get().lower()
            if ext and not filepath.lower().endswith(f".{ext}"):
                return False
                
            # Verificar tamaño
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            if self.search_params["min_size"].get():
                target_size = float(self.search_params["min_size"].get())
                if not eval(f"{size_mb} {self.search_params['min_size'].get()[0]} {target_size}"):
                    return False
                    
            # Verificar fecha modificación
            mod_date = datetime.fromtimestamp(os.path.getmtime(filepath))
            if self.search_params["modified_after"].get():
                target_date = datetime.strptime(self.search_params["modified_after"].get(), "%d/%m/%Y")
                if mod_date < target_date:
                    return False
                    
            # Verificar contenido
            content = self.search_params["content"].get()
            if content:
                try:
                    with open(filepath, 'r', errors='ignore') as f:
                        if content.lower() not in f.read().lower():
                            return False
                except:
                    return False
                    
            return True
            
        except Exception as e:
            return False

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = FileSearchApp(root)
    root.mainloop()