from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Roles(models.TextChoices):
        STUDENT = 'student', 'Student'
        ADMIN = 'admin', 'Admin/Librarian'

    class Departments(models.TextChoices):
        CSE = 'CSE', 'CSE'
        ECE = 'ECE', 'ECE'
        ME = 'ME', 'ME'
        CIVIL = 'CIVIL', 'CIVIL'
        EEE = 'EEE', 'EEE'
        CHEM = 'CHEM', 'CHEM'

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STUDENT)
    department = models.CharField(max_length=20, choices=Departments.choices, blank=True, null=True)
    year = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    semester = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    mobile_number = models.CharField(max_length=15, blank=True, null=True, unique=True)


class Book(models.Model):
    class Departments(models.TextChoices):
        CSE = 'CSE', 'CSE'
        ECE = 'ECE', 'ECE'
        ME = 'ME', 'ME'
        CIVIL = 'CIVIL', 'CIVIL'
        EEE = 'EEE', 'EEE'
        CHEM = 'CHEM', 'CHEM'

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    department = models.CharField(max_length=20, choices=Departments.choices)
    year = models.PositiveSmallIntegerField()
    semester = models.PositiveSmallIntegerField()
    isbn = models.CharField(max_length=20, unique=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True, help_text="Direct link to the cover image")
    available_copies = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    content_file = models.FileField(upload_to='books/', blank=True, null=True)
    content_url = models.URLField(max_length=500, blank=True, null=True, help_text="Direct link to the PDF or reading resource")

    def __str__(self):
        return f"{self.title} ({self.isbn})"

    @property
    def readable_source(self) -> str | None:
        if self.content_file:
            return self.content_file.url
        if self.content_url:
            # If it's an image, it's NOT a readable book source
            if any(x in self.content_url.lower() for x in ['.jpg', '.jpeg', '.png', '.webp']):
                return None
            return self.content_url
        return None

    @property
    def get_thumbnail(self) -> str:
        if self.thumbnail:
            return self.thumbnail.url
        if self.thumbnail_url:
            return self.thumbnail_url
        # Legacy fallback
        if self.content_url and any(x in self.content_url.lower() for x in ['.jpg', '.jpeg', '.png', '.webp']):
            return self.content_url
        return f"https://via.placeholder.com/300x400?text={self.title.replace(' ', '+')}"


class Transaction(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'requested', 'Requested'
        ISSUED = 'issued', 'Issued'
        RETURN_REQUESTED = 'return_requested', 'Return Requested'
        RETURNED = 'returned', 'Returned'
        OVERDUE = 'overdue', 'Overdue'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='transactions')
    issue_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    fine = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_fine(self) -> int:
        daily_fine = getattr(settings, 'DAILY_FINE_INR', 10)
        if self.due_date and not self.return_date:
            overdue_days = (timezone.localdate() - self.due_date).days
        elif self.due_date and self.return_date:
            overdue_days = (self.return_date - self.due_date).days
        else:
            overdue_days = 0
        overdue_days = max(0, overdue_days)
        return overdue_days * daily_fine

    def mark_issued(self):
        if self.book.available_copies > 0:
            self.status = Transaction.Status.ISSUED
            self.issue_date = timezone.localdate()
            loan_days = getattr(settings, 'LOAN_DAYS', 14)
            self.due_date = self.issue_date + timezone.timedelta(days=loan_days)
            self.book.available_copies -= 1
            self.book.save()
            self.save()

    def mark_returned(self):
        self.return_date = timezone.localdate()
        self.fine = self.calculate_fine()
        self.status = Transaction.Status.RETURNED
        self.book.available_copies += 1
        self.book.save()
        self.save()

    def mark_cancelled(self):
        self.status = Transaction.Status.CANCELLED
        self.save()

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"

class FeedbackMessage(models.Model):
    rating = models.CharField(max_length=50)
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} - Feedback"