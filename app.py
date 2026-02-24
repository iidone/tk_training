import tkinter as tk
from tkinter import ttk, messagebox
from db import Database
from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT, 
    COLOR_TEXT, FONT_MAIN, FONT_HEADER, FONT_TITLE, FONT_BUTTON
)
from PIL import Image, ImageTk
import os


class LoginWindow(tk.Tk):
    
    def __init__(self, dbname, user, password, host):
        super().__init__()
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        
        self.title("ООО «Обувь» - Вход")
        self.geometry('400x450+550+200')
        self.resizable(False, False)
        
        self.configure(bg=COLOR_MAIN_BG)
        
        self.create_widgets()
        self.mainloop()
    
    
    def create_widgets(self):
        title = tk.Label(
            self, 
            text="ООО «Обувь»", 
            font=FONT_TITLE, 
            bg=COLOR_MAIN_BG, 
            fg=COLOR_TEXT
        )
        title.pack(pady=(30, 10))
        
        subtitle = tk.Label(
            self, 
            text="Авторизация", 
            font=FONT_HEADER, 
            bg=COLOR_MAIN_BG, 
            fg=COLOR_TEXT
        )
        subtitle.pack(pady=(0, 30))
        
        form_frame = tk.Frame(self, bg=COLOR_MAIN_BG)
        form_frame.pack(pady=10)
        
        tk.Label(
            form_frame, 
            text="Логин:", 
            font=FONT_MAIN, 
            bg=COLOR_MAIN_BG, 
            fg=COLOR_TEXT
        ).grid(row=0, column=0, padx=10, pady=10, sticky='e')
        
        self.login_entry = tk.Entry(form_frame, font=FONT_MAIN, width=20)
        self.login_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(
            form_frame, 
            text="Пароль:", 
            font=FONT_MAIN, 
            bg=COLOR_MAIN_BG, 
            fg=COLOR_TEXT
        ).grid(row=1, column=0, padx=10, pady=10, sticky='e')
        
        self.password_entry = tk.Entry(form_frame, font=FONT_MAIN, width=20, show='*')
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        btn_frame = tk.Frame(self, bg=COLOR_MAIN_BG)
        btn_frame.pack(pady=20)
        
        login_btn = tk.Button(
            btn_frame, 
            text="Войти", 
            font=FONT_BUTTON,
            bg=COLOR_ACCENT,
            fg=COLOR_TEXT,
            width=12,
            command=self.login
        )
        login_btn.pack(pady=5)
        
        guest_btn = tk.Button(
            btn_frame, 
            text="Гость", 
            font=FONT_BUTTON,
            bg=COLOR_SECONDARY_BG,
            fg=COLOR_TEXT,
            width=12,
            command=self.login_as_guest
        )
        guest_btn.pack(pady=5)
    
    
    def login(self):
        username = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль!")
            return
        
        db = Database(self.dbname, self.user, self.password, self.host)
        
        db.init_roles()
        
        user_data = db.check_user(username, password)
        
        if user_data:
            role = db.get_user_role(user_data['role_id'])
            self.destroy()
            app = App(self.dbname, self.user, self.password, self.host, role, username)
            app.mainloop()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")
    
    
    def login_as_guest(self):
        self.destroy()
        app = App(self.dbname, self.user, self.password, self.host, "Гость", "Гость")
        app.mainloop()


