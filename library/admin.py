from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Book, Transaction


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")} ),
        ("Library profile", {"fields": ("role", "department", "year", "semester")} ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    list_display = ("username", "email", "role", "department", "year", "semester", "is_staff")
    list_filter = ("role", "department", "is_staff", "is_superuser", "is_active", "groups")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "department", "year", "semester", "isbn", "available_copies")
    search_fields = ("title", "author", "isbn")
    list_filter = ("department", "year", "semester")
    fieldsets = (
        (None, {"fields": ("title", "author", "isbn")} ),
        ("Classification", {"fields": ("department", "year", "semester")} ),
        ("Availability", {"fields": ("available_copies",)} ),
        ("Media", {"fields": ("thumbnail", "thumbnail_url", "content_file", "content_url")} ),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "status", "issue_date", "due_date", "return_date", "fine")
    list_filter = ("status", "issue_date", "due_date")
    search_fields = ("user__username", "book__title", "book__isbn")

from .models import ContactMessage, FeedbackMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email', 'message')

@admin.register(FeedbackMessage)
class FeedbackMessageAdmin(admin.ModelAdmin):
    list_display = ('rating', 'created_at')
    list_filter = ('rating',)
