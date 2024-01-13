from controller.password_manager import PasswordManager
from model.database import DatabaseManager

import os
import npyscreen
import pyperclip


# TODO: Add the logic for the first time the user runs the application.
# Master key is 12345

class MasterKeyForm(npyscreen.ActionFormMinimal):
    """The form to enter the master key."""

    def create(self):
        """Creates the applications objects."""
        self.master_key = self.add(npyscreen.TitlePassword, name='Master Key')
        self.exit_bt = self.add(npyscreen.ButtonPress, name='Exit')
        self.exit_bt.whenPressed = self.exit

    def on_ok(self):
        """Checks if the master key is correct when the user presses the OK button."""
        master_key = self.master_key.value

        master_key_check = self.parentApp.password_manager.db_manager.get_master_key_hash()
        if master_key_check is None:
            self.parentApp.switchForm('CreateMasterKeyForm')

        self.parentApp.password_manager.master_key = master_key

        if self.parentApp.password_manager.verify_master_key():
            self.parentApp.password_manager.set_key_fernat()
            self.parentApp.switchForm('PasswordManagerMenu')
        else:
            npyscreen.notify_confirm("Wrong master key!", title='Error')

    def exit(self):
        """Exits the application when the user presses the Exit button."""
        self.parentApp.setNextForm(None)
        self.parentApp.switchForm(None)


class PasswordManagerApp(npyscreen.NPSAppManaged):
    """Initializes the application."""

    def onStart(self):
        """Starts the forms of the application."""
        self.password_manager = PasswordManager('none', DatabaseManager('passwords_db'))
        self.addForm('MAIN', MasterKeyForm, name='Password Manager')
        self.addForm('PasswordManagerMenu', PasswordManagerMenu, name='Password Manager Menu')
        self.addForm('PasswordManagerForm', PasswordManagerForm, name='Password Manager')
        self.addForm('CreateMasterKeyForm', CreateMasterKeyForm, name='Create Master Key')
        self.addForm('DisplayPasswordsForm', DisplayPasswordsForm, name='List Password')
        self.addForm('UpdatePasswordForm', UpdatePasswordForm, name='Update Password')
        self.addForm('DeletePasswordForm', DeletePasswordForm, name='Delete Password')
        self.addForm('CheckMasterKeyForm', CheckMasterKeyForm, name='Check Master Key')

    def onCleanExit(self):
        self.switchForm('CheckMasterKeyForm')


class PasswordManagerMenu(npyscreen.Form):
    """The menu form of the application."""

    def create(self):
        """Creates the menu."""
        self.menu = self.add(npyscreen.MultiLineAction, name='Password Manager Menu', values=[
            'Search Password - 1',
            'Store Password - 2',
            'Delete Password - 3',
            'Update Password - 4',
            'Exit - 5'
        ])
        self.menu.add_handlers({
            '1': self.search_password,
            '2': self.store_password,
            '3': self.delete_password,
            '4': self.update_password,
            '5': self.exit
        })  # TODO: Fix the bug that the option is not selected when the user presses the enter key.

    def search_password(self, input):  # For some reason the input parameter is needed,
        # without it the option is not selected.
        """Switches to the SearchPasswordForm when the user presses the 1 key."""
        self.parentApp.switchForm('DisplayPasswordsForm')

    def store_password(self, input):
        """Switches to the StorePasswordForm when the user presses the 2 key."""
        self.parentApp.switchForm('PasswordManagerForm')

    def delete_password(self, input):
        """Switches to the DeletePasswordForm when the user presses the 3 key."""
        self.parentApp.switchForm('DeletePasswordForm')

    def update_password(self, input):
        """Switches to the UpdatePasswordForm when the user presses the 4 key."""
        self.parentApp.switchForm('UpdatePasswordForm')

    def exit(self, input):
        """Exits the application when the user presses the 5 key."""
        self.parentApp.setNextForm(None)
        self.parentApp.switchForm(None)


class PasswordManagerForm(npyscreen.ActionFormMinimal):
    """The form to store a password."""

    def create(self):
        """Creates the applications objects."""
        self.service = self.add(npyscreen.TitleText, name='Service')
        self.password = self.add(npyscreen.TitlePassword, name='Password')

        self.cancel_bt = self.add(npyscreen.ButtonPress, name='Back')
        self.cancel_bt.whenPressed = self.on_cancel

        self.length_gen_password = self.add(npyscreen.TitleSlider, name='Length Password', lowest=12)
        self.password_generator_bt = self.add(npyscreen.ButtonPress, name='Generate Strong Password')
        self.password_generator_bt.whenPressed = self.gen_strong_password

    def go_to_display_passwords(self):
        """Switches to the DisplayPasswordsForm."""
        self.parentApp.switchForm('DisplayPasswordsForm')

    def gen_strong_password(self):
        """Generates a strong password based on the length of the password slider."""
        length_password = int(self.length_gen_password.value)
        new_password = self.parentApp.password_manager.generate_password(length_password)

        self.password.value = new_password
        npyscreen.notify_confirm('New Password create with success!')

    def on_ok(self):
        """Stores the password when the user presses the OK button."""
        service = self.service.value
        password = self.password.value

        if len(service) > 0 and len(password) > 0:  # Checks if the service and password fields are not empty.
            self.parentApp.password_manager.set_password(service, password)
            npyscreen.notify_confirm('Service and Password add with success!')
            self.service.value = ''
            self.password.value = ''
        else:
            npyscreen.notify_confirm('Service and Password field must not empty!')

    def on_cancel(self):
        """Switches to the PasswordManagerMenu when the user presses the Cancel button."""
        self.parentApp.switchForm('PasswordManagerMenu')


