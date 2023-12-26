import os

import npyscreen
import main
from main import PasswordManager


class MasterKeyForm(npyscreen.ActionFormMinimal):

    def create(self):
        self.master_key = self.add(npyscreen.TitlePassword, name='Master Key')
        self.create_master_key_button = self.add(npyscreen.ButtonPress, name='Create Master Key')
        self.create_master_key_button.whenPressed = self.go_to_create_master_key

    def go_to_create_master_key(self):
        self.parentApp.switchForm('CreateMasterKeyForm')
    def on_ok(self):
        master_key = self.master_key.value

        self.parentApp.password_manager.master_key = master_key

        if self.parentApp.password_manager.verify_master_key():
            self.parentApp.password_manager.set_key_Fernat()
            cipher_suite = self.parentApp.password_manager.key
            npyscreen.notify_confirm(str(cipher_suite))
            self.parentApp.switchForm('PasswordManagerForm')
        else:
            npyscreen.notify_confirm("Wrong master key!", title='Error')

    def on_cancel(self):
        self.parentApp.switchForm(None)


class PasswordManagerApp(npyscreen.NPSAppManaged):

    def onStart(self):
        self.password_manager = main.PasswordManager('none', main.DatabaseManager('passwords_db'))
        self.addForm('MAIN', MasterKeyForm, name='Password Manager')
        self.addForm('PasswordManagerForm', PasswordManagerForm, name='Password Manager')
        self.addForm('CreateMasterKeyForm', CreateMasterKeyForm, name='Create Master Key')
        self.addForm('DisplayPasswordsForm', DisplayPasswordsForm, name='List Passwords')


class PasswordManagerForm(npyscreen.ActionFormMinimal):

    def create(self):
        self.service = self.add(npyscreen.TitleText, name='Service')
        self.password = self.add(npyscreen.TitlePassword, name='Password')
        self.passwords_display = self.add(npyscreen.ButtonPress, name='Display Passwords')
        self.passwords_display.whenPressed = self.go_to_display_passwords


    def go_to_display_passwords(self):
        self.parentApp.switchForm('DisplayPasswordsForm')

    def on_ok(self):
        service = self.service.value
        password = self.password.value

        if len(service) > 0 and len(password) > 0:
            self.parentApp.password_manager.set_password(service, password)
            npyscreen.notify_confirm('Service and Password add with success!')
        else:
            npyscreen.notify_confirm('Service and Password field must not empty!')

    def on_cancel(self):
        self.parentApp.switchForm('MasterKeyForm')

class CreateMasterKeyForm(npyscreen.ActionFormMinimal):

    def create(self):
        self.master_key = self.add(npyscreen.TitlePassword, name='Master Key')
        self.confirm_master_key = self.add(npyscreen.TitlePassword, name='Confirm Master Key')

    def on_ok(self):
        master_key = self.master_key.value
        confirm_master_key = self.confirm_master_key.value

        if master_key == confirm_master_key:
            npyscreen.notify_confirm('Master Key create with success!')
            hash_master_key = password_manager.hash_string(master_key)
            salt = os.urandom(32)
            password_manager.db_manager.set_master_key_hash_and_salt(hash_master_key, salt)

            self.parentApp.switchForm('MAIN')
        else:
            npyscreen.notify_confirm('Master Key must be identical!', title='Error')

class DisplayPasswordsForm(npyscreen.ActionFormMinimal):

    def create(self):
        self.passwords_list = self.add(npyscreen.MultiLineAction, name='Passwords', values=[])

    def beforeEditing(self):
        passwords = self.parentApp.password_manager.db_manager.get_all_passwords()
        npyscreen.notify_confirm(str(passwords))
        decrypted_passwords = [(service, self.parentApp.password_manager.decrypt_password(password)) for service, password in passwords]
        self.passwords_list.values = [f'Service: {service}, Password: {password}' for service, password in decrypted_passwords]
        self.passwords_list.display()

    def on_ok(self):
        self.parentApp.switchForm('PasswordManagerForm')

    def on_cancel(self):
        self.parentApp.switchForm('PasswordManagerForm')

if __name__ == '__main__':
    db_path = 'passwords_db'
    db_manager = main.DatabaseManager(db_path)
    password_manager: PasswordManager = main.PasswordManager('none', db_manager)
    app = PasswordManagerApp()
    app.run()

