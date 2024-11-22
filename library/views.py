from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Book, BorrowRecord
from rest_framework.exceptions import ValidationError
from .serializers import RegistrationSerializer, BookSerializer, BorrowRecordSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
from datetime import timedelta, date




class IsLibrarian(BasePermission):
    """
    Allows access only to users who are authenticated as librarians.
    """

    def has_permission(self, request, view):
        # Ensure the user is authenticated and has the 'is_librarian' field set to True
        return request.user.is_authenticated and getattr(request.user, 'is_librarian', False)

# Registration View
class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login View
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_librarian": user.is_librarian,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)


class AddOrUpdateBookView(APIView):
    permission_classes = [IsAuthenticated, IsLibrarian]

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Book added successfully!", "book": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Book updated successfully!", "book": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# List All Books View
class ListBooksView(ListAPIView):
    permission_classes = [IsAuthenticated, IsLibrarian]
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    

class BorrowBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_librarian:
            return Response({"error": "Librarians are not allowed to borrow books."}, status=status.HTTP_403_FORBIDDEN)

        book_id = request.data.get('book_id')
        custom_borrow_date = request.data.get('borrow_date', None)  # Optional borrow_date parameter

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has already borrowed the same book and it hasn't been returned yet
        active_borrow = BorrowRecord.objects.filter(
            borrower=request.user,
            book=book,
            return_date__gt=date.today()
        ).exists()

        if active_borrow:
            return Response({"error": "You already have an active borrow for this book."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user has already borrowed 3 books
        active_borrows_count = BorrowRecord.objects.filter(
            borrower=request.user,
            return_date__gt=date.today()
        ).count()

        if active_borrows_count >= 3:
            return Response({"error": "You cannot borrow more than 3 books at a time."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the book is available
        if not book.is_available:
            return Response({"error": "This book is currently unavailable."}, status=status.HTTP_400_BAD_REQUEST)

        # Parse borrow_date if provided, otherwise use today's date
        if custom_borrow_date:
            try:
                borrow_date = date.fromisoformat(custom_borrow_date)
            except ValueError:
                return Response({"error": "Invalid borrow_date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            borrow_date = date.today()

        # Calculate return_date (14 days from borrow_date)
        return_date = borrow_date + timedelta(days=14)

        # Create the borrow record
        borrow_record = BorrowRecord.objects.create(
            book=book,
            borrower=request.user,
            borrow_date=borrow_date,
            return_date=return_date
        )

        # Mark the book as unavailable
        book.is_available = False
        book.save()

        return Response({
            "message": "Book borrowed successfully!",
            "borrow_record": {
                "id": borrow_record.id,
                "book": borrow_record.book.title,
                "borrow_date": borrow_record.borrow_date,
                "return_date": borrow_record.return_date,
            }
        }, status=status.HTTP_201_CREATED)




class ListBorrowedBooksView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BorrowRecordSerializer

    def get_queryset(self):
        # Filter borrow records for the logged-in user that are still active
        return BorrowRecord.objects.filter(
            borrower=self.request.user,
            return_date__gt=date.today()  # Include only records with return_date in the future
        )
    
    
class ReturnBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_librarian:
            return Response({"error": "Librarians are not allowed to borrow books."}, status=status.HTTP_403_FORBIDDEN)
        
        borrow_record_id = request.data.get('borrow_record_id')

        # Find the borrow record
        try:
            borrow_record = BorrowRecord.objects.get(id=borrow_record_id, borrower=request.user)
        except BorrowRecord.DoesNotExist:
            return Response({"error": "Borrow record not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the book hasn't already been returned
        if borrow_record.return_date <= date.today():
            return Response({"error": "This book has already been returned."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the borrow record and book status
        borrow_record.return_date = date.today()
        borrow_record.book.is_available = True
        borrow_record.book.save()
        borrow_record.save()

        return Response({
            "message": "Book returned successfully!",
            "borrow_record": {
                "id": borrow_record.id,
                "book": borrow_record.book.title,
                "borrow_date": borrow_record.borrow_date,
                "return_date": borrow_record.return_date,
            }
        }, status=status.HTTP_200_OK)


class SearchBooksView(ListAPIView):
    """
    API endpoint to search for books by title or author without using SearchFilter.
    """
    serializer_class = BookSerializer

    def get_queryset(self):
        # Get the search query parameter
        search = self.request.query_params.get('search', None)

        queryset = Book.objects.all()

        # If a search parameter is provided, filter by title or author
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(
                author__icontains=search
            )

        return queryset