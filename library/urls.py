from django.urls import path
from .views import RegistrationView, LoginView, AddOrUpdateBookView, ListBooksView , BorrowBookView, ListBorrowedBooksView, ReturnBookView, SearchBooksView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('books/', ListBooksView.as_view(), name='list_books'),
    path('books/add/', AddOrUpdateBookView.as_view(), name='add_book'),
    path('books/update/<int:pk>/', AddOrUpdateBookView.as_view(), name='update_book'),
    path('books/borrow/', BorrowBookView.as_view(), name='borrow_book'),
    path('books/borrowed/', ListBorrowedBooksView.as_view(), name='list_borrowed_books'),
    path('books/return/', ReturnBookView.as_view(), name='return_book'),
    path('books/search/', SearchBooksView.as_view(), name='search-books'),
]