class App(tk.Tk):
    
    def __init__(self, dbname, user, password, host, role, username):
        super().__init__()
        self.db = Database(dbname, user, password, host)
        self.role = role
        self.username = username
        
        self.title(f"ООО «Обувь» - {role}")
        self.geometry('1200x700+200+50')
        
        self.configure(bg=COLOR_MAIN_BG)
        
        self.search_var = tk.StringVar()
        self.sort_var = tk.StringVar()
        
        self.current_photo = None
        self.photo_label = None
        
        self.product_cards = []
        self.selected_product_id = None
        
        self.create_widgets()
        self.apply_role_permissions()
        self.load_data()
        
        self.db.init_roles()
    
    
    def create_widgets(self):
        top_frame = tk.Frame(self, bg=COLOR_SECONDARY_BG, height=60)
        top_frame.pack(side=tk.TOP, fill=tk.X)
        top_frame.pack_propagate(False)
        
        title_label = tk.Label(
            top_frame, 
            text="ООО «Обувь»", 
            font=FONT_TITLE, 
            bg=COLOR_SECONDARY_BG, 
            fg=COLOR_TEXT
        )
        title_label.pack(side=tk.LEFT, padx=20)
        
        user_label = tk.Label(
            top_frame,
            text=f"Пользователь: {self.username} | Роль: {self.role}",
            font=FONT_MAIN,
            bg=COLOR_SECONDARY_BG,
            fg=COLOR_TEXT
        )
        user_label.pack(side=tk.RIGHT, padx=20)
        
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        products_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Товары", menu=products_menu)
        products_menu.add_command(label="Товары", command=self.show_products)
        products_menu.add_command(label="Добавить товар", command=self.open_add_window)
        products_menu.add_command(label="Редактировать товар", command=self.open_edit_window)
        products_menu.add_command(label="Удалить товар", command=self.delete_product)
        
        if self.role in ["Менеджер", "Администратор"]:
            orders_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Заказы", menu=orders_menu)
            orders_menu.add_command(label="Просмотр заказов", command=self.show_orders)
            if self.role == "Администратор":
                orders_menu.add_command(label="Добавить заказ", command=self.add_order)
                orders_menu.add_command(label="Редактировать заказ", command=self.edit_order)
                orders_menu.add_command(label="Удалить заказ", command=self.delete_order)
        
        menubar.add_command(label="Выход", command=self.quit)
        
        main_container = tk.Frame(self, bg=COLOR_MAIN_BG)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        products_area = tk.Frame(main_container, bg=COLOR_MAIN_BG)
        products_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        toolbar = tk.Frame(products_area, bg=COLOR_MAIN_BG)
        toolbar.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        if self.role in ["Менеджер", "Администратор"]:
            tk.Label(
                toolbar, 
                text="Поиск:", 
                font=FONT_MAIN, 
                bg=COLOR_MAIN_BG
            ).pack(side=tk.LEFT, padx=5)
            
            self.search_entry = tk.Entry(toolbar, textvariable=self.search_var, width=20, font=FONT_MAIN)
            self.search_entry.pack(side=tk.LEFT, padx=5)
            
            search_btn = tk.Button(
                toolbar, 
                text="Найти", 
                command=self.search_products,
                bg=COLOR_ACCENT,
                font=FONT_BUTTON
            )
            search_btn.pack(side=tk.LEFT, padx=5)

            tk.Label(
                toolbar, 
                text="Сортировка:", 
                font=FONT_MAIN, 
                bg=COLOR_MAIN_BG
            ).pack(side=tk.LEFT, padx=5)
            
            sort_combo = ttk.Combobox(
                toolbar, 
                textvariable=self.sort_var,
                values=["По умолчанию", "По названию (А-Я)", "По названию (Я-А)", 
                        "По цене (возр.)", "По цене (убыв.)", 
                        "По количеству (возр.)", "По количеству (убыв.)"],
                width=20,
                state="readonly"
            )
            sort_combo.pack(side=tk.LEFT, padx=5)
            sort_combo.bind("<<ComboboxSelected>>", lambda e: self.sort_products())

            reset_btn = tk.Button(
                toolbar,
                text="Сброс",
                command=self.load_data,
                bg=COLOR_SECONDARY_BG,
                font=FONT_BUTTON
            )
            reset_btn.pack(side=tk.LEFT, padx=5)
        
        btn_frame = tk.Frame(products_area, bg=COLOR_MAIN_BG)
        btn_frame.pack(side=tk.BOTTOM, pady=10)
        
        self.add_btn = tk.Button(
            btn_frame, 
            text="Добавить", 
            command=self.open_add_window,
            bg=COLOR_ACCENT,
            fg=COLOR_TEXT,
            font=FONT_BUTTON,
            width=12
        )
        self.add_btn.pack(padx=2, side=tk.LEFT)
        
        self.edit_btn = tk.Button(
            btn_frame, 
            text="Изменить", 
            command=self.open_edit_window,
            bg=COLOR_ACCENT,
            fg=COLOR_TEXT,
            font=FONT_BUTTON,
            width=12
        )
        self.edit_btn.pack(padx=2, side=tk.LEFT)
        
        self.delete_btn = tk.Button(
            btn_frame, 
            text="Удалить", 
            command=self.delete_product,
            bg=COLOR_ACCENT,
            fg=COLOR_TEXT,
            font=FONT_BUTTON,
            width=12
        )
        self.delete_btn.pack(padx=2, side=tk.LEFT)
        
        self.refresh_btn = tk.Button(
            btn_frame, 
            text="Обновить", 
            command=self.load_data,
            bg=COLOR_ACCENT,
            fg=COLOR_TEXT,
            font=FONT_BUTTON,
            width=12
        )
        self.refresh_btn.pack(padx=2, side=tk.LEFT)
        
        self.create_cards_area(products_area)
        self.create_photo_frame(main_container)
    
    
    def create_cards_area(self, parent):
        cards_container = tk.Frame(parent, bg=COLOR_MAIN_BG)
        cards_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        
        self.canvas = tk.Canvas(cards_container, bg=COLOR_MAIN_BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(cards_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLOR_MAIN_BG)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.cards_per_row = 3
        self.card_width = 260
        self.card_height = 320
    
    
    def create_product_card(self, parent, product_data, row, col):
        product_id, product_name, price, quantity, discount = product_data
        
        card_frame = tk.Frame(
            parent, 
            bg=COLOR_SECONDARY_BG, 
            width=self.card_width, 
            height=self.card_height,
            relief=tk.RAISED,
            borderwidth=2
        )
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card_frame.pack_propagate(False)
        
        card_frame.grid_rowconfigure(0, weight=1)
        
        image_label = tk.Label(card_frame, bg=COLOR_MAIN_BG, width=240, height=180)
        image_label.pack(padx=5, pady=5)
        image_label.pack_propagate(False)
        
        product_info = self.db.get_product_by_id(product_id)
        if product_info and product_info.get('photo_url'):
            self.load_card_image(image_label, product_info.get('photo_url'))
        else:
            self.load_card_image(image_label, 'images/picture.png')
        
        info_frame = tk.Frame(card_frame, bg=COLOR_SECONDARY_BG)
        info_frame.pack(fill=tk.X, padx=8, pady=5)
        
        name_label = tk.Label(
            info_frame,
            text=product_name if product_name else "Без названия",
            font=FONT_MAIN,
            bg=COLOR_SECONDARY_BG,
            fg=COLOR_TEXT,
            wraplength=self.card_width - 20,
            justify=tk.CENTER
        )
        name_label.pack()
        
        price_text = f"{price:.0f} руб."
        if discount and discount > 0:
            price_text = f"{price * (1 - discount/100):.0f} руб. (-{discount:.0f}%)"
        
        price_label = tk.Label(
            info_frame,
            text=price_text,
            font=FONT_HEADER,
            bg=COLOR_SECONDARY_BG,
            fg="#000000"
        )
        price_label.pack()
        
        quantity_text = f"В наличии: {quantity} шт."
        if quantity == 0:
            quantity_text = "Нет в наличии"
        
        quantity_label = tk.Label(
            info_frame,
            text=quantity_text,
            font=FONT_MAIN,
            bg=COLOR_SECONDARY_BG,
            fg=COLOR_TEXT
        )
        quantity_label.pack()
        
        card_frame.bind("<Button-1>", lambda e, pid=product_id: self.on_card_click(pid))
        image_label.bind("<Button-1>", lambda e, pid=product_id: self.on_card_click(pid))
        info_frame.bind("<Button-1>", lambda e, pid=product_id: self.on_card_click(pid))
        name_label.bind("<Button-1>", lambda e, pid=product_id: self.on_card_click(pid))
        price_label.bind("<Button-1>", lambda e, pid=product_id: self.on_card_click(pid))
        quantity_label.bind("<Button-1>", lambda e, pid=product_id: self.on_card_click(pid))
        
        for widget in card_frame.winfo_children():
            widget.bind("<Button-1>", lambda e, pid=product_id: self.on_card_click(pid))
        
        return card_frame
    
    
    def load_card_image(self, label, photo_url):
        if not photo_url or photo_url == 'NULL' or photo_url is None:
            photo_url = 'images/picture.png'
        
        try:
            possible_paths = [
                photo_url,
                os.path.join('images', os.path.basename(photo_url)),
                os.path.join(os.path.dirname(__file__), photo_url),
                os.path.join(os.path.dirname(__file__), 'images', os.path.basename(photo_url))
            ]
            
            image_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    image_path = path
                    break
            
            if not image_path:
                return
            
            image = Image.open(image_path)
            image = image.resize((230, 170), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            label.config(image=photo)
            label.image = photo
            
        except Exception as e:
            print(f"Error loading card image: {str(e)}")
    
    
    def on_card_click(self, product_id):
        self.selected_product_id = product_id
        
        for card in self.product_cards:
            card.config(bg=COLOR_SECONDARY_BG, relief=tk.RAISED, borderwidth=2)
        
        product_info = self.db.get_product_by_id(product_id)
        
        if product_info:
            self.info_labels['Артикул:'].config(text=product_info.get('article', '-'))
            self.info_labels['Цена:'].config(text=f"{product_info.get('price', 0)} руб.")
            self.info_labels['Скидка:'].config(text=f"{product_info.get('discount', 0)}%")
            self.info_labels['На складе:'].config(text=str(product_info.get('quantity', 0)))
            
            self.load_image(product_info.get('photo_url'))
    
    
    def create_photo_frame(self, parent):
        photo_frame = tk.Frame(parent, bg=COLOR_SECONDARY_BG, width=300)
        photo_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        photo_frame.pack_propagate(False)
        
        tk.Label(
            photo_frame,
            text="Изображение товара",
            font=FONT_HEADER,
            bg=COLOR_SECONDARY_BG,
            fg=COLOR_TEXT
        ).pack(pady=10)
        
        self.image_container = tk.Frame(photo_frame, bg=COLOR_MAIN_BG, width=280, height=280)
        self.image_container.pack(pady=10)
        self.image_container.pack_propagate(False)
        
        self.photo_label = tk.Label(self.image_container, bg=COLOR_MAIN_BG)
        self.photo_label.pack(fill=tk.BOTH, expand=True)
        
        self.default_text = tk.Label(
            self.image_container,
            text="Нет изображения",
            font=FONT_MAIN,
            bg=COLOR_MAIN_BG,
            fg=COLOR_TEXT
        )
        self.default_text.pack(expand=True)
        
        self.info_frame = tk.Frame(photo_frame, bg=COLOR_SECONDARY_BG)
        self.info_frame.pack(fill=tk.X, pady=10)
        
        self.info_labels = {}
        info_fields = ['Артикул:', 'Цена:', 'Скидка:', 'На складе:']
        
        for field in info_fields:
            frame = tk.Frame(self.info_frame, bg=COLOR_SECONDARY_BG)
            frame.pack(fill=tk.X, pady=2)
            
            tk.Label(
                frame,
                text=field,
                font=FONT_MAIN,
                bg=COLOR_SECONDARY_BG,
                fg=COLOR_TEXT,
                width=10,
                anchor='w'
            ).pack(side=tk.LEFT)
            
            self.info_labels[field] = tk.Label(
                frame,
                text="-",
                font=FONT_MAIN,
                bg=COLOR_SECONDARY_BG,
                fg=COLOR_TEXT,
                anchor='w'
            )
            self.info_labels[field].pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            photo_frame,
            text="Увеличить",
            command=self.show_large_image,
            bg=COLOR_ACCENT,
            fg=COLOR_TEXT,
            font=FONT_BUTTON,
            width=15
        ).pack(pady=10)
    
    
    def load_image(self, photo_url):
        self.default_text.pack_forget()

        if not photo_url or photo_url == 'NULL' or photo_url is None:
            self.load_default_image()
            return

        try:
            possible_paths = [
                photo_url,
                os.path.join('images', os.path.basename(photo_url)),
                os.path.join(os.path.dirname(__file__), photo_url),
                os.path.join(os.path.dirname(__file__), 'images', os.path.basename(photo_url))
            ]

            image_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    image_path = path
                    break

            if not image_path:
                print(f"Image not found: {photo_url}")
                self.load_default_image()
                return

            image = Image.open(image_path)
            image = image.resize((260, 260), Image.Resampling.LANCZOS)

            self.current_photo = ImageTk.PhotoImage(image)
            self.photo_label.config(image=self.current_photo)

        except Exception as e:
            print(f"Error loading image {photo_url}: {str(e)}")
            self.load_default_image()

    def load_default_image(self):
        try:
            image = Image.open('images/picture.png')
            image = image.resize((260, 260), Image.Resampling.LANCZOS)

            self.current_photo = ImageTk.PhotoImage(image)
            self.photo_label.config(image=self.current_photo)
        except Exception as e:
            print(f"Error loading default image: {str(e)}")
            self.show_no_image()
    
    
    def show_no_image(self):
        self.photo_label.config(image='')
        self.default_text.pack(expand=True)
    
    
    def show_large_image(self):
        if not hasattr(self, 'current_photo') or self.current_photo is None:
            messagebox.showinfo("Информация", "Нет изображения для отображения")
            return
        
        if not self.selected_product_id:
            messagebox.showinfo("Информация", "Выберите товар для просмотра")
            return
        
        product_info = self.db.get_product_by_id(self.selected_product_id)
        if not product_info:
            return
        
        LargeImageWindow(self, product_info)
    
    
    def apply_role_permissions(self):
        if self.role == "Гость" or self.role == "Клиент":
            self.add_btn.config(state=tk.DISABLED)
            self.edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)
            
            self.config(menu=tk.Menu(self))
            menubar = tk.Menu(self)
            self.config(menu=menubar)
            menubar.add_command(label="Товары", command=self.show_products)
            menubar.add_command(label="Выход", command=self.quit)
        
        elif self.role == "Менеджер":
            self.add_btn.config(state=tk.DISABLED)
            self.edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)
    
    
    def load_data(self):
        for card in self.product_cards:
            card.destroy()
        self.product_cards.clear()
        
        rows = self.db.get_all_products()
        
        for i, row in enumerate(rows):
            product_id, product_name, price, quantity, discount = row
            row_idx = i // self.cards_per_row
            col_idx = i % self.cards_per_row
            
            card = self.create_product_card(self.scrollable_frame, row, row_idx, col_idx)
            self.product_cards.append(card)
        
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    
    def search_products(self):
        search_text = self.search_var.get().strip()
        if not search_text:
            messagebox.showinfo("Поиск", "Введите текст для поиска!")
            return
        
        sort_by = None
        sort_order = 'ASC'
        
        sort_value = self.sort_var.get()
        if sort_value == "По названию (А-Я)":
            sort_by = 'name'
        elif sort_value == "По названию (Я-А)":
            sort_by = 'name'
            sort_order = 'DESC'
        elif sort_value == "По цене (возр.)":
            sort_by = 'price'
        elif sort_value == "По цене (убыв.)":
            sort_by = 'price'
            sort_order = 'DESC'
        elif sort_value == "По количеству (возр.)":
            sort_by = 'quantity'
        elif sort_value == "По количеству (убыв.)":
            sort_by = 'quantity'
            sort_order = 'DESC'
        
        rows = self.db.search_products(search_text, sort_by=sort_by, sort_order=sort_order)
        
        for card in self.product_cards:
            card.destroy()
        self.product_cards.clear()
        
        for i, row in enumerate(rows):
            product_id, product_name, price, quantity, discount = row
            row_idx = i // self.cards_per_row
            col_idx = i % self.cards_per_row
            
            card = self.create_product_card(self.scrollable_frame, row, row_idx, col_idx)
            self.product_cards.append(card)
        
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    
    def sort_products(self):
        search_text = self.search_var.get().strip()
        
        sort_by = None
        sort_order = 'ASC'
        
        sort_value = self.sort_var.get()
        if sort_value == "По названию (А-Я)":
            sort_by = 'name'
        elif sort_value == "По названию (Я-А)":
            sort_by = 'name'
            sort_order = 'DESC'
        elif sort_value == "По цене (возр.)":
            sort_by = 'price'
        elif sort_value == "По цене (убыв.)":
            sort_by = 'price'
            sort_order = 'DESC'
        elif sort_value == "По количеству (возр.)":
            sort_by = 'quantity'
        elif sort_value == "По количеству (убыв.)":
            sort_by = 'quantity'
            sort_order = 'DESC'
        
        if search_text:
            rows = self.db.search_products(search_text, sort_by=sort_by, sort_order=sort_order)
        else:
            rows = self.db.get_all_products()
            if sort_by:
                rows = self.db.search_products("", sort_by=sort_by, sort_order=sort_order)
        
        for card in self.product_cards:
            card.destroy()
        self.product_cards.clear()
        
        for i, row in enumerate(rows):
            product_id, product_name, price, quantity, discount = row
            row_idx = i // self.cards_per_row
            col_idx = i % self.cards_per_row
            
            card = self.create_product_card(self.scrollable_frame, row, row_idx, col_idx)
            self.product_cards.append(card)
        
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    
    def show_products(self):
        self.load_data()
    
    
    def show_orders(self):
        OrdersWindow(self, self.db, self.role)
    
    
    def open_add_window(self):
        if self.role not in ["Администратор"]:
            messagebox.showinfo("Доступ", "У вас нет прав для добавления товаров!")
            return
        AddProductWindow(self, self.db)
    
    
    def open_edit_window(self):
        if self.role not in ["Администратор"]:
            messagebox.showinfo("Доступ", "У вас нет прав для редактирования товаров!")
            return
        
        if not self.selected_product_id:
            messagebox.showinfo("Информация", "Выберите товар для редактирования!")
            return
        
        EditProductWindow(self, self.db, self.selected_product_id)
    
    
    def delete_product(self):
        if self.role not in ["Администратор"]:
            messagebox.showinfo("Доступ", "У вас нет прав для удаления товаров!")
            return
        
        if not self.selected_product_id:
            messagebox.showinfo("Информация", "Выберите товар для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот товар?"):
            if self.db.delete_product(self.selected_product_id):
                messagebox.showinfo("Успех", "Товар успешно удален!")
                self.load_data()
                self.show_no_image()
                for label in self.info_labels.values():
                    label.config(text="-")
                self.selected_product_id = None
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить товар!")
    
    
    def add_order(self):
        messagebox.showinfo("Информация", "Функция добавления заказа в разработке")
    
    
    def edit_order(self):
        messagebox.showinfo("Информация", "Функция редактирования заказа в разработке")
    
    
    def delete_order(self):
        messagebox.showinfo("Информация", "Функция удаления заказа в разработке")


