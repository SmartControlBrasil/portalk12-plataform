from django.urls import path

from . import views

app_name = "admin_k12"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("pages/<slug:page>/", views.admin_page, name="admin_page"),
]
