from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
import razorpay

from .forms import SignupForm, BookForm
from .models import Book, Transaction, User, ContactMessage, FeedbackMessage


def is_admin(user: User) -> bool:
    return user.is_staff or user.role == User.Roles.ADMIN


def home(request: HttpRequest) -> HttpResponse:
    featured_books = Book.objects.filter(
        Q(thumbnail__gt='') | 
        Q(content_url__icontains='.jpg') | 
        Q(content_url__icontains='.png') | 
        Q(content_url__icontains='m.media-amazon')
    ).distinct().order_by('?')[:4]
    return render(request, 'home.html', {'featured_books': featured_books})


def about(request: HttpRequest) -> HttpResponse:
    return render(request, 'about.html')

def contact(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        if name and email and message:
            ContactMessage.objects.create(name=name, email=email, message=message)
            messages.success(request, 'Thank you! Your message has been sent securely.')
        return redirect('contact')
    return render(request, 'contact.html')

def feedback(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        rating = request.POST.get('rating')
        feedback_text = request.POST.get('feedback_text')
        if rating and feedback_text:
            FeedbackMessage.objects.create(rating=rating, feedback_text=feedback_text)
            messages.success(request, 'Thank you for your valuable feedback!')
        return redirect('feedback')
    return render(request, 'feedback.html')


def signup_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.role == User.Roles.ADMIN:
                user.is_staff = True
            # Require email verification before login
            user.is_active = False
            user.save()

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_path = reverse('activate_account', args=[uidb64, token])
            activation_link = request.build_absolute_uri(activation_path)
            subject = 'Activate your LibraryMS account'
            message = (
                f'Hi {user.username},\n\n'
                f'Thanks for signing up at LibraryMS. Please activate your account by clicking the link below:\n'
                f'{activation_link}\n\n'
                f'If you did not sign up, you can ignore this email.'
            )
            send_mail(subject, message, None, [user.email], fail_silently=False)

            messages.success(request, 'Account created! Please check your email for the activation link.')
            return redirect('activation_pending')
    else:
        form = SignupForm()
    return render(request, 'auth/signup.html', {'form': form})

def activation_pending(request: HttpRequest) -> HttpResponse:
    return render(request, 'registration/activation_pending.html')


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    if is_admin(request.user):
        if request.method == 'POST':
            txn_id = request.POST.get('txn_id')
            action = request.POST.get('action')
            txn = get_object_or_404(Transaction, id=txn_id)
            if action == 'approve_issue':
                txn.mark_issued()
                messages.success(request, f"Request for '{txn.book.title}' by {txn.user.username} APPROVED.")
            elif action == 'approve_return':
                txn.mark_returned()
                messages.success(request, f"Return for '{txn.book.title}' by {txn.user.username} CONFIRMED.")
            elif action == 'reject_request':
                txn.mark_cancelled()
                messages.error(request, f"Request for '{txn.book.title}' by {txn.user.username} REJECTED/CANCELLED.")
            return redirect('dashboard')

        pending_requests = Transaction.objects.filter(status__in=[Transaction.Status.REQUESTED, Transaction.Status.RETURN_REQUESTED]).order_by('-created_at')
        latest_contacts = ContactMessage.objects.all().order_by('-created_at')[:5]
        latest_feedback = FeedbackMessage.objects.all().order_by('-created_at')[:5]
        context = {
            'pending_requests': pending_requests,
            'latest_contacts': latest_contacts,
            'latest_feedback': latest_feedback
        }
        return render(request, 'dashboard/admin_dashboard.html', context)
    else:
        if request.method == 'POST':
            txn_id = request.POST.get('txn_id')
            action = request.POST.get('action')
            txn = get_object_or_404(Transaction, id=txn_id, user=request.user)
            if action == 'cancel_request' and txn.status == Transaction.Status.REQUESTED:
                txn.mark_cancelled()
                messages.warning(request, "Request cancelled.")
            elif action == 'request_return' and txn.status == Transaction.Status.ISSUED:
                txn.status = Transaction.Status.RETURN_REQUESTED
                txn.save()
                messages.success(request, "Return requested. Please wait for admin approval.")
            return redirect('dashboard')

        txns = Transaction.objects.filter(user=request.user).exclude(status=Transaction.Status.CANCELLED).order_by('-created_at')
        return render(request, 'dashboard/student_dashboard.html', {'transactions': txns})

@login_required
@user_passes_test(is_admin)
def admin_user_list(request: HttpRequest) -> HttpResponse:
    users = User.objects.filter(role=User.Roles.STUDENT).order_by('username')
    return render(request, 'admin/user_list.html', {'students': users})

@login_required
@user_passes_test(is_admin)
def admin_user_detail(request: HttpRequest, user_id: int) -> HttpResponse:
    student = get_object_or_404(User, id=user_id)
    history = Transaction.objects.filter(user=student).order_by('-created_at')
    currently_issued = history.filter(status=Transaction.Status.ISSUED)
    return render(request, 'admin/user_detail.html', {
        'student': student,
        'history': history,
        'currently_issued': currently_issued
    })

@login_required
@user_passes_test(is_admin)
def admin_transactions(request: HttpRequest) -> HttpResponse:
    all_txns = Transaction.objects.all().order_by('-created_at')
    return render(request, 'admin/all_transactions.html', {'transactions': all_txns})

@login_required
def book_list(request: HttpRequest) -> HttpResponse:
    query = request.GET.get('q', '')
    department = request.GET.get('department', '')
    year = request.GET.get('year', '')
    semester = request.GET.get('semester', '')

    books = Book.objects.all().order_by('title')
    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))
    if department:
        books = books.filter(department=department)
    if year:
        books = books.filter(year=year)
    if semester:
        books = books.filter(semester=semester)

    context = {
        'books': books,
        'query': query,
        'department': department,
        'year': year,
        'semester': semester,
    }
    return render(request, 'books/book_list.html', context)


