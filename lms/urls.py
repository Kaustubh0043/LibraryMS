from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from library import views as lib_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('allauth.urls')),
    path('', lib_views.home, name='home'),
    path('about/', lib_views.about, name='about'),
    path('contact/', lib_views.contact, name='contact'),
    path('feedback/', lib_views.feedback, name='feedback'),
    path('library/', include('library.urls')),
    path('activation-pending/', lib_views.activation_pending, name='activation_pending'),
    path('resend-activation/', lib_views.resend_activation, name='resend_activation'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)