"""
Serviço central de permissões do PortalK12.

Hoje este serviço usa regras fixas baseadas no papel do usuário.
No futuro, a função can() deverá considerar:
- papel base do usuário;
- grupos de acesso configuráveis por escola;
- permissões individuais;
- bloqueios individuais;
- escopo por escola;
- auditoria de mudanças de permissão.
"""

from __future__ import annotations

from typing import Any

from apps.accounts import permission_codes as codes
from apps.accounts.permissions import (
    is_collaborator,
    is_school_director,
    is_system_admin,
    is_teacher,
)


DIRECTOR_PERMISSIONS = {
    codes.STUDENTS_VIEW,
    codes.STUDENTS_CREATE,
    codes.STUDENTS_UPDATE,
    codes.STUDENTS_DELETE,
    codes.STUDENTS_MANAGE,
    codes.GUARDIANS_VIEW,
    codes.GUARDIANS_CREATE,
    codes.GUARDIANS_UPDATE,
    codes.GUARDIANS_DELETE,
    codes.GUARDIANS_MANAGE,
    codes.TEACHERS_VIEW,
    codes.TEACHERS_CREATE,
    codes.TEACHERS_UPDATE,
    codes.TEACHERS_DELETE,
    codes.TEACHERS_MANAGE,
    codes.CLASSES_VIEW,
    codes.CLASSES_CREATE,
    codes.CLASSES_UPDATE,
    codes.CLASSES_DELETE,
    codes.CLASSES_MANAGE,
    codes.COLLABORATORS_VIEW,
    codes.COLLABORATORS_CREATE,
    codes.COLLABORATORS_UPDATE,
    codes.COLLABORATORS_DELETE,
    codes.COLLABORATORS_MANAGE,
    codes.VISITORS_VIEW,
    codes.VISITORS_CREATE,
    codes.VISITORS_UPDATE,
    codes.VISITORS_DELETE,
    codes.VISITORS_MANAGE,
    codes.CANTINA_VIEW,
    codes.CANTINA_PRODUCTS_MANAGE,
    codes.CANTINA_ORDERS_VIEW,
    codes.CANTINA_ORDERS_MANAGE,
    codes.CANTINA_MANAGE,
    codes.FILES_VIEW,
    codes.FILES_UPLOAD,
    codes.FILES_DELETE,
    codes.FILES_MANAGE,
    codes.MESSAGES_VIEW,
    codes.MESSAGES_SEND,
    codes.MESSAGES_READ_RECEIPTS_VIEW,
    codes.MESSAGES_MANAGE,
    codes.SCHOOL_VIEW,
    codes.SCHOOL_SETTINGS_UPDATE,
    codes.SCHOOL_USERS_MANAGE,
    codes.SCHOOL_PERMISSIONS_MANAGE,
    codes.SCHOOL_ADMIN_GRANT,
    codes.AUDITLOG_VIEW,
}

TEACHER_PERMISSIONS = {
    codes.STUDENTS_VIEW,
    codes.TEACHERS_VIEW,
    codes.CLASSES_VIEW,
    codes.VISITORS_VIEW,
    codes.VISITORS_CREATE,
    codes.VISITORS_MANAGE,
    codes.CANTINA_VIEW,
    codes.FILES_VIEW,
    codes.MESSAGES_VIEW,
    codes.MESSAGES_SEND,
}

COLLABORATOR_PERMISSIONS = {
    codes.CANTINA_VIEW,
}


def can(user: Any, permission_code: str) -> bool:
    """
    Verifica se o usuário possui uma permissão.

    Importante:
    - Superuser/staff/admin global passa em tudo.
    - Diretor da escola possui permissões administrativas da escola.
    - Professor e colaborador seguem escopo inicial do MVP.
    - No futuro, esta função consultará permissões configuráveis no banco.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return False

    if is_system_admin(user):
        return True

    if is_school_director(user):
        return permission_code in DIRECTOR_PERMISSIONS

    if is_teacher(user):
        return permission_code in TEACHER_PERMISSIONS

    if is_collaborator(user):
        return permission_code in COLLABORATOR_PERMISSIONS

    return False


def can_any(user: Any, permission_codes: list[str] | tuple[str, ...] | set[str]) -> bool:
    return any(can(user, permission_code) for permission_code in permission_codes)


def can_all(user: Any, permission_codes: list[str] | tuple[str, ...] | set[str]) -> bool:
    return all(can(user, permission_code) for permission_code in permission_codes)
