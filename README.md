# Password Manager Application

This is a simple password manager application developed in Python. It allows users to securely store, retrieve, update, and delete passwords for various services. The application uses SQLite for data storage and cryptography for password encryption and decryption.

## Features

- Secure passwords storage
- Password encryption and decryption
- Password retrival, update, deletion
- Master key creation and verification

## Installation

1. Ensure you have Python installed on your system.
2. Clone the repository to your local machine using the following command:

````shell
git clone https://github.com/MoonAmon/passwords_manager.git
````

3. Navigate to the project directory:

```shell
cd passwordManger
```

4. Install the required dependencies:
```shell
pip install -r requirements.txt
```

## Usage

To start the application, run the following command in the project directory:
```shell
python main.py
```
The application will prompt you to enter your master key. If you are using the application for the first time, you will be asked to create a master key.

The main menu of the application provides the following options:

1. Search Password
2. Store Password
3. Delete Password
4. Update Password
5. Exit

Press the number corresponding of the desired operation.

## Contributing

Thank you for considering contributing to this project! As it's my first CRUD project, I'm eager to receive suggestions, corrections, and enhancements from the community. Please follow these guidelines to contribute effectively:

### How to Contribute

1. Fork the repository to your GitHub account.
2. Create a new branch for your feature or bug fix:

   ```shell
   git checkout -b feature/your-feature-name

## License

This project is licensed under the MIT License.