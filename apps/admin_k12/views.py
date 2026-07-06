from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render


ALLOWED_ADMIN_PAGES = {
    "students": "students.html",
    "student": "students.html",
    "student-detail": "student-detail.html",
    "student-form": "student-form.html",
    "add-student": "student-form.html",

    "teachers": "teachers.html",
    "teacher": "teachers.html",
    "teacher-detail": "teacher-detail.html",
    "teacher-form": "teacher-form.html",
    "add-teacher": "teacher-form.html",

    "classes": "classes.html",
    "class": "classes.html",

    "visitors": "visitors.html",
    "visitor": "visitors.html",

    "file-manager": "file-manager.html",

    "cantina": "cantina.html",
    "cantina-detail": "cantina-detail.html",

    # aliases temporários para não quebrar links antigos
    
    "cantina": "cantina.html",
    "cantina-detail": "cantina-detail.html",  # alias temporário para não quebrar links antigos                                                                                                                       

    "calendar": "calendar.html",
    "profile": "profile.html",
    "profile-edit": "profile-edit.html",

    "chat": "chat.html",
    "messages": "messages.html",
    "message-detail": "message-detail.html",
    "message-compose": "message-compose.html",
}


@login_required
def dashboard(request):
    return render(request, "admin-k12/pages/dashboard.html")


@login_required
def admin_page(request, page):
    template_name = ALLOWED_ADMIN_PAGES.get(page)

    if not template_name:
        raise Http404("Página administrativa não encontrada.")

    return render(request, f"admin-k12/pages/{template_name}")
