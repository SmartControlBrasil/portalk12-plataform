from __future__ import annotations

from typing import Any

from apps.accounts.models import UserRole


def get_user_profile(user: Any):
    if not user or not getattr(user, "is_authenticated", False):
        return None

    return getattr(user, "profile", None)


def is_system_admin(user: Any) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False

    return bool(
        getattr(user, "is_superuser", False)
        or getattr(user, "is_staff", False)
        or (
            get_user_profile(user)
            and get_user_profile(user).role == UserRole.SYSTEM_ADMIN
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


def can_view_students(user: Any) -> bool:
    return is_system_admin(user) or is_school_director(user) or is_teacher(user)


def can_manage_students(user: Any) -> bool:
    return is_system_admin(user) or is_school_director(user)


def can_view_teachers(user: Any) -> bool:
    return is_system_admin(user) or is_school_director(user) or is_teacher(user)


def can_manage_teachers(user: Any) -> bool:
    return is_system_admin(user) or is_school_director(user)


def can_view_classes(user: Any) -> bool:
    return is_system_admin(user) or is_school_director(user) or is_teacher(user)


def can_manage_classes(user: Any) -> bool:
    return is_system_admin(user) or is_school_director(user)


def can_view_collaborators(user: Any) -> bool:
    return is_system_admin(user) or is_school_director(user)


def can_manage_collaborators(user: Any) -> bool:
    return is_system_admin(user) or is_school_director(user)


def can_view_visitors(user: Any) -> bool:
    return is_system_admin(user) or is_school_director(user) or is_teacher(user)


def can_manage_visitors(user: Any) -> bool:
    return is_system_admin(user) or is_school_director(user) or is_teacher(user)


def can_view_cantina(user: Any) -> bool:
    return (
        is_system_admin(user)
        or is_school_director(user)
        or is_teacher(user)
        or is_collaborator(user)
    )


def can_manage_cantina(user: Any) -> bool:
    return is_system_admin(user) or is_school_director(user)


def can_view_file_manager(user: Any) -> bool:
    return is_system_admin(user) or is_school_director(user) or is_teacher(user)


def can_manage_file_manager(user: Any) -> bool:
    return is_system_admin(user) or is_school_director(user)