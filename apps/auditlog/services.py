from __future__ import annotations

from decimal import Decimal
from typing import Any, Iterable

from django.db import models
from django.http import HttpRequest
from django.utils import timezone

from apps.auditlog.models import AuditAction, AuditLog


SENSITIVE_FIELD_NAMES = {
    "password",
    "senha",
    "token",
    "secret",
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
}


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


def serialize_value(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Decimal):
        return str(value)

    if hasattr(value, "isoformat"):
        return value.isoformat()

    if isinstance(value, models.Model):
        return {
            "id": value.pk,
            "repr": str(value),
        }

    return str(value)


def should_mask_field(field_name: str) -> bool:
    normalized = field_name.lower()

    return any(sensitive in normalized for sensitive in SENSITIVE_FIELD_NAMES)


def model_snapshot(
    obj: models.Model,
    *,
    include_fields: Iterable[str] | None = None,
    exclude_fields: Iterable[str] | None = None,
) -> dict:
    """
    Gera snapshot simples de campos concretos do model.

    Não inclui relações many-to-many.
    Mascara campos sensíveis por nome.
    """
    include = set(include_fields or [])
    exclude = set(exclude_fields or [])

    data = {}

    for field in obj._meta.fields:
        field_name = field.name

        if include and field_name not in include:
            continue

        if field_name in exclude:
            continue

        if should_mask_field(field_name):
            data[field_name] = "***"
            continue

        value = getattr(obj, field_name, None)

        if isinstance(field, models.ForeignKey):
            data[field_name] = getattr(value, "pk", None)
        else:
            data[field_name] = serialize_value(value)

    return data


def diff_snapshots(before: dict, after: dict) -> dict:
    fields = set(before.keys()) | set(after.keys())

    return {
        field: {
            "before": before.get(field),
            "after": after.get(field),
        }
        for field in sorted(fields)
        if before.get(field) != after.get(field)
    }


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


def audit_created(
    *,
    obj: models.Model,
    module: str,
    request: HttpRequest | None = None,
    actor_user: Any = None,
    school: Any = None,
    include_fields: Iterable[str] | None = None,
    exclude_fields: Iterable[str] | None = None,
    metadata: dict | None = None,
) -> AuditLog:
    after = model_snapshot(
        obj,
        include_fields=include_fields,
        exclude_fields=exclude_fields,
    )

    return record_audit_event(
        request=request,
        actor_user=actor_user,
        school=school,
        action=AuditAction.CREATED,
        module=module,
        obj=obj,
        changes_before={},
        changes_after=after,
        metadata={
            "event": f"{module}.created",
            **(metadata or {}),
        },
    )


def audit_updated(
    *,
    obj: models.Model,
    module: str,
    before: dict,
    request: HttpRequest | None = None,
    actor_user: Any = None,
    school: Any = None,
    include_fields: Iterable[str] | None = None,
    exclude_fields: Iterable[str] | None = None,
    metadata: dict | None = None,
) -> AuditLog | None:
    after = model_snapshot(
        obj,
        include_fields=include_fields,
        exclude_fields=exclude_fields,
    )
    changes = diff_snapshots(before, after)

    if not changes:
        return None

    return record_audit_event(
        request=request,
        actor_user=actor_user,
        school=school,
        action=AuditAction.UPDATED,
        module=module,
        obj=obj,
        changes_before=before,
        changes_after=after,
        metadata={
            "event": f"{module}.updated",
            "changes": changes,
            **(metadata or {}),
        },
    )


def audit_deleted(
    *,
    obj: models.Model,
    module: str,
    before: dict | None = None,
    request: HttpRequest | None = None,
    actor_user: Any = None,
    school: Any = None,
    metadata: dict | None = None,
) -> AuditLog:
    before = before or model_snapshot(obj)

    return record_audit_event(
        request=request,
        actor_user=actor_user,
        school=school,
        action=AuditAction.DELETED,
        module=module,
        obj=obj,
        changes_before=before,
        changes_after={},
        metadata={
            "event": f"{module}.deleted",
            **(metadata or {}),
        },
    )


def audit_restored(
    *,
    obj: models.Model,
    module: str,
    before: dict,
    request: HttpRequest | None = None,
    actor_user: Any = None,
    school: Any = None,
    metadata: dict | None = None,
) -> AuditLog:
    after = model_snapshot(obj)

    return record_audit_event(
        request=request,
        actor_user=actor_user,
        school=school,
        action=AuditAction.RESTORED,
        module=module,
        obj=obj,
        changes_before=before,
        changes_after=after,
        metadata={
            "event": f"{module}.restored",
            **(metadata or {}),
        },
    )


def now_iso() -> str:
    return timezone.now().isoformat()
