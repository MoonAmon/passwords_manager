from controller.password_manager import PasswordManager
from model.database import DatabaseManager

import os
import npyscreen
import pyperclip


class CheckMasterKeyForm(npyscreen.ActionFormMinimal):
    def create(self):
        pass

    def afterEditing(self):
        pass


class MasterKeyForm(npyscreen.ActionFormMinimal):

    def create(self):
        self.master_key = self.add(npyscreen.TitlePassword, name='Master Key')
        self.exit_bt = self.add(npyscreen.ButtonPress, name='Exit')
        self.exit_bt.whenPressed = self.exit

    def on_ok(self):
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
        self.parentApp.setNextForm(None)
        self.parentApp.switchForm(None)


class PasswordManagerApp(npyscreen.NPSAppManaged):

    def onStart(self):
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

    def create(self):
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
        })

    def search_password(self, input):
        self.parentApp.switchForm('DisplayPasswordsForm')

    def store_password(self, input):
        self.parentApp.switchForm('PasswordManagerForm')

    def delete_password(self, input):
        self.parentApp.switchForm('DeletePasswordForm')

    def update_password(self, input):
        self.parentApp.switchForm('UpdatePasswordForm')

    def exit(self, input):
        self.parentApp.setNextForm(None)
        self.parentApp.switchForm(None)


class PasswordManagerForm(npyscreen.ActionFormMinimal):

    def create(self):
        self.service = self.add(npyscreen.TitleText, name='Service')
        self.password = self.add(npyscreen.TitlePassword, name='Password')

        self.cancel_bt = self.add(npyscreen.ButtonPress, name='Back')
        self.cancel_bt.whenPressed = self.on_cancel

        self.length_gen_password = self.add(npyscreen.TitleSlider, name='Length Password', lowest=12)
        self.password_generator_bt = self.add(npyscreen.ButtonPress, name='Generate Strong Password')
        self.password_generator_bt.whenPressed = self.gen_strong_password

    def go_to_display_passwords(self):
        self.parentApp.switchForm('DisplayPasswordsForm')

    def gen_strong_password(self):
        length_password = int(self.length_gen_password.value)
        new_password = self.parentApp.password_manager.generate_password(length_password)

        self.password.value = new_password
        npyscreen.notify_confirm('New Password create with success!')

    def on_ok(self):
        service = self.service.value
        password = self.password.value

        if len(service) > 0 and len(password) > 0:
            self.parentApp.password_manager.set_password(service, password)
            npyscreen.notify_confirm('Service and Password add with success!')
            self.service.value = ''
            self.password.value = ''
        else:
            npyscreen.notify_confirm('Service and Password field must not empty!')

    def on_cancel(self):
        self.parentApp.switchForm('PasswordManagerMenu')


class CreateMasterKeyForm(npyscreen.ActionFormMinimal):

    def create(self):
        self.master_key = self.add(npyscreen.TitlePassword, name='Master Key')
        self.confirm_master_key = self.add(npyscreen.TitlePassword, name='Confirm Master Key')

    def on_ok(self):
        master_key = self.master_key.value
        confirm_master_key = self.confirm_master_key.value

        if master_key == confirm_master_key:
            npyscreen.notify_confirm('Master Key create with success!')
            hash_master_key = self.parentApp.password_manager.hash_string(master_key)
            salt = os.urandom(32)
            self.parentApp.password_manager.db_manager.set_master_key_hash_and_salt(hash_master_key, salt)
            self.parentApp.switchForm('MAIN')
        else:
            npyscreen.notify_confirm('Master Key must be identical!', title='Error')


class DisplayPasswordsForm(npyscreen.ActionFormMinimal):

    def create(self):
        self.service_search = self.add(npyscreen.TitleText, name='Service')
        self.show_services_bt = self.add(npyscreen.ButtonPress, name='Show Available Services')
        self.show_services_bt.whenPressed = self.show_services
        self.cancel_bt = self.add(npyscreen.ButtonPress, name='Back')
        self.cancel_bt.whenPressed = self.on_cancel

    def on_ok(self):
        service = self.service_search.value
        password_result = self.parentApp.password_manager.get_decrypted_password(service)

        if password_result is not None:
            pyperclip.copy(password_result)
            npyscreen.notify_confirm('Password copied to clipboard!')

            self.service_search.value = ''
        else:
            npyscreen.notify_confirm('Password not found!', title='Error')


    def show_services(self):
        services = self.parentApp.password_manager.get_services()
        if services:
            services_str = '\n'.join(service[0] for service in services)
            npyscreen.notify_confirm(f"Available services: {services_str}")
        else:
            npyscreen.notify_confirm("No services found!")

    def on_cancel(self):
        self.parentApp.switchForm('PasswordManagerMenu')


class UpdatePasswordForm(npyscreen.ActionFormMinimal):

    def create(self):
        self.service = self.add(npyscreen.TitleText, name='Service')
        self.password = self.add(npyscreen.TitlePassword, name='Password')
        self.length_gen_password = self.add(npyscreen.TitleSlider, name='Length Password')
        self.gen_password_bt = self.add(npyscreen.ButtonPress, name='Generate Password')
        self.gen_password_bt.whenPressed = self.gen_strong_password
        self.cancel_bt = self.add(npyscreen.ButtonPress, name='Back')
        self.cancel_bt.whenPressed = self.on_cancel

    def gen_strong_password(self):
        length_password = int(self.length_gen_password.value)
        new_password = self.parentApp.password_manager.generate_password(length_password)

        self.password.value = new_password
        npyscreen.notify_confirm('New Password create with success!')

    def on_ok(self):
        new_service = self.service.value
        new_password = self.password.value

        if len(new_service) > 0 and len(new_password) > 0:
            self.parentApp.password_manager.update_password(new_service, new_password)
            npyscreen.notify_confirm('Password update with success!')
        else:
            npyscreen.notify_confirm('Password and Service field must not be empty!')

    def on_cancel(self):
        self.parentApp.switchForm('PasswordManagerMenu')


class DeletePasswordForm(npyscreen.ActionFormMinimal):

    def create(self):
        self.service = self.add(npyscreen.TitleText, name='Service')
        self.cancel_bt = self.add(npyscreen.ButtonPress, name='Back')
        self.cancel_bt.whenPressed = self.on_cancel

    def on_ok(self):
        service = self.service.value
        password_result = self.parentApp.password_manager.get_decrypted_password(service)
        if password_result:
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
        self.parentApp.switchForm('PasswordManagerMenu')
