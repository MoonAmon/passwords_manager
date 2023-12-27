import secrets
import string
def generate_password(length=12):
    all_characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(all_characters) for _ in range(length))
    return password

password_test = generate_password(30)

print(password_test)