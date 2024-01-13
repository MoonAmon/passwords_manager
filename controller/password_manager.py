import base64
import hashlib
import secrets
import string

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class PasswordManager:
    """Is the controller of the application. CRUD operations are performed here.

    Atributes:
        master_key (str): The master key used to encrypt and decrypt the passwords.
        db_manager (DatabaseManager): The database manager used to perform CRUD operations on the database.
        salt (bytes): The salt used to generate the key.
        master_key_hash (str): The hash of the master key.
        cipher_suite (Fernet): The cipher suite used to encrypt and decrypt the passwords.
        key (bytes): The key used to encrypt and decrypt the passwords.
    """

    def __init__(self, master_key, db_manager):
        """Initializes the instance based on the master key and the database manager.

        Args:
            master_key (str): The master key used to encrypt and decrypt the passwords.
            db_manager (DatabaseManager): The database manager used to perform CRUD operations on the database.
        """
        self.master_key = master_key
        self.db_manager = db_manager
        self.salt = db_manager.get_salt()
        self.master_key_hash = self.hash_string(self.master_key)
        self.cipher_suite = None
        self.key = None

    @staticmethod  # static method because it doesn't need to access any instance attributes
    def hash_string(input_string):
        return hashlib.sha256(input_string.encode()).hexdigest()

    @staticmethod  # static method because it doesn't need to access any instance attributes
    def generate_password(length=12):
        all_characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(all_characters) for _ in range(length))
        return password

    def set_password(self, service, password):
        """Sets a password for a given service.

        Args:
            service (str): The service for which the password is set.
            password (str): The password to be set.
        """
        encrypted_password = self.encrypt_password(password)
        self.db_manager.set_password(service, encrypted_password)

    def update_password(self, service, password):
        """Updates a password for a given service in the database.

        Args:
            service (str): The service for which the password is updated.
            password (str): The password to be updated.
        """
        encrypted_password = self.encrypt_password(password)
        self.db_manager.update_password(service, encrypted_password)

    def encrypt_password(self, password):
        """Encrypts a password.

        Args:
            password (str): The password to be encrypted.

        Returns:
            str: The encrypted password.
        """
        return self.cipher_suite.encrypt(password.encode()).decode()

    def decrypt_password(self, encrypted_password):
        """Decrypts a password.

        Args:
            encrypted_password (str): The password to be decrypted.

        Returns:
            str: The decrypted password.
        """
        return self.cipher_suite.decrypt(encrypted_password.encode()).decode()

    def delete_passwords(self, service):
        """Deletes a password for a given service.

        Args:
            service (str): The service for which the password is deleted.
        """
        self.db_manager.delete_password(service)

    def get_decrypted_password(self, service):
        """Gets the decrypted password for a given service.

        Args:
            service (str): The service for which the password is retrieved.

        Returns:
            str: The decrypted password.
        """
        encrypted_password = self.db_manager.get_password(service)
        if encrypted_password is not None:
            return self.decrypt_password(encrypted_password)
        else:
            return None

    def verify_master_key(self):
        """Verifies the master key.

        Returns:
            bool: True if the master key is correct, False otherwise.
        """
        stored_hash_master_key = self.db_manager.get_master_key_hash()
        hash_master_key = self.hash_string(self.master_key)
        if hash_master_key != stored_hash_master_key:
            return False
        else:
            return True

    def set_key_fernat(self):
        """Sets the key and the cipher suite used to encrypt and decrypt the passwords."""
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
        """Gets all the services from the database.

        Returns:
            list: A list of tuples containing the service and the password.
        """
        results = self.db_manager.get_services()
        return results