class LargeImageWindow(tk.Toplevel):
    
    def __init__(self, parent, product_info):
        super().__init__(parent)
        self.parent = parent
        self.product_info = product_info
        
        self.title(f"Изображение: {product_info.get('product_name', 'Товар')}")
        self.geometry('600x750+400-50')
        self.configure(bg=COLOR_MAIN_BG)
        
        self.create_widgets()
        self.grab_set()
    
    
    def create_widgets(self):
        tk.Label(
            self,
            text=self.product_info.get('product_name', 'Товар'),
            font=FONT_HEADER,
            bg=COLOR_MAIN_BG,
            fg=COLOR_TEXT
        ).pack(pady=10)
        
        image_frame = tk.Frame(self, bg=COLOR_SECONDARY_BG, width=500, height=500)
        image_frame.pack(pady=10)
        image_frame.pack_propagate(False)
        
        self.photo_label = tk.Label(image_frame, bg=COLOR_SECONDARY_BG)
        self.photo_label.pack(fill=tk.BOTH, expand=True)
        
        self.load_large_image()
        
        info_text = f"""
            Артикул: {self.product_info.get('article', '-')}
            Цена: {self.product_info.get('price', 0)} руб.
            Скидка: {self.product_info.get('discount', 0)}%
            На складе: {self.product_info.get('quantity', 0)}
        """
        
        tk.Label(
            self,
            text=info_text,
            font=FONT_MAIN,
            bg=COLOR_MAIN_BG,
            fg=COLOR_TEXT,
            justify=tk.LEFT
        ).pack(pady=10)
        
        tk.Button(
            self,
            text="Закрыть",
            command=self.destroy,
            bg=COLOR_ACCENT,
            fg=COLOR_TEXT,
            font=FONT_BUTTON,
            width=15
        ).pack(pady=10)
    
    
    def load_large_image(self):
        photo_url = self.product_info.get('photo_url')
        
        if not photo_url or photo_url == 'NULL' or photo_url is None:
            self.show_no_image()
            return
        
        try:
            possible_paths = [
                photo_url,
                os.path.join('images', os.path.basename(photo_url)),
                os.path.join(os.path.dirname(__file__), photo_url),
                os.path.join(os.path.dirname(__file__), 'images', os.path.basename(photo_url))
            ]
            
            image_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    image_path = path
                    break
            
            if not image_path:
                self.show_no_image()
                return
            
            image = Image.open(image_path)
            image = image.resize((480, 480), Image.Resampling.LANCZOS)
            
            self.current_photo = ImageTk.PhotoImage(image)
            self.photo_label.config(image=self.current_photo)
            
        except Exception as e:
            print(f"Error loading large image: {str(e)}")
            self.show_no_image()
    
    
    def show_no_image(self):
        self.photo_label.config(
            text="Изображение отсутствует",
            font=FONT_MAIN,
            bg=COLOR_SECONDARY_BG
        )


