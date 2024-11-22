# Library Management System

This is a Django-based library management system that allows users to register, borrow, return books, and receive due date notifications. Librarians have additional privileges for managing the library's book inventory. The system uses Django REST Framework for the API and Celery for background tasks, such as sending email notifications for books due soon.

## Features

- **User Registration and Login**: Users and librarians can register, log in, and manage their accounts.
- **Book Management**: Librarians can add, update, and view books.
- **Borrowing and Returning Books**: Users can borrow and return books with automatic tracking of borrow and return dates.
- **Notifications**: Email notifications are sent to users when their borrowed books are due soon (3 days before the return date).
- **Search**: Search for books by title or author.
- **Permissions**: Permissions are managed using Django's built-in authentication system, and custom permissions are implemented for librarians.

## Tech Stack

- **Django**: Python web framework for building the app.
- **Django REST Framework**: For creating the API.
- **Celery**: For background tasks such as sending email notifications.
- **Sqllite**: Used as the message broker for Celery.
- **Django Celery Beat**: For scheduling periodic tasks (e.g., sending due date reminders).
- **sqlite3**: Database backend.

# Installation

Follow these steps to set up and run the library management system:

### 1. Clone the repository
 git clone https://github.com/17prateek12/Library_management .

### 2. SetUp virtual Enviroment
 python -m virtualenv server

### 3. Install packages
 pip install -r requirements.txt 

### 4. Start with following
python manage.py runserver
celery -A library_management worker --loglevel=info
celery -A library_management beat --loglevel=info

### To login as librarian
username:17prateek12
password: Prateek@1712
email associated: 17prateek12@gmail.com

### To login as user
username:walkclick
password: Prateek@1712
email associated: prateeksharma1885@gmail.com

username:walkclick12
password: Prateek@1712
email associated: 99prateek12@gmail.com



