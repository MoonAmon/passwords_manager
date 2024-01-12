from model.database import DatabaseManager
from controller.password_manager import PasswordManager
from view.cli_hud import PasswordManagerApp


if __name__ == '__main__':
    db_path = 'passwords_db'
    db_manager = DatabaseManager(db_path)
    password_manager: PasswordManager = PasswordManager('none', db_manager)
    app = PasswordManagerApp()
    app.run()
