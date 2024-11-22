from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    first_name = models.CharField(max_length=30, blank=True)  # Customize length or add constraints if needed
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)  # Ensure email is unique
    username = models.CharField(max_length=30, unique=True)
    is_librarian = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({'Librarian' if self.is_librarian else 'User'})"
    

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BorrowRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField()
