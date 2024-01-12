import sqlite3


class DatabaseManager:

    def __init__(self, db_path):
        self.conn = self.create_connection(db_path)

    def create_connection(self, db_path):
        try:
            conn = sqlite3.connect(db_path)
            return conn
        except Exception as e:
            print(e)

    def close_connection(self):
        if self.conn:
            self.conn.close()

    def set_password(self, service, password):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO passwords (service, password)
                VALUES (?, ?)
            """, (service, password))
            self.conn.commit()
        except Exception as e:
            print(e)

    def delete_password(self, service):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                DELETE FROM passwords WHERE service = ?
            """, (service,))
            self.conn.commit()
        except Exception as e:
            print(e)

    def get_all_passwords(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT passwords.service, passwords.password FROM passwords;
        """)
        result = cursor.fetchall()
        return result

    def get_password(self, service):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT password FROM passwords
            WHERE service = ?;
        """, (service,))
        result = cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            print("Password for the service not found!")

    def set_master_key_hash_and_salt(self, hash_master_key, salt):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO master_key (hash, salt)
                VALUES ( ?,? );
            """, (hash_master_key, salt))
            self.conn.commit()
        except Exception as e:
            print(e)

    def get_master_key_hash(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT hash FROM master_key
            LIMIT 1;
        """)
        result = cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            return print("Master Key hash not found!")

    def get_salt(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT salt FROM master_key
            LIMIT 1;
        """)
        result = cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            print(result[0])
            return print("Salt not found!")

    def update_password(self, service, password):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE passwords
                SET password = ?      
                WHERE service = ?;
            """, (password, service))
            self.conn.commit()
        except Exception as e:
            print(e)

    def get_services(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT service FROM passwords; 
            """)
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(e)
