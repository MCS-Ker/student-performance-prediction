from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from students import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # صفحات المصادقة
    path('login/', auth_views.LoginView.as_view(
        template_name='students/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # صفحات النظام
    path('dashboard/', views.dashboard, name='dashboard'),
    path('predictions/', views.predict_all, name='predictions'),
    path('add/', views.add_record, name='add_record'),
    path('export/', views.export_csv, name='export_csv'),
]