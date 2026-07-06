from __future__ import annotations

from typing import Any

from django.http import HttpRequest

from apps.auditlog.models import AuditAction, AuditLog


def get_client_ip(request: HttpRequest | None) -> str | None:
    if request is None:
        return None

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def get_user_agent(request: HttpRequest | None) -> str:
    if request is None:
        return ""

    return request.META.get("HTTP_USER_AGENT", "")


def get_actor_role(user: Any) -> str:
    profile = getattr(user, "profile", None)

    if profile and getattr(profile, "role", None):
        return str(profile.role)

    if getattr(user, "is_superuser", False):
        return "superuser"

    if getattr(user, "is_staff", False):
        return "staff"

    return ""


def get_actor_school(user: Any):
    profile = getattr(user, "profile", None)

    if profile and getattr(profile, "school", None):
        return profile.school

    return None


def record_audit_event(
    *,
    request: HttpRequest | None = None,
    actor_user: Any = None,
    school: Any = None,
    action: str = AuditAction.OTHER,
    module: str = "",
    obj: Any = None,
    object_type: str = "",
    object_id: str = "",
    object_repr: str = "",
    changes_before: dict | None = None,
    changes_after: dict | None = None,
    metadata: dict | None = None,
) -> AuditLog:
    """
    Registra um evento de auditoria.

    Uso recomendado:
        record_audit_event(
            request=request,
            action=AuditAction.UPDATED,
            module="students",
            obj=student,
            changes_before={...},
            changes_after={...},
        )
    """
    if actor_user is None and request is not None:
        actor_user = getattr(request, "user", None)

    if actor_user is not None and not getattr(actor_user, "is_authenticated", False):
        actor_user = None

    if school is None and actor_user is not None:
        school = get_actor_school(actor_user)

    if obj is not None:
        object_type = object_type or obj.__class__.__name__
        object_id = object_id or str(getattr(obj, "pk", ""))
        object_repr = object_repr or str(obj)

        if school is None and getattr(obj, "school", None):
            school = obj.school

    return AuditLog.objects.create(
        school=school,
        actor_user=actor_user,
        actor_role=get_actor_role(actor_user) if actor_user else "",
        action=action,
        module=module,
        object_type=object_type,
        object_id=object_id,
        object_repr=object_repr,
        changes_before=changes_before or {},
        changes_after=changes_after or {},
        metadata=metadata or {},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
