from __future__ import annotations

from typing import Any

from apps.accounts import permission_codes as codes
from apps.accounts.models import UserRole


def get_user_profile(user: Any):
    if not user or not getattr(user, "is_authenticated", False):
        return None

    return getattr(user, "profile", None)


def is_system_admin(user: Any) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False

    profile = get_user_profile(user)

    return bool(
        getattr(user, "is_superuser", False)
        or getattr(user, "is_staff", False)
        or (
            profile
            and profile.is_active_profile
            and profile.role == UserRole.SYSTEM_ADMIN
        )
    )


def is_school_director(user: Any) -> bool:
    profile = get_user_profile(user)

    if is_system_admin(user):
        return True

    return bool(
        profile
        and profile.is_active_profile
        and profile.role == UserRole.SCHOOL_DIRECTOR
    )


def is_teacher(user: Any) -> bool:
    profile = get_user_profile(user)

    return bool(
        profile
        and profile.is_active_profile
        and profile.role == UserRole.TEACHER
    )


def is_collaborator(user: Any) -> bool:
    profile = get_user_profile(user)

    return bool(
        profile
        and profile.is_active_profile
        and profile.role == UserRole.COLLABORATOR
    )


def is_guardian(user: Any) -> bool:
    profile = get_user_profile(user)

    return bool(
        profile
        and profile.is_active_profile
        and profile.role == UserRole.GUARDIAN
    )


def is_student(user: Any) -> bool:
    profile = get_user_profile(user)

    return bool(
        profile
        and profile.is_active_profile
        and profile.role == UserRole.STUDENT
    )


def has_permission(user: Any, permission_code: str) -> bool:
    """
    Ponto público para checar permissões por código.

    Mantemos o import local para evitar dependência circular:
    - permission_service precisa das funções is_* deste arquivo;
    - este arquivo precisa chamar permission_service.can().
    """
    from apps.accounts.services.permission_service import can

    return can(user, permission_code)


def can_view_students(user: Any) -> bool:
    return has_permission(user, codes.STUDENTS_VIEW)


def can_manage_students(user: Any) -> bool:
    return has_permission(user, codes.STUDENTS_MANAGE)


def can_view_teachers(user: Any) -> bool:
    return has_permission(user, codes.TEACHERS_VIEW)


def can_manage_teachers(user: Any) -> bool:
    return has_permission(user, codes.TEACHERS_MANAGE)


def can_view_classes(user: Any) -> bool:
    return has_permission(user, codes.CLASSES_VIEW)


def can_manage_classes(user: Any) -> bool:
    return has_permission(user, codes.CLASSES_MANAGE)


def can_view_collaborators(user: Any) -> bool:
    return has_permission(user, codes.COLLABORATORS_VIEW)


def can_manage_collaborators(user: Any) -> bool:
    return has_permission(user, codes.COLLABORATORS_MANAGE)


def can_view_visitors(user: Any) -> bool:
    return has_permission(user, codes.VISITORS_VIEW)


def can_manage_visitors(user: Any) -> bool:
    return has_permission(user, codes.VISITORS_MANAGE)


def can_view_cantina(user: Any) -> bool:
    return has_permission(user, codes.CANTINA_VIEW)


def can_manage_cantina(user: Any) -> bool:
    return has_permission(user, codes.CANTINA_MANAGE)


def can_view_file_manager(user: Any) -> bool:
    return has_permission(user, codes.FILES_VIEW)


def can_manage_file_manager(user: Any) -> bool:
    return has_permission(user, codes.FILES_MANAGE)


def can_view_messages(user: Any) -> bool:
    return has_permission(user, codes.MESSAGES_VIEW)


def can_send_messages(user: Any) -> bool:
    return has_permission(user, codes.MESSAGES_SEND)


def can_manage_school_permissions(user: Any) -> bool:
    return has_permission(user, codes.SCHOOL_PERMISSIONS_MANAGE)


def can_grant_school_admin(user: Any) -> bool:
    return has_permission(user, codes.SCHOOL_ADMIN_GRANT)


def can_view_auditlog(user: Any) -> bool:
    return has_permission(user, codes.AUDITLOG_VIEW)