class CreateMasterKeyForm(npyscreen.ActionFormMinimal):
    """The form to create the master key."""

    def create(self):
        """Creates the applications objects."""
        self.master_key = self.add(npyscreen.TitlePassword, name='Master Key')
        self.confirm_master_key = self.add(npyscreen.TitlePassword, name='Confirm Master Key')

    def on_ok(self):
        """Creates the master key when the user presses the OK button."""
        master_key = self.master_key.value
        confirm_master_key = self.confirm_master_key.value

        if master_key == confirm_master_key:  # Checks if the master key and confirm master key are identical.
            npyscreen.notify_confirm('Master Key create with success!')
            hash_master_key = self.parentApp.password_manager.hash_string(master_key)
            salt = os.urandom(32)
            self.parentApp.password_manager.db_manager.set_master_key_hash_and_salt(hash_master_key, salt)
            self.parentApp.switchForm('MAIN')
        else:
            npyscreen.notify_confirm('Master Key must be identical!', title='Error')


class DisplayPasswordsForm(npyscreen.ActionFormMinimal):
    """The form to display the passwords."""

    def create(self):
        """Creates the applications objects."""
        self.service_search = self.add(npyscreen.TitleText, name='Service')
        self.show_services_bt = self.add(npyscreen.ButtonPress, name='Show Available Services')
        self.show_services_bt.whenPressed = self.show_services
        self.cancel_bt = self.add(npyscreen.ButtonPress, name='Back')
        self.cancel_bt.whenPressed = self.on_cancel

    def on_ok(self):
        """Copies the password to the clipboard when the user presses the OK button."""
        service = self.service_search.value
        password_result = self.parentApp.password_manager.get_decrypted_password(service)

        if password_result:  # Checks if the password is found.
            pyperclip.copy(password_result)
            npyscreen.notify_confirm('Password copied to clipboard!')

            self.service_search.value = ''
        else:
            npyscreen.notify_confirm('Password not found!', title='Error')

    def show_services(self):
        """Shows the available services when the user presses the Show Available Services button."""
        services = self.parentApp.password_manager.get_services()
        if services:  # Checks if the services list is found.
            services_str = '\n'.join(service[0] for service in services)
            npyscreen.notify_confirm(f"Available services: {services_str}")
        else:
            npyscreen.notify_confirm("No services found!")

    def on_cancel(self):
        """Switches to the PasswordManagerMenu when the user presses the Cancel button."""
        self.parentApp.switchForm('PasswordManagerMenu')


class UpdatePasswordForm(npyscreen.ActionFormMinimal):
    """The form to update a password."""

    def create(self):
        """Creates the applications objects."""
        self.service = self.add(npyscreen.TitleText, name='Service')
        self.password = self.add(npyscreen.TitlePassword, name='Password')
        self.length_gen_password = self.add(npyscreen.TitleSlider, name='Length Password')
        self.gen_password_bt = self.add(npyscreen.ButtonPress, name='Generate Password')
        self.gen_password_bt.whenPressed = self.gen_strong_password
        self.cancel_bt = self.add(npyscreen.ButtonPress, name='Back')
        self.cancel_bt.whenPressed = self.on_cancel

    def gen_strong_password(self):
        """Generates a strong password based on the length of the password slider."""
        length_password = int(self.length_gen_password.value)
        new_password = self.parentApp.password_manager.generate_password(length_password)

        self.password.value = new_password
        npyscreen.notify_confirm('New Password create with success!')

    def on_ok(self):
        """Updates the password when the user presses the OK button."""
        new_service = self.service.value
        new_password = self.password.value

        if new_service and new_password:  # Checks if the service and password fields are not empty.
            self.parentApp.password_manager.update_password(new_service, new_password)
            npyscreen.notify_confirm('Password update with success!')
        else:
            npyscreen.notify_confirm('Password and Service field must not be empty!')

    def on_cancel(self):
        self.parentApp.switchForm('PasswordManagerMenu')


class DeletePasswordForm(npyscreen.ActionFormMinimal):
    """The form to delete a password."""

    def create(self):
        """Creates the applications objects."""
        self.service = self.add(npyscreen.TitleText, name='Service')
        self.cancel_bt = self.add(npyscreen.ButtonPress, name='Back')
        self.cancel_bt.whenPressed = self.on_cancel

    def on_ok(self):
        """Deletes the password when the user presses the OK button."""
        service = self.service.value
        password_result = self.parentApp.password_manager.get_decrypted_password(service)

        if password_result:  # Checks if the password is found.
            confirm = npyscreen.notify_yes_no("Are you sure you want to delete the password for service: " + service,
                                              title="Warning Delete")
            if confirm:
                self.parentApp.password_manager.delete_passwords(service)
                npyscreen.notify_confirm("Password deleted successfully!")
            else:
                pass
        elif service is None:
            npyscreen.notify_confirm("Service field must not be empty!")
        else:
            npyscreen.notify_confirm(f"Password for {service} not found!")

    def on_cancel(self):
        """Switches to the PasswordManagerMenu when the user presses the Cancel button."""
        self.parentApp.switchForm('PasswordManagerMenu')
