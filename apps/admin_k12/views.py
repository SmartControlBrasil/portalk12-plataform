from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render

from apps.accounts.permissions import (
    can_manage_classes,
    can_manage_collaborators,
    can_manage_students,
    can_manage_teachers,
    can_manage_visitors,
    can_view_cantina,
    can_view_classes,
    can_view_collaborators,
    can_view_file_manager,
    can_view_students,
    can_view_teachers,
    can_view_visitors,
)


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

    "collaborators": "collaborators.html",
    "collaborator": "collaborators.html",

    "visitors": "visitors.html",
    "visitor": "visitors.html",

    "file-manager": "file-manager.html",

    "cantina": "cantina.html",
    "cantina-detail": "cantina-detail.html",

    "calendar": "calendar.html",
    "profile": "profile.html",
    "profile-edit": "profile-edit.html",

    "chat": "chat.html",
    "messages": "messages.html",
    "message-detail": "message-detail.html",
    "message-compose": "message-compose.html",
}


PAGE_ACCESS_RULES = {
    # Alunos
    "students": can_view_students,
    "student": can_view_students,
    "student-detail": can_view_students,
    "student-form": can_manage_students,
    "add-student": can_manage_students,

    # Professores
    "teachers": can_view_teachers,
    "teacher": can_view_teachers,
    "teacher-detail": can_view_teachers,
    "teacher-form": can_manage_teachers,
    "add-teacher": can_manage_teachers,

    # Turmas
    "classes": can_view_classes,
    "class": can_view_classes,

    # Colaboradores
    "collaborators": can_view_collaborators,
    "collaborator": can_view_collaborators,

    # Visitantes
    "visitors": can_view_visitors,
    "visitor": can_manage_visitors,

    # Arquivos
    "file-manager": can_view_file_manager,

    # Cantina
    "cantina": can_view_cantina,
    "cantina-detail": can_view_cantina,
}


@login_required
def dashboard(request):
    return render(request, "admin-k12/pages/dashboard.html")


@login_required
def admin_page(request, page):
    template_name = ALLOWED_ADMIN_PAGES.get(page)

    if not template_name:
        raise Http404("Página administrativa não encontrada.")

    access_rule = PAGE_ACCESS_RULES.get(page)

    if access_rule and not access_rule(request.user):
        raise PermissionDenied("Você não tem permissão para acessar esta página.")

    return render(request, f"admin-k12/pages/{template_name}")