class AddProductWindow(tk.Toplevel):
    
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        
        self.title("Добавить товар")
        self.geometry('500x500+600+200')
        self.resizable(False, False)
        self.configure(bg=COLOR_MAIN_BG)
        
        self.create_widgets()
        self.grab_set()
    
    
    def create_widgets(self):
        tk.Label(
            self, 
            text="Добавить товар", 
            font=FONT_HEADER, 
            bg=COLOR_MAIN_BG, 
            fg=COLOR_TEXT
        ).grid(row=0, column=0, columnspan=2, pady=15)
        
        fields = [
            ("Название:", 1),
            ("Цена:", 2),
            ("Количество:", 3),
            ("Артикул:", 4),
            ("Скидка (%):", 5),
            ("Путь к фото:", 6),
            ("Описание:", 7)
        ]
        
        self.entries = {}
        
        for label_text, row in fields:
            tk.Label(
                self, 
                text=label_text, 
                font=FONT_MAIN, 
                bg=COLOR_MAIN_BG, 
                fg=COLOR_TEXT
            ).grid(row=row, column=0, padx=10, pady=8, sticky='e')
            
            if label_text == "Описание:":
                entry = tk.Text(self, font=FONT_MAIN, width=25, height=5)
                entry.grid(row=row, column=1, padx=10, pady=8)
            else:
                entry = tk.Entry(self, font=FONT_MAIN, width=25)
                entry.grid(row=row, column=1, padx=10, pady=8)
            
            self.entries[label_text] = entry
        
        tk.Button(
            self,
            text="Выбрать файл",
            command=self.select_file,
            bg=COLOR_SECONDARY_BG,
            font=FONT_BUTTON
        ).grid(row=6, column=2, padx=5, pady=8)
        
        btn_frame = tk.Frame(self, bg=COLOR_MAIN_BG)
        btn_frame.grid(row=8, column=0, columnspan=3, pady=20)
        
        tk.Button(
            btn_frame, 
            text="Добавить", 
            command=self.save,
            bg=COLOR_ACCENT,
            fg=COLOR_TEXT,
            font=FONT_BUTTON,
            width=12
        ).pack(padx=5, side=tk.LEFT)
        
        tk.Button(
            btn_frame, 
            text="Отмена", 
            command=self.destroy,
            bg=COLOR_SECONDARY_BG,
            fg=COLOR_TEXT,
            font=FONT_BUTTON,
            width=12
        ).pack(padx=5, side=tk.LEFT)
    
    
    def select_file(self):
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if filename:
            self.entries["Путь к фото:"].delete(0, tk.END)
            self.entries["Путь к фото:"].insert(0, filename)
    
    
    def save(self):
        name = self.entries["Название:"].get().strip()
        price = self.entries["Цена:"].get().strip()
        quantity = self.entries["Количество:"].get().strip()
        article = self.entries["Артикул:"].get().strip()
        discount = self.entries["Скидка (%):"].get().strip()
        photo_path = self.entries["Путь к фото:"].get().strip()
        description = self.entries["Описание:"].get("1.0", tk.END).strip()
        
        if not name or not price or not quantity or not article:
            messagebox.showerror("Ошибка", "Заполните все обязательные поля!")
            return
        
        try:
            price = float(price)
            quantity = int(quantity)
            discount = float(discount) if discount else 0
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат данных!")
            return
        
        if self.db.add_product(name, price, quantity, article, discount):
            messagebox.showinfo("Успех", "Товар успешно добавлен!")
            self.parent.load_data()
            self.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить товар!")


