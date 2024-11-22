from django.contrib import admin
from .models import BorrowRecord, Book, User

# Register your models here.
admin.site.register(BorrowRecord)
admin.site.register(Book)
admin.site.register(User)
