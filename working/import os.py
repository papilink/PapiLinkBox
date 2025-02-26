import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pwd
import grp

class SimpleFileSearch:
    def __init__(self, master):
        self.master = master
        master.title("Buscador Avanzado")
        master.geometry("1000x600")
        master.configure(bg="#2c3e50")
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Variables
        self.filename = tk.StringVar()
        
        # Crear interfaz
        self.create_widgets()
        
    def configure_styles(self):
        self.style.configure('TFrame', background='#3498db')
        self.style.configure('TLabel', background='#3498db', foreground='white', font=('Arial', 12))
        self.style.configure('TButton', background='#2980b9', foreground='white', font=('Arial', 12))
        self.style.map('TButton', background=[('active', '#1f618d')])
        self.style.configure('TEntry', fieldbackground='white', font=('Arial', 12))
        self.style.configure('Treeview', background='white', fieldbackground='white', foreground='black')
        self.style.configure('Treeview.Heading', background='#2980b9', foreground='white', font=('Arial', 10, 'bold'))
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campo de búsqueda
        ttk.Label(main_frame, text="Nombre del archivo a buscar:").pack(pady=10)
        search_entry = ttk.Entry(main_frame, textvariable=self.filename, width=50)
        search_entry.pack(pady=5)
        
        ttk.Button(main_frame, text="Buscar en todo el disco", command=self.start_search).pack(pady=10)
        
        # Resultados
        self.tree = ttk.Treeview(main_frame, columns=('Detalle', 'Valor'), show='headings')
        self.tree.heading('Detalle', text='Detalle')
        self.tree.heading('Valor', text='Valor')
        self.tree.column('Detalle', width=200)
        self.tree.column('Valor', width=750)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def start_search(self):
        filename = self.filename.get().strip()
        if not filename:
            messagebox.showwarning("Advertencia", "Ingresa un nombre de archivo")
            return
            
        self.tree.delete(*self.tree.get_children())
        
        try:
            for root, dirs, files in os.walk('/'):
                for file in files:
                    if file == filename:
                        filepath = os.path.join(root, file)
                        self.show_file_details(filepath)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def show_file_details(self, filepath):
        try:
            stat = os.stat(filepath)
            file_info = {
                'Ruta completa': filepath,
                'Tamaño': self.format_size(stat.st_size),
                'Última modificación': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'Último acceso': datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
                'Permisos': self.format_permissions(stat.st_mode),
                'Propietario': pwd.getpwuid(stat.st_uid).pw_name,
                'Grupo': grp.getgrgid(stat.st_gid).gr_name,
                'Número de enlaces': stat.st_nlink,
                'Dispositivo': stat.st_dev,
                'Nodo inode': stat.st_ino
            }
            
            for key, value in file_info.items():
                self.tree.insert('', tk.END, values=(key, value))
                
            # Separador entre archivos
            self.tree.insert('', tk.END, values=('-'*50, '-'*100))
            
        except Exception as e:
            self.tree.insert('', tk.END, values=("Error", f"No se pudieron obtener detalles: {str(e)}"))
            
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    def format_permissions(self, mode):
        perm = ''
        permissions = [
            ('r', os.R_OK),
            ('w', os.W_OK),
            ('x', os.X_OK)
        ]
        
        for i in range(3):
            for p in permissions:
                if mode & (0x100 >> (i*3 + (2 - permissions.index(p)))):
                    perm += p[0]
                else:
                    perm += '-'
            perm += ' '
        return perm

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleFileSearch(root)
    root.mainloop()