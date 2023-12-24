import os
import base64
import sqlite3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class PasswordManager:

    def __init__(self, master_key, db_manager):
        self.master_key = master_key
        self.db_manager = db_manager
        self.salt = os.urandom(16)
        self.pepper = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        self.cipher_suite = Fernet(key)

    def set_password(self, service, password):
        encrypted_password = self.encrypt_password(password)
        self.db_manager.store_password(service, encrypted_password)

    def encrypt_password(self, password):
        return self.cipher_suite.encrypt(password.encode()).decode()

    def decrypt_password(self, encrypted_password):
        return self.cipher_suite.decrypt(encrypted_password.encode()).decode()

    def delete_passwords(self, service):
        self.db_manager.delete_password(service)

    def get_all_passwords(self):
        self.db_manager.get_all_passwords()

    def get_decrypted_password(self, service):
        encrypted_password = self.db_manager.get_password(service)
        if encrypted_password is not None:
            return self.decrypt_password(encrypted_password)
        else:
            return None


class DatabaseManager:

    def __init__(self, db_path):
        self.conn = self.create_connection(db_path)

    @property
    def create_connection(self, db_path):
        conn = None
        try:
            conn = sqlite3.connect(db_path)
            return conn
        except Exception as e:
            print(e)

    def close_connection(self):
        if self.conn:
            self.conn.close()

    def store_password(self, service, password):
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
            SELECT * FROM passwords;
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
        return result[0]

db_man = DatabaseManager()
pass_man = PasswordManager('85738336', db_man)

pass_man.set_password('netflix','cavalodefogo11')
pass_man.set_password('gmail','LouvadorDeGods')

pass_man.get_all_passwords()

print(pass_man.get_decrypted_password('netflix'))



