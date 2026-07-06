"""
Serviço central de permissões do PortalK12.

Modelo atual:
- Super Admin passa em tudo.
- Permissões individuais podem liberar ou bloquear.
- Grupos de acesso ativos podem liberar permissões.
- Papel base funciona como fallback do MVP.

Modelo futuro:
- grupos configuráveis por escola via tela;
- permissões por checkbox;
- auditoria de concessão/revogação;
- escopo refinado por escola, turma, aluno e vínculo familiar.
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


def get_user_school(user: Any):
    profile = getattr(user, "profile", None)

    if profile and getattr(profile, "school", None):
        return profile.school

    return None


def has_individual_block(user: Any, permission_code: str) -> bool:
    from apps.accounts.models import UserPermissionOverride

    school = get_user_school(user)

    if school is None:
        return False

    return UserPermissionOverride.objects.filter(
        user=user,
        school=school,
        permission_code=permission_code,
        allowed=False,
        is_active=True,
    ).exists()


def has_individual_allow(user: Any, permission_code: str) -> bool:
    from apps.accounts.models import UserPermissionOverride

    school = get_user_school(user)

    if school is None:
        return False

    return UserPermissionOverride.objects.filter(
        user=user,
        school=school,
        permission_code=permission_code,
        allowed=True,
        is_active=True,
    ).exists()


def has_group_allow(user: Any, permission_code: str) -> bool:
    from apps.accounts.models import AccessGroupPermission

    school = get_user_school(user)

    if school is None:
        return False

    return AccessGroupPermission.objects.filter(
        group__school=school,
        group__is_active=True,
        group__members__user=user,
        group__members__is_active=True,
        permission_code=permission_code,
        allowed=True,
    ).exists()


def has_base_role_permission(user: Any, permission_code: str) -> bool:
    if is_school_director(user):
        return permission_code in DIRECTOR_PERMISSIONS

    if is_teacher(user):
        return permission_code in TEACHER_PERMISSIONS

    if is_collaborator(user):
        return permission_code in COLLABORATOR_PERMISSIONS

    return False


def can(user: Any, permission_code: str) -> bool:
    """
    Verifica se o usuário possui uma permissão.

    Ordem:
    1. Super Admin PortalK12 passa em tudo.
    2. Bloqueio individual ativo nega.
    3. Permissão individual ativa libera.
    4. Grupo ativo com permissão libera.
    5. Papel base libera como fallback.
    6. Sem regra, nega.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return False

    if is_system_admin(user):
        return True

    if has_individual_block(user, permission_code):
        return False

    if has_individual_allow(user, permission_code):
        return True

    if has_group_allow(user, permission_code):
        return True

    return has_base_role_permission(user, permission_code)


def can_any(user: Any, permission_codes: list[str] | tuple[str, ...] | set[str]) -> bool:
    return any(can(user, permission_code) for permission_code in permission_codes)


def can_all(user: Any, permission_codes: list[str] | tuple[str, ...] | set[str]) -> bool:
    return all(can(user, permission_code) for permission_code in permission_codes)
