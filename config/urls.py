from django.contrib import admin
from django.urls import path
from students import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("predictions/", views.predict_all, name="predictions"),
    path("add/", views.add_record, name="add_record"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('export/', views.export_csv, name='export_csv'),
]