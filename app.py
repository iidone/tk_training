import tkinter as tk
from tkinter import ttk, messagebox
from db import Database



class App(tk.Tk):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.title('ООО "Обувь"')
        self.geometry('700x300+400+200')
        self.resizable = (False, False)

        self.create_widgets()
        self.load_data()

    def create_widgets(self):

        btn_frame = tk.Frame()
        btn_frame.pack(side="bottom", padx=6, pady=6)

        tk.Button(btn_frame, text="Добавить", command=self.open_add_window).pack(padx=2, side=tk.LEFT)
        tk.Button(btn_frame, text="Изменить").pack(padx=2, side=tk.LEFT)
        tk.Button(btn_frame, text="Удалить", command=self.delete_product).pack(padx=2, side=tk.LEFT)
        tk.Button(btn_frame, text="Обновить", command=self.load_data).pack(padx=2, side=tk.LEFT)

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


    def delete_product(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showinfo("выберите товар")
        
        item = self.tree.item(selected[0])
        product_id = item['values'][0]
        if messagebox.askyesno("подтверждение", "удалить товар?"):
            self.db.execute_query("DELETE FROM products WHERE id = %s", (product_id,))
            self.load_data()


class AddWindow(tk.Toplevel):

    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.title("Add product")
        self.geometry('300x300+600+200')
        self.resizable(False, False)
    

        tk.Label(self, text="Name: ").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(self)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="Price: ").grid(row=1, column=0, padx=5, pady=5)
        self.price_entry = tk.Entry(self)
        self.price_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self, text="Quantity: ").grid(row=2, column=0, padx=5, pady=5)
        self.quantity_entry = tk.Entry(self)
        self.quantity_entry.grid(row=2, column=1, padx=5, pady=5)


        btn_frame = tk.Frame(self)
        btn_frame.grid(row=10, column=1, padx=10, pady=10)

        add_btn = tk.Button(btn_frame, text="Add", command=self.save)
        add_btn.grid()

    
    def save(self):
        name = self.name_entry.get().strip()
        price = self.price_entry.get().strip()
        quantity = self.quantity_entry.get().strip()

        if not name or not price or not quantity:
            messagebox.showerror("поля должны быть заполнены")
            return
        
        try:
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("не получилось сконвертить")
            return

        query = "INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s)"
        
        if self.db.execute_query(query, (name, price, quantity)):
            messagebox.showinfo("success")
            self.parent.load_data()
            self.destroy()
        else:
            messagebox.showerror("insert error")

    



if __name__ == "__main__":

    DBNAME = "tkinter"
    DBUSER = "postgres"
    DBPASSWORD = "postgres"
    DBHOST = "localhost"


    db = Database(DBNAME, DBUSER, DBPASSWORD, DBHOST)
    app = App(db)
    app.mainloop()
    db.db_close()