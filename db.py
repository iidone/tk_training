import psycopg2



class Database():

    def __init__(self, dbname, user, password, host='localhost', port=5432):

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


    def fetch_all(self, query, params=None):
        try:
            self.cur.execute(query, params)
            return self.cur.fetchall(   )
        except Exception as e:
            print(f"error: {str(e)}")
            return []


    def db_close(self):
        if self.cur:
            self.cur.close()

        if self.conn:
            self.conn.close()

        print("db connection closed")