@login_required
@user_passes_test(is_admin)
def book_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book added')
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form})


@login_required
def book_detail(request: HttpRequest, pk: int) -> HttpResponse:
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books/book_detail.html', {'book': book})


@login_required
@user_passes_test(is_admin)
def book_update(request: HttpRequest, pk: int) -> HttpResponse:
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated')
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form, 'book': book})


@login_required
@user_passes_test(is_admin)
def book_delete(request: HttpRequest, pk: int) -> HttpResponse:
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted')
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})


@login_required
def request_issue(request: HttpRequest, book_id: int) -> HttpResponse:
    book = get_object_or_404(Book, id=book_id)
    txn = Transaction.objects.create(user=request.user, book=book, status=Transaction.Status.REQUESTED)
    messages.info(request, 'Issue request submitted')
    return redirect('dashboard')


@login_required
def request_return(request: HttpRequest, txn_id: int) -> HttpResponse:
    txn = get_object_or_404(Transaction, id=txn_id, user=request.user)
    if txn.status == Transaction.Status.ISSUED:
        txn.status = Transaction.Status.RETURN_REQUESTED
        txn.save()
        messages.info(request, 'Return request submitted')
    return redirect('dashboard')


@login_required
@user_passes_test(is_admin)
def admin_requests(request: HttpRequest) -> HttpResponse:
    post_triggered = False
    if request.method == 'POST':
        post_triggered = True
        print('POST data:', request.POST)
        action = request.POST.get('action')
        txn_id = request.POST.get('txn_id')
        print('Action:', action, 'Txn ID:', txn_id)
        txn = get_object_or_404(Transaction, id=txn_id)
        print('Fetched txn:', txn, 'Status:', txn.status)
        if action == 'approve_issue' and txn.status == Transaction.Status.REQUESTED:
            if txn.book.available_copies > 0:
                txn.book.available_copies -= 1
                txn.book.save()
                txn.mark_issued()
                print('Transaction marked as issued.')
                messages.success(request, 'Issue approved')
            else:
                print('No copies available.')
                messages.error(request, 'No copies available')
        elif action == 'approve_return' and txn.status == Transaction.Status.RETURN_REQUESTED:
            txn.mark_returned()
            txn.book.available_copies += 1
            txn.book.save()
            print('Transaction marked as returned.')
            messages.success(request, 'Return approved')
        else:
            print('Invalid action or status.')
            messages.error(request, 'Invalid action')
    pending = Transaction.objects.filter(status__in=[Transaction.Status.REQUESTED, Transaction.Status.RETURN_REQUESTED])
    return render(request, 'dashboard/admin_requests.html', {'pending': pending, 'post_triggered': post_triggered})


