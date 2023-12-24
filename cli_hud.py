import npyscreen


class PasswordManagerApp(npyscreen.NPSAppManaged):

    def onStart(self):
        self.addForm('MAIN', PasswordManagerForm, name='Password Manager')


class PasswordManagerForm(npyscreen.ActionFormMinimal):

    def __init__(self, *args, **keywords):
        super().__init__(args, keywords)
        self.service = None
        self.password = None

    def create(self):
        self.service = self.add(npyscreen.TitleText, name='Service')
        self.password = self.add(npyscreen.TitlePassword, name='Password')

    def on_ok(self):
        service = self.service.value
        password = self.service.value

    def on_cancel(self):
        self.parentApp.switchForm(None)


if __name__ == '__main__':
    app = PasswordManagerApp()
    app.run()