class EditProductWindow(tk.Toplevel):
    
    def __init__(self, parent, db, product_id):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.product_id = product_id
        
        self.title("Редактировать товар")
        self.geometry('500x500+600+200')
        self.resizable(False, False)
        self.configure(bg=COLOR_MAIN_BG)
        
        self.product_info = self.db.get_product_by_id(product_id)
        self.create_widgets()
        self.grab_set()
    
    
    def create_widgets(self):
        tk.Label(
            self, 
            text="Редактировать товар", 
            font=FONT_HEADER, 
            bg=COLOR_MAIN_BG, 
            fg=COLOR_TEXT
        ).grid(row=0, column=0, columnspan=2, pady=15)
        
        fields = [
            ("Название:", 1),
            ("Цена:", 2),
            ("Количество:", 3),
            ("Артикул:", 4),
            ("Скидка (%):", 5),
            ("Путь к фото:", 6),
            ("Описание:", 7)
        ]
        
        self.entries = {}
        
        for label_text, row in fields:
            tk.Label(
                self, 
                text=label_text, 
                font=FONT_MAIN, 
                bg=COLOR_MAIN_BG, 
                fg=COLOR_TEXT
            ).grid(row=row, column=0, padx=10, pady=8, sticky='e')
            
            if label_text == "Описание:":
                entry = tk.Text(self, font=FONT_MAIN, width=25, height=5)
                entry.grid(row=row, column=1, padx=10, pady=8)
            else:
                entry = tk.Entry(self, font=FONT_MAIN, width=25)
                entry.grid(row=row, column=1, padx=10, pady=8)
            
            self.entries[label_text] = entry
        
        tk.Button(
            self,
            text="Выбрать файл",
            command=self.select_file,
            bg=COLOR_SECONDARY_BG,
            font=FONT_BUTTON
        ).grid(row=6, column=2, padx=5, pady=8)
        
        if self.product_info:
            self.entries["Название:"].insert(0, self.product_info.get('product_name', ''))
            self.entries["Цена:"].insert(0, str(self.product_info.get('price', 0)))
            self.entries["Количество:"].insert(0, str(self.product_info.get('quantity', 0)))
            self.entries["Артикул:"].insert(0, self.product_info.get('article', ''))
            self.entries["Скидка (%):"].insert(0, str(self.product_info.get('discount', 0)))
            self.entries["Путь к фото:"].insert(0, self.product_info.get('photo_url', ''))
            self.entries["Описание:"].insert("1.0", self.product_info.get('description', ''))
        
        btn_frame = tk.Frame(self, bg=COLOR_MAIN_BG)
        btn_frame.grid(row=8, column=0, columnspan=3, pady=20)
        
        tk.Button(
            btn_frame, 
            text="Сохранить", 
            command=self.save,
            bg=COLOR_ACCENT,
            fg=COLOR_TEXT,
            font=FONT_BUTTON,
            width=12
        ).pack(padx=5, side=tk.LEFT)
        
        tk.Button(
            btn_frame, 
            text="Отмена", 
            command=self.destroy,
            bg=COLOR_SECONDARY_BG,
            fg=COLOR_TEXT,
            font=FONT_BUTTON,
            width=12
        ).pack(padx=5, side=tk.LEFT)
    
    
    def select_file(self):
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if filename:
            self.entries["Путь к фото:"].delete(0, tk.END)
            self.entries["Путь к фото:"].insert(0, filename)
    
    
    def save(self):
        name = self.entries["Название:"].get().strip()
        price = self.entries["Цена:"].get().strip()
        quantity = self.entries["Количество:"].get().strip()
        article = self.entries["Артикул:"].get().strip()
        discount = self.entries["Скидка (%):"].get().strip()
        photo_path = self.entries["Путь к фото:"].get().strip()
        description = self.entries["Описание:"].get("1.0", tk.END).strip()
        
        if not name or not price or not quantity or not article:
            messagebox.showerror("Ошибка", "Заполните все обязательные поля!")
            return
        
        try:
            price = float(price)
            quantity = int(quantity)
            discount = float(discount) if discount else 0
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат данных!")
            return
        
        if self.db.update_product(self.product_id, name, price, quantity, article, discount):
            messagebox.showinfo("Успех", "Товар успешно обновлен!")
            self.parent.load_data()
            self.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось обновить товар!")


