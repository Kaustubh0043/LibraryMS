from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_create, name='book_create'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('read/<int:pk>/', views.book_read, name='book_read'),
    path('books/<int:pk>/read/', views.book_read), # Legacy compatibility
    path('books/<int:pk>/edit/', views.book_update, name='book_update'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('issue/<int:book_id>/', views.request_issue, name='request_issue'),
    path('return/<int:txn_id>/', views.request_return, name='request_return'),
    path('admin/requests/', views.admin_requests, name='admin_requests'),
    path('admin/transactions/', views.admin_transactions, name='admin_transactions'),
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('payment/create/<int:txn_id>/', views.create_razorpay_order, name='create_payment'),
    path('payment/callback/', views.razorpay_callback, name='razorpay_callback'),
    path('activate/<str:uidb64>/<str:token>/', views.activate_account, name='activate_account'),
    path('resend-activation/', views.resend_activation, name='resend_activation'),
]