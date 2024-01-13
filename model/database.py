import sqlite3


class DatabaseManager:
    """To manage the database operations.

    Is used to create a connection to the database, to close the connection,
    to set a password for a given service, to delete a password for a given service,

    Atributes:
        conn: The connection object to the database.
    """
    def __init__(self, db_path):
        """Initializes the instance based on the database path.

        Args:
            db_path (str): The path to the SQLite database.
        """
        self.conn = self.create_connection(db_path)

    def create_connection(self, db_path):
        """Creates a connection to the database.

        Args:
            db_path (str): The path to the SQLite database.

        Returns:
            conn: The connection object to the database.
        """
        try:
            conn = sqlite3.connect(db_path)
            return conn
        except Exception as e:
            print(e)

    def close_connection(self):
        """Closes the connection to the database."""
        if self.conn:
            self.conn.close()

    def set_password(self, service, password):
        """Sets a password for a given service.

        Args:
            service (str): The service for which the password is set.
            password (str): The password to be set.
        """
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
        """Deletes a password for a given service.

        Args:
            service (str): The service for which the password is deleted.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                DELETE FROM passwords WHERE service = ?
            """, (service,))
            self.conn.commit()
        except Exception as e:
            print(e)

    def get_all_passwords(self):
        """Gets all the passwords from the database.

        Return:
            result (list): A list of tuples containing the service and the password.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT passwords.service, passwords.password FROM passwords;
        """)
        result = cursor.fetchall()
        return result

    def get_password(self, service):
        """Gets the password for a given service.

        Args:
            service (str): The service for which the password is retrieved.

        Return:
            result (str): The password for the given service.
        """
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
        """Sets the hash of the master key and the salt.

        Args:
            hash_master_key (str): The hash of the master key.
            salt (bytes): The salt.

        Raise:
            Exception: If the query fails.
        """
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
        """Gets the hash of the master key.

        Return:
            result (str): The hash of the master key.

        Raise:
            Exception: If the query is empty.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT hash FROM master_key
            LIMIT 1;
        """)
        result = cursor.fetchone()
        if result is None:
            raise Exception("Master Key hash not found!")
        else:
            return result[0]

    def get_salt(self):
        """Gets the salt.

        Return:
            result (bytes): The salt.

        Raise:
            Exception: If the query fails.
        """
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
        """Updates the password for a given service.

        Args:
            service (str): The service for which the password is updated.
            password (str): The new password.

        Raise:
            Exception: If the query fails.
        """
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
        """Gets all the services from the database.

        Return:
            results (list): A list of tuples containing the service.

        Raise:
            Exception: If the query fails.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT service FROM passwords; 
            """)
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(e)
