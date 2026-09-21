from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from students import views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='dashboard'), name='home'),

    # صفحات المصادقة
    path('login/', auth_views.LoginView.as_view(
        template_name='students/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password/', auth_views.PasswordChangeView.as_view(template_name='students/password_change.html'), name='password_change'),
    path('password/done/', auth_views.PasswordChangeDoneView.as_view(template_name='students/password_change_done.html'), name='password_change_done'),

    # صفحات النظام
    path('dashboard/', views.dashboard, name='dashboard'),
    path('predictions/', views.predict_all, name='predictions'),
    path('add/', views.add_record, name='add_record'),
    path('export/', views.export_csv, name='export_csv'),
]