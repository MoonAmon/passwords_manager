import base64
import hashlib
import secrets
import sqlite3
import string

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class PasswordManager:

    def __init__(self, master_key, db_manager):
        self.master_key = master_key
        self.db_manager = db_manager
        self.salt = db_manager.get_salt()
        self.master_key_hash = self.hash_string(self.master_key)
        self.cipher_suite = None
        self.key = None

    @staticmethod
    def hash_string(input_string):
        return hashlib.sha256(input_string.encode()).hexdigest()

    @staticmethod
    def generate_password(length=12):
        all_characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(all_characters) for _ in range(length))
        return password

    def set_password(self, service, password):
        encrypted_password = self.encrypt_password(password)
        self.db_manager.set_password(service, encrypted_password)

    def update_password(self, service, password):
        encrypted_password = self.encrypt_password(password)
        self.db_manager.update_password(service, encrypted_password)

    def encrypt_password(self, password):
        return self.cipher_suite.encrypt(password.encode()).decode()

    def decrypt_password(self, encrypted_password):
        return self.cipher_suite.decrypt(encrypted_password.encode()).decode()

    def delete_passwords(self, service):
        self.db_manager.delete_password(service)

    def get_decrypted_password(self, service):
        encrypted_password = self.db_manager.get_password(service)
        if encrypted_password is not None:
            return self.decrypt_password(encrypted_password)
        else:
            return None

    def verify_master_key(self):
        stored_hash_master_key = self.db_manager.get_master_key_hash()
        hash_master_key = self.hash_string(self.master_key)
        if hash_master_key != stored_hash_master_key:
            return False
        else:
            return True

    def set_key_fernat(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        self.key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        self.cipher_suite = Fernet(self.key)

    def get_services(self):
        results = self.db_manager.get_services()
        return results


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
                INSERT INTO master_key 
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