@login_required
@user_passes_test(is_admin)
def admin_transactions(request: HttpRequest) -> HttpResponse:
    txns = Transaction.objects.all().order_by('-created_at')
    return render(request, 'dashboard/admin_transactions.html', {'transactions': txns})


@login_required
def book_read(request: HttpRequest, pk: int) -> HttpResponse:
    book = get_object_or_404(Book, pk=pk)
    source = book.readable_source
    if not source:
        messages.error(request, 'No readable content available for this book yet.')
        return redirect('book_detail', pk=book.pk)
    # Check if user has an approved transaction for this book
    has_access = Transaction.objects.filter(user=request.user, book=book, status=Transaction.Status.ISSUED).exists()
    preview_source = book.preview_source if hasattr(book, 'preview_source') and book.preview_source else source
    return render(request, 'books/book_read.html', {'book': book, 'source': source, 'has_access': has_access, 'preview_source': preview_source})


def activate_account(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    from django.utils.http import urlsafe_base64_decode
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated. You can log in now.')
        return redirect('login')
    return render(request, 'registration/activation_invalid.html')


def resend_activation(request: HttpRequest) -> HttpResponse:
    if request.method != 'POST':
        return redirect('login')

    identifier = request.POST.get('identifier', '').strip()
    user: User | None = None
    if identifier:
        try:
            user = User.objects.get(email__iexact=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username__iexact=identifier)
            except User.DoesNotExist:
                user = None

    if not user:
        messages.error(request, 'No account found with that email/username.')
        return redirect('login')

    if user.is_active:
        messages.info(request, 'This account is already active. You can log in.')
        return redirect('login')

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_path = reverse('activate_account', args=[uidb64, token])
    activation_link = request.build_absolute_uri(activation_path)
    subject = 'Activate your LibraryMS account'
    message = (
        f'Hi {user.username},\n\n'
        f'Click the link below to activate your account:\n{activation_link}\n\n'
        f'If you did not sign up, you can ignore this email.'
    )
    send_mail(subject, message, None, [user.email], fail_silently=True)
    messages.success(request, 'Activation email sent. Please check your inbox.')
    return redirect('activation_pending')


@login_required
def create_razorpay_order(request: HttpRequest, txn_id: int) -> HttpResponse:
    txn = get_object_or_404(Transaction, id=txn_id, user=request.user)
    if txn.fine <= 0:
        txn.fine = txn.calculate_fine()
        txn.save()
    if txn.fine <= 0:
        messages.info(request, 'No fine due.')
        return redirect('dashboard')

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    order_data = {
        'amount': txn.fine * 100,
        'currency': 'INR',
        'payment_capture': 1,
        'notes': {'txn_id': str(txn.id), 'user': request.user.username},
    }
    order = client.order.create(order_data)
    context = {
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order': order,
        'txn': txn,
    }
    return render(request, 'payments/razorpay_checkout.html', context)


@csrf_exempt
def razorpay_callback(request: HttpRequest) -> HttpResponse:
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')

    payload = request.POST
    order_id = payload.get('razorpay_order_id')
    payment_id = payload.get('razorpay_payment_id')
    signature = payload.get('razorpay_signature')
    txn_id = request.GET.get('txn_id') or payload.get('notes[txn_id]')

    if not (order_id and payment_id and signature and txn_id):
        return HttpResponseBadRequest('Missing parameters')

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        })
    except razorpay.errors.SignatureVerificationError:
        return HttpResponseBadRequest('Signature verification failed')

    txn = get_object_or_404(Transaction, id=int(txn_id))
    txn.fine = 0
    txn.save()
    return redirect('dashboard')


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '').strip()
        user = None
        if identifier and password:
            # 1. Try directly (Username)
            user = authenticate(request, username=identifier, password=password)
            
            if not user:
                # 2. Try as Email
                try:
                    user_obj = User.objects.filter(email__iexact=identifier).first()
                    if user_obj:
                        user = authenticate(request, username=user_obj.username, password=password)
                except Exception:
                    pass

            if not user:
                # 3. Try as Mobile
                try:
                    user_obj = User.objects.get(mobile_number=identifier)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
        if user:
            if user.is_active:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Account not activated. Check your email for activation link.')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    return render(request, 'registration/login.html')