class OrdersWindow(tk.Toplevel):
    
    def __init__(self, parent, db, role):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.role = role
        
        self.title("Заказы")
        self.geometry('800x400+300+150')
        self.configure(bg=COLOR_MAIN_BG)
        
        self.create_widgets()
        self.load_orders()
        self.grab_set()
    
    
    def create_widgets(self):
        tk.Label(
            self, 
            text="Заказы", 
            font=FONT_HEADER, 
            bg=COLOR_MAIN_BG, 
            fg=COLOR_TEXT
        ).pack(pady=10)
        
        columns = ('id', 'date_create', 'date_delivery', 'get_code', 'status', 'username', 'address')
        
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=15)
        self.tree.heading('id', text="ID")
        self.tree.heading('date_create', text="Дата создания")
        self.tree.heading('date_delivery', text="Дата доставки")
        self.tree.heading('get_code', text="Код получения")
        self.tree.heading('status', text="Статус")
        self.tree.heading('username', text="Клиент")
        self.tree.heading('address', text="Адрес")
        
        self.tree.column('id', width='40')
        self.tree.column('date_create', width='100')
        self.tree.column('date_delivery', width='100')
        self.tree.column('get_code', width='80')
        self.tree.column('status', width='100')
        self.tree.column('username', width='100')
        self.tree.column('address', width='150')
        
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Button(
            self, 
            text="Закрыть", 
            command=self.destroy,
            bg=COLOR_SECONDARY_BG,
            fg=COLOR_TEXT,
            font=FONT_BUTTON,
            width=12
        ).pack(pady=10)
    
    
    def load_orders(self):
        rows = self.db.get_orders()
        for row in rows:
            self.tree.insert('', tk.END, values=row)


