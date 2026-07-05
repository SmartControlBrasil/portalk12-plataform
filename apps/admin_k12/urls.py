from django.urls import path

from . import views

app_name = "admin_k12"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("pages/<path:page>", views.akademi_page, name="akademi_page"),
]
