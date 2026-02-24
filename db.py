import psycopg2
import json
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT



class Database():

    def __init__(self, dbname, user, password, host='localhost', port=5432):

        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        
        self.conn = None
        try:
            self.conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host
            )
            self.cur = self.conn.cursor()
            print("db succesfull")
        except Exception as e:
            print(f"troubles: {str(e)}")


    @staticmethod
    def load_config():
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                return json.load(f)
        return None


    @staticmethod
    def save_config(config):
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)


    @staticmethod
    def init_db(dbname, user, password, host='localhost', port=5432):
        try:
            conn = psycopg2.connect(
                dbname='postgres',
                user=user,
                password=password,
                host=host,
                port=port
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()

            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}'")
            if not cur.fetchone():
                cur.execute(f'CREATE DATABASE {dbname}')
                print(f"Database '{dbname}' created successfully")
            else:
                print(f"Database '{dbname}' already exists")
            
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error creating database: {str(e)}")
            raise

        try:
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            cur = conn.cursor()
            
            tables_sql = [
                """CREATE TABLE IF NOT EXISTS addresses (
                    id serial primary key,
                    index int not null,
                    address varchar(255) not null)""",
                
                """CREATE TABLE IF NOT EXISTS order_status (
                    id serial primary key,
                    status varchar(50))""",
                
                """CREATE TABLE IF NOT EXISTS order_articles (
                    id serial primary key,
                    article_name1 varchar(255),
                    article_quantity1 int,
                    article_name2 varchar(255),
                    article_quantity2 int)""",
                
                """CREATE TABLE IF NOT EXISTS roles (
                    id serial primary key,
                    role varchar(50))""",
                
                """CREATE TABLE IF NOT EXISTS users (
                    id serial primary key,
                    username varchar(255) not null,
                    password varchar(255) not null,
                    role_id int references roles(id),
                    fio varchar(255))""",
                
                """CREATE TABLE IF NOT EXISTS product_name (
                    id serial primary key,
                    name varchar(255))""",
                
                """CREATE TABLE IF NOT EXISTS suppliers (
                    id serial primary key,
                    name varchar(255))""",
                
                """CREATE TABLE IF NOT EXISTS manufacturers (
                    id serial primary key,
                    name varchar(255))""",
                
                """CREATE TABLE IF NOT EXISTS categories (
                    id serial primary key,
                    name varchar(255))""",
                
                """CREATE TABLE IF NOT EXISTS products (
                    id serial primary key,
                    name varchar(255),
                    product_name_id int references product_name(id),
                    price float not null,
                    article varchar(255) not null,
                    supplier_id int references suppliers(id),
                    manufacturer_id int references manufacturers(id),
                    category_id int references categories(id),
                    discount float not null default 0,
                    quantity int not null,
                    description varchar(1000),
                    photo_url varchar(255))""",
                
                """CREATE TABLE IF NOT EXISTS orders (
                    id serial primary key,
                    articles_id int references order_articles(id),
                    date_of_create date not null,
                    date_of_delivery date not null,
                    address int references addresses(id),
                    user_id int references users(id),
                    get_code int not null,
                    order_status_id int references order_status(id))"""
            ]
            
            for sql in tables_sql:
                cur.execute(sql)
                print(f"Table created or already exists")
            
            conn.commit()
            cur.close()
            conn.close()
            print("All tables initialized successfully")
            
        except Exception as e:
            print(f"Error creating tables: {str(e)}")
            raise

    @staticmethod
    def seed_data(dbname, user, password, host='localhost', port=5432):
        try:
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM roles")
            if cur.fetchone()[0] > 0:
                print("Data already exists, skipping seed...")
                cur.close()
                conn.close()
                return

            roles = [
                (1, 'Администратор'),
                (2, 'Менеджер'),
                (3, 'Авторизированный клиент')
            ]
            for role_id, role_name in roles:
                cur.execute("INSERT INTO roles (id, role) VALUES (%s, %s)", (role_id, role_name))
            
            addresses = [
                (420151, 'г. Лесной, ул. Вишневая, 32'),
                (125061, 'г. Лесной, ул. Подгорная, 8'),
                (630370, 'г. Лесной, ул. Шоссейная, 24'),
                (400562, 'г. Лесной, ул. Зеленая, 32'),
                (614510, 'г. Лесной, ул. Маяковского, 47'),
                (410542, 'г. Лесной, ул. Светлая, 46'),
                (620839, 'г. Лесной, ул. Цветочная, 8'),
                (443890, 'г. Лесной, ул. Коммунистическая, 1'),
                (603379, 'г. Лесной, ул. Спортивная, 46'),
                (603721, 'г. Лесной, ул. Гоголя, 41'),
                (410172, 'г. Лесной, ул. Северная, 13'),
                (614611, 'г. Лесной, ул. Молодежная, 50'),
                (454311, 'г.Лесной, ул. Новая, 19'),
                (660007, 'г.Лесной, ул. Октябрьская, 19'),
                (603036, 'г. Лесной, ул. Садовая, 4'),
                (394060, 'г.Лесной, ул. Фрунзе, 43'),
                (410661, 'г. Лесной, ул. Школьная, 50'),
                (625590, 'г. Лесной, ул. Коммунистическая, 20'),
                (625683, 'г. Лесной, ул. 8 Марта'),
                (450983, 'г.Лесной, ул. Комсомольская, 26'),
                (394782, 'г. Лесной, ул. Чехова, 3'),
                (603002, 'г. Лесной, ул. Дзержинского, 28'),
                (450558, 'г. Лесной, ул. Набережная, 30'),
                (344288, 'г. Лесной, ул. Чехова, 1'),
                (614164, 'г.Лесной, ул. Степная, 30'),
                (394242, 'г. Лесной, ул. Коммунистическая, 43'),
                (660540, 'г. Лесной, ул. Солнечная, 25'),
                (125837, 'г. Лесной, ул. Шоссейная, 40'),
                (125703, 'г. Лесной, ул. Партизанская, 49'),
                (625283, 'г. Лесной, ул. Победы, 46'),
                (614753, 'г. Лесной, ул. Полевая, 35'),
                (426030, 'г. Лесной, ул. Маяковского, 44'),
                (450375, 'г. Лесной ул. Клубная, 44'),
                (625560, 'г. Лесной, ул. Некрасова, 12'),
                (630201, 'г. Лесной, ул. Комсомольская, 17'),
                (190949, 'г. Лесной, ул. Мичурина, 26')
            ]
            for index, address in addresses:
                cur.execute("INSERT INTO addresses (index, address) VALUES (%s, %s)", (index, address))

            users = [
                (1, '94d5ous@gmail.com', 'uzWC67', 'Никифорова Весения Николаевна'),
                (1, 'uth4iz@mail.com', '2L6KZG', 'Сазонов Руслан Германович'),
                (1, 'yzls62@outlook.com', 'JlFRCZ', 'Одинцов Серафим Артёмович'),
                (2, '1diph5e@tutanota.com', '8ntwUp', 'Степанов Михаил Артёмович'),
                (2, 'tjde7c@yahoo.com', 'YOyhfR', 'Ворсин Пётр Евгеньевич'),
                (2, 'wpmrc3do@tutanota.com', 'RSbvHv', 'Старикова Елена Павловна'),
                (3, '5d4zbu@tutanota.com', 'rwVDh9', 'Михайлюк Анна Вячеславовна'),
                (3, 'ptec8ym@yahoo.com', 'LdNyos', 'Ситдикова Елена Анатольевна'),
                (3, '1qz4kw@mail.com', 'gynQMT', 'Ворсин Пётр Евгеньевич'),
                (3, '4np6se@mail.com', 'AtnDjr', 'Старикова Елена Павловна')
            ]
            for role_id, username, password, fio in users:
                cur.execute("INSERT INTO users (username, password, role_id, fio) VALUES (%s, %s, %s, %s)", 
                          (username, password, role_id, fio))

            order_statuses = [
                (1, 'Новый'),
                (2, 'Завершен')
            ]
            for status_id, status_name in order_statuses:
                cur.execute("INSERT INTO order_status (id, status) VALUES (%s, %s)", (status_id, status_name))

            order_articles = [
                ('А112Т4', 2, 'F635R4', 2),
                ('H782T5', 1, 'G783F5', 1),
                ('J384T6', 10, 'D572U8', 10),
                ('F572H7', 5, 'D329H3', 4),
                ('А112Т4', 2, 'F635R4', 2),
                ('H782T5', 1, 'G783F5', 1),
                ('J384T6', 10, 'D572U8', 10),
                ('F572H7', 5, 'D329H3', 4),
                ('B320R5', 5, 'G432E4', 1),
                ('S213E3', 5, 'E482R4', 5)
            ]
            for art1, qty1, art2, qty2 in order_articles:
                cur.execute("INSERT INTO order_articles (article_name1, article_quantity1, article_name2, article_quantity2) VALUES (%s, %s, %s, %s)",
                           (art1, qty1, art2, qty2))
            
            categories = [
                (1, 'Женская обувь'),
                (2, 'Мужская обувь')
            ]
            for cat_id, cat_name in categories:
                cur.execute("INSERT INTO categories (id, name) VALUES (%s, %s)", (cat_id, cat_name))
            
            product_names = [
                (1, 'Ботинки'),
                (2, 'Туфли'),
                (3, 'Кроссовки'),
                (4, 'Полуботинки'),
                (5, 'Кеды'),
                (6, 'Тапочки'),
                (7, 'Сапоги')
            ]
            for prod_id, prod_name in product_names:
                cur.execute("INSERT INTO product_name (id, name) VALUES (%s, %s)", (prod_id, prod_name))

            suppliers = [
                (1, 'Kari'),
                (2, 'Обувь для вас')
            ]
            for sup_id, sup_name in suppliers:
                cur.execute("INSERT INTO suppliers (id, name) VALUES (%s, %s)", (sup_id, sup_name))

            manufacturers = [
                (1, 'Kari'),
                (2, 'Marco Tozzi'),
                (3, 'Рос'),
                (4, 'Rieker'),
                (5, 'Alessio Nesca'),
                (6, 'CROSBY')
            ]
            for man_id, man_name in manufacturers:
                cur.execute("INSERT INTO manufacturers (id, name) VALUES (%s, %s)", (man_id, man_name))

            products = [
                ('А112Т4', 1, 4990, 1, 1, 1, 3, 6, 'Женские Ботинки демисезонные kari', 'images/1.jpg'),
                ('F635R4', 1, 3244, 2, 2, 1, 2, 13, 'Ботинки Marco Tozzi женские демисезонные, размер 39, цвет бежевый', 'images/2.jpg'),
                ('H782T5', 2, 4499, 1, 1, 2, 4, 5, 'Туфли kari мужские классика MYZ21AW-450A, размер 43, цвет: черный', 'images/3.jpg'),
                ('G783F5', 1, 5900, 1, 3, 2, 2, 8, 'Мужские ботинки Рос-Обувь кожаные с натуральным мехом', 'images/4.jpg'),
                ('J384T6', 1, 3800, 2, 4, 2, 2, 16, 'B3430/14 Полуботинки мужские Rieker', 'images/5.jpg'),
                ('D572U8', 3, 4100, 2, 3, 2, 3, 6, '129615-4 Кроссовки мужские', 'images/6.jpg'),
                ('F572H7', 2, 2700, 1, 2, 1, 2, 14, 'Туфли Marco Tozzi женские летние, размер 39, цвет черный', 'images/7.jpg'),
                ('D329H3', 4, 1890, 2, 5, 1, 4, 4, 'Полуботинки Alessio Nesca женские 3-30797-47, размер 37, цвет: бордовый', 'images/8.jpg'),
                ('B320R5', 2, 4300, 1, 4, 1, 2, 6, 'Туфли Rieker женские демисезонные, размер 41, цвет коричневый', 'images/9.jpg'),
                ('G432E4', 2, 2800, 1, 1, 1, 3, 15, 'Туфли kari женские TR-YR-413017, размер 37, цвет: черный', 'images/10.jpg'),
                ('S213E3', 4, 2156, 2, 6, 2, 3, 6, '407700/01-01 Полуботинки мужские CROSBY', None),
                ('E482R4', 4, 1800, 1, 1, 1, 2, 14, 'Полуботинки kari женские MYZ20S-149, размер 41, цвет: черный', None),
                ('S634B5', 5, 5500, 2, 6, 2, 3, 0, 'Кеды Caprice мужские демисезонные, размер 42, цвет черный', None),
                ('K345R4', 4, 2100, 2, 6, 2, 2, 3, '407700/01-02 Полуботинки мужские CROSBY', None),
                ('O754F4', 2, 5400, 2, 4, 1, 4, 18, 'Туфли женские демисезонные Rieker артикул 55073-68/37', None),
                ('G531F4', 1, 6600, 1, 1, 1, 12, 9, 'Ботинки женские зимние ROMER арт. 893167-01 Черный', None),
                ('J542F5', 6, 500, 1, 1, 2, 13, 0, 'Тапочки мужские Арт.70701-55-67син р.41', None),
                ('B431R5', 1, 2700, 2, 4, 2, 2, 5, 'Мужские кожаные ботинки/мужские ботинки', None),
                ('P764G4', 2, 6800, 1, 6, 1, 15, 15, 'Туфли женские, ARGO, размер 38', None),
                ('C436G5', 1, 10200, 1, 5, 1, 15, 9, 'Ботинки женские, ARGO, размер 40', None),
                ('F427R5', 1, 11800, 2, 4, 1, 15, 11, 'Ботинки на молнии с декоративной пряжкой FRAU', None),
                ('N457T5', 4, 4600, 1, 6, 1, 3, 13, 'Полуботинки Ботинки черные зимние, мех', None),
                ('D364R4', 2, 12400, 1, 1, 1, 16, 5, 'Туфли Luiza Belly женские Kate-lazo черные из натуральной замши', None),
                ('S326R5', 6, 9900, 2, 6, 2, 17, 15, 'Мужские кожаные тапочки Профиль С.Дали', None),
                ('L754R4', 4, 1700, 1, 1, 1, 2, 7, 'Полуботинки kari женские WB2020SS-26, размер 38, цвет: черный', None),
                ('M542T5', 3, 2800, 2, 4, 2, 18, 3, 'Кроссовки мужские TOFA', None),
                ('D268G5', 2, 4399, 2, 4, 1, 3, 12, 'Туфли Rieker женские демисезонные, размер 36, цвет коричневый', None),
                ('T324F5', 7, 4699, 1, 6, 1, 2, 5, '7 замша Цвет: синий', None),
                ('K358H6', 6, 599, 1, 4, 2, 20, 2, 'Тапочки мужские син р.41', None),
                ('H535R5', 1, 2300, 2, 4, 1, 2, 7, 'Женские Ботинки демисезонные', None)
            ]
            for article, prod_name_id, price, supplier_id, manufacturer_id, category_id, discount, quantity, description, photo_url in products:
                cur.execute("""INSERT INTO products (article, product_name_id, price, supplier_id, manufacturer_id, category_id, discount, quantity, description, photo_url) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                          (article, prod_name_id, price, supplier_id, manufacturer_id, category_id, discount, quantity, description, photo_url))

            cur.execute("SELECT id, fio FROM users WHERE role_id = 2")
            manager_users = {row[1]: row[0] for row in cur.fetchall()}
            
            cur.execute("SELECT id, fio FROM users WHERE role_id = 1")
            admin_users = {row[1]: row[0] for row in cur.fetchall()}
            
            cur.execute("SELECT id, fio FROM users WHERE role_id = 3")
            client_users = {row[1]: row[0] for row in cur.fetchall()}
            
            all_users = {**admin_users, **manager_users, **client_users}
            
            orders_data = [
                (1, '2025-02-27', '2025-04-20', 1, all_users.get('Степанов Михаил Артёмович'), 901, 2),
                (2, '2022-09-28', '2025-04-21', 11, all_users.get('Никифорова Весения Николаевна'), 902, 2),
                (3, '2025-03-21', '2025-04-22', 2, all_users.get('Сазонов Руслан Германович'), 903, 2),
                (4, '2025-02-20', '2025-04-23', 11, all_users.get('Одинцов Серафим Артёмович'), 904, 2),
                (5, '2025-03-17', '2025-04-24', 2, all_users.get('Степанов Михаил Артёмович'), 905, 2),
                (6, '2025-03-01', '2025-04-25', 15, all_users.get('Никифорова Весения Николаевна'), 906, 2),
                (7, '2025-02-28', '2025-04-26', 3, all_users.get('Сазонов Руслан Германович'), 907, 2),
                (8, '2025-03-31', '2025-04-27', 19, all_users.get('Одинцов Серафим Артёмович'), 908, 1),
                (9, '2025-04-02', '2025-04-28', 5, all_users.get('Степанов Михаил Артёмович'), 909, 1),
                (10, '2025-04-03', '2025-04-29', 19, all_users.get('Степанов Михаил Артёмович'), 910, 1)
            ]
            
            for articles_id, date_create, date_delivery, address_id, user_id, get_code, status_id in orders_data:
                if user_id:
                    cur.execute("""INSERT INTO orders (articles_id, date_of_create, date_of_delivery, address, user_id, get_code, order_status_id) 
                               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                              (articles_id, date_create, date_delivery, address_id, user_id, get_code, status_id))
            
            conn.commit()
            cur.close()
            conn.close()
            print("Data seeded successfully!")
            
        except Exception as e:
            print(f"Error seeding data: {str(e)}")
            raise


    def fetch_all(self, query, params=None):
        try:
            self.cur.execute(query, params)
            return self.cur.fetchall()
        except Exception as e:
            print(f"fetchall error : {str(e)}")
            return []

        

    
    def execute_query(self, query, params=None):
        try:
            self.cur.execute(query, params)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"execute error: {str(e)}")
            return False


    def db_close(self):
        if self.cur:
            self.cur.close()

        if self.conn:
            self.conn.close()

        print("db connection closed")


    def check_user(self, username, password):
        try:
            query = "SELECT id, username, role_id FROM users WHERE username = %s AND password = %s"
            self.cur.execute(query, (username, password))
            result = self.cur.fetchone()
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'role_id': result[2]
                }
            return None
        except Exception as e:
            print(f"check_user error: {str(e)}")
            return None


    def get_user_role(self, role_id):
        try:
            query = "SELECT role FROM roles WHERE id = %s"
            self.cur.execute(query, (role_id,))
            result = self.cur.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"get_user_role error: {str(e)}")
            return None


    def init_roles(self):
        try:
            self.cur.execute("SELECT COUNT(*) FROM roles")
            count = self.cur.fetchone()[0]
            
            if count == 0:
                roles = [
                    ('Гость',),
                    ('Клиент',),
                    ('Менеджер',),
                    ('Администратор',)
                ]
                for role in roles:
                    self.cur.execute("INSERT INTO roles (role) VALUES (%s)", role)
                self.conn.commit()
                print("Roles initialized successfully")
            
            self.cur.execute("SELECT COUNT(*) FROM users")
            count = self.cur.fetchone()[0]
            
            if count == 0:
                self.cur.execute("SELECT id, role FROM roles")
                roles_map = {row[1]: row[0] for row in self.cur.fetchall()}
                
                users = [
                    ('admin', 'admin', roles_map.get('Администратор')),
                    ('manager', 'manager', roles_map.get('Менеджер')),
                    ('client', 'client', roles_map.get('Клиент')),
                    ('guest', 'guest', roles_map.get('Гость'))
                ]
                
                for user in users:
                    if user[2]:
                        self.cur.execute(
                            "INSERT INTO users (username, password, role_id) VALUES (%s, %s, %s)",
                            user
                        )
                self.conn.commit()
                print("Test users initialized successfully")
                
        except Exception as e:
            print(f"init_roles error: {str(e)}")
            self.conn.rollback()


    def get_all_products(self):
        query = """
            SELECT p.id, pn.name as product_name, p.price, p.quantity, p.discount 
            FROM products p
            LEFT JOIN product_name pn ON p.product_name_id = pn.id
            ORDER BY p.id
        """
        return self.fetch_all(query)
    


    def get_orders(self):
        query = """
            SELECT o.id, o.date_of_create, o.date_of_delivery, o.get_code, 
                   os.status, u.username, o.address
            FROM orders o
            LEFT JOIN order_status os ON o.order_status_id = os.id
            LEFT JOIN users u ON o.user_id = u.id
            ORDER BY o.id
        """
        return self.fetch_all(query)


    def add_product(self, name, price, quantity, article, discount=0):
        query = "SELECT id FROM product_name WHERE name = %s"
        result = self.fetch_all(query, (name,))

        if result:
            product_name_id = result[0][0]
        else:
            self.execute_query("INSERT INTO product_name (name) VALUES (%s)", (name,))
            result = self.fetch_all("SELECT id FROM product_name WHERE name = %s", (name,))
            product_name_id = result[0][0]

        query = """
            INSERT INTO products 
            (product_name_id, price, quantity, article, discount) 
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (product_name_id, price, quantity, article, discount))


    def update_product(self, product_id, name, price, quantity, article, discount):
        query = "SELECT id FROM product_name WHERE name = %s"
        result = self.fetch_all(query, (name,))

        if result:
            product_name_id = result[0][0]
        else:
            self.execute_query("INSERT INTO product_name (name) VALUES (%s)", (name,))
            result = self.fetch_all("SELECT id FROM product_name WHERE name = %s", (name,))
            product_name_id = result[0][0]

        query = """
            UPDATE products 
            SET product_name_id=%s, price=%s, quantity=%s, article=%s, discount=%s 
            WHERE id=%s
        """
        return self.execute_query(query, (product_name_id, price, quantity, article, discount, product_id))


    def delete_product(self, product_id):
        query = "DELETE FROM products WHERE id = %s"
        return self.execute_query(query, (product_id,))


    def search_products(self, search_text, category=None, sort_by=None, sort_order='ASC'):
        query = """
            SELECT p.id, pn.name as product_name, p.price, p.quantity, p.discount 
            FROM products p
            LEFT JOIN product_name pn ON p.product_name_id = pn.id
            WHERE 1=1
        """
        params = []
        
        if search_text:
            query += " AND (pn.name ILIKE %s OR p.article ILIKE %s)"
            search_pattern = f"%{search_text}%"
            params.extend([search_pattern, search_pattern])
        
        if category:
            query += " AND p.category_id = %s"
            params.append(category)
        
        if sort_by:
            valid_sort_columns = {
                'name': 'pn.name', 
                'price': 'p.price', 
                'quantity': 'p.quantity', 
                'discount': 'p.discount'
            }
            if sort_by in valid_sort_columns:
                query += f" ORDER BY {valid_sort_columns[sort_by]}"
                if sort_order == 'DESC':
                    query += " DESC"
        
        return self.fetch_all(query, tuple(params) if params else None)


    def get_product_by_id(self, product_id):
        query = """
            SELECT p.id, pn.name as product_name, p.price, p.article, 
                   p.discount, p.quantity, p.photo_url, p.description
            FROM products p
            LEFT JOIN product_name pn ON p.product_name_id = pn.id
            WHERE p.id = %s
        """
        try:
            self.cur.execute(query, (product_id,))
            result = self.cur.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'product_name': result[1],
                    'price': result[2],
                    'article': result[3],
                    'discount': result[4],
                    'quantity': result[5],
                    'photo_url': result[6],
                    'description': result[7]
                }
            return None
        except Exception as e:
            print(f"get_product_by_id error: {str(e)}")
            return None