class ConfigWindow(tk.Toplevel):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Настройка подключения к БД")
        self.geometry('400x250+500+300')
        self.resizable(False, False)
        
        config = Database.load_config()
        
        tk.Label(self, text="Имя базы данных:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.dbname_entry = tk.Entry(self)
        self.dbname_entry.insert(0, config.get('dbname', 'demo') if config else 'demo')
        self.dbname_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(self, text="Пользователь:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.user_entry = tk.Entry(self)
        self.user_entry.insert(0, config.get('user', 'postgres') if config else 'postgres')
        self.user_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(self, text="Пароль:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.password_entry = tk.Entry(self, show='*')
        self.password_entry.insert(0, config.get('password', '') if config else '')
        self.password_entry.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(self, text="Хост:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.host_entry = tk.Entry(self)
        self.host_entry.insert(0, config.get('host', 'localhost') if config else 'localhost')
        self.host_entry.grid(row=3, column=1, padx=10, pady=10)
        
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="Сохранить и подключиться", command=self.save_and_connect).pack()
        
        self.grab_set()
        self.focus_force()
    
    
    def save_and_connect(self):
        dbname = self.dbname_entry.get().strip()
        user = self.user_entry.get().strip()
        password = self.password_entry.get()
        host = self.host_entry.get().strip()
        
        if not dbname or not user or not password or not host:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        
        config = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host
        }
        Database.save_config(config)
        
        try:
            Database.init_db(dbname, user, password, host)
            Database.seed_data(dbname, user, password, host)
            self.destroy()
            self.parent.destroy()
            
            login = LoginWindow(dbname, user, password, host)
        except Exception as e:
            messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к БД:\n{str(e)}")


if __name__ == "__main__":
    def main():
        config = Database.load_config()
        if config and config.get('password'):
            try:
                dbname = config['dbname']
                user = config['user']
                password = config['password']
                host = config['host']
                
                Database.init_db(dbname, user, password, host)
                Database.seed_data(dbname, user, password, host)
                login = LoginWindow(dbname, user, password, host)
                return
            except Exception as e:
                print(f"Error: {e}")
        
        root = tk.Tk()
        root.title("Настройка подключения к БД")
        root.geometry('400x250+500+300')
        root.resizable(False, False)
        root.withdraw()
        config_win = ConfigWindow(root)
        root.mainloop()
    
    main()
