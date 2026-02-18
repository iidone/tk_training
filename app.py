import tkinter as tk
from tkinter import ttk, messagebox
from db import Database



class App(tk.Tk):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.title = 'app'
        self.geometry = '1200x800'
        self.resizable = (False, False)

        self.create_widgets()
        self.load_data()

    def create_widgets(self):

        btn_frame = tk.Frame()
        btn_frame.pack(side="bottom", padx=6, pady=6)

        tk.Button(btn_frame, text="Добавить", command=self.open_add_window).pack(padx=2, side=tk.LEFT)
        tk.Button(btn_frame, text="Изменить").pack(padx=2, side=tk.LEFT)
        tk.Button(btn_frame, text="Удалить").pack(padx=2, side=tk.LEFT)
        tk.Button(btn_frame, text="Обновить").pack(padx=2, side=tk.LEFT)

        columns = ('id', 'name', 'price', 'quantity')


        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.heading('id', text="ID")
        self.tree.heading('name', text="Название")
        self.tree.heading('price', text="Цена")
        self.tree.heading('quantity', text="Количество")


        self.tree.column('id', width='50')
        self.tree.column('name', width='200')
        self.tree.column('price', width='100')
        self.tree.column('quantity', width='100')
        

        self.tree.pack(fill=tk.X)

    def load_data(self):
        
        for row in self.tree.get_children():
            self.tree.delete(row)

        rows = self.db.fetch_all("SELECT id, name, price, quantity FROM products ORDER BY id")
        for row in rows:
            self.tree.insert('', tk.END, values=row)

    
    def open_add_window(self):
        AddWindow(self, self.db)

class AddWindow(tk.Toplevel):

    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.title("Add product")
        self.geometry('800x800')
        self.resizable(False, False)



if __name__ == "__main__":

    DBNAME = "tkinter"
    DBUSER = "postgres"
    DBPASSWORD = "postgres"
    DBHOST = "localhost"


    db = Database(DBNAME, DBUSER, DBPASSWORD, DBHOST)
    app = App(db)
    app.mainloop()
    db.db_close()