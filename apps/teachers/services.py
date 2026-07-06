from __future__ import annotations

from typing import Any

from django.db import transaction
from django.http import HttpRequest
from django.utils import timezone

from apps.accounts import permission_codes as codes
from apps.auditlog.models import AuditAction
from apps.auditlog.services import (
    audit_created,
    audit_deleted,
    audit_restored,
    audit_updated,
    model_snapshot,
    record_audit_event,
)
from apps.teachers.models import Teacher


TEACHER_AUDIT_MODULE = "teachers"


def get_actor_from_request(request: HttpRequest | None):
    if request is None:
        return None

    user = getattr(request, "user", None)

    if user and getattr(user, "is_authenticated", False):
        return user

    return None


@transaction.atomic
def create_teacher(
    *,
    data: dict[str, Any],
    actor_user=None,
    request: HttpRequest | None = None,
    metadata: dict | None = None,
) -> Teacher:
    actor_user = actor_user or get_actor_from_request(request)

    teacher = Teacher.objects.create(**data)

    audit_created(
        obj=teacher,
        module=TEACHER_AUDIT_MODULE,
        request=request,
        actor_user=actor_user,
        metadata={
            "permission_code": codes.TEACHERS_CREATE,
            "event": "teacher_created",
            **(metadata or {}),
        },
    )

    return teacher


@transaction.atomic
def update_teacher(
    *,
    teacher: Teacher,
    data: dict[str, Any],
    actor_user=None,
    request: HttpRequest | None = None,
    metadata: dict | None = None,
) -> Teacher:
    actor_user = actor_user or get_actor_from_request(request)

    before = model_snapshot(teacher)
    changed_fields = []

    for field_name, value in data.items():
        if not hasattr(teacher, field_name):
            continue

        current_value = getattr(teacher, field_name)

        if current_value != value:
            setattr(teacher, field_name, value)
            changed_fields.append(field_name)

    if changed_fields:
        teacher.save(update_fields=changed_fields)

        audit_updated(
            obj=teacher,
            module=TEACHER_AUDIT_MODULE,
            before=before,
            request=request,
            actor_user=actor_user,
            metadata={
                "permission_code": codes.TEACHERS_UPDATE,
                "event": "teacher_updated",
                "changed_fields": changed_fields,
                **(metadata or {}),
            },
        )

    return teacher


@transaction.atomic
def soft_delete_teacher(
    *,
    teacher: Teacher,
    actor_user=None,
    request: HttpRequest | None = None,
    reason: str = "",
    metadata: dict | None = None,
) -> Teacher:
    actor_user = actor_user or get_actor_from_request(request)

    before = model_snapshot(teacher)
    update_fields = []

    if hasattr(teacher, "deleted_at"):
        teacher.deleted_at = timezone.now()
        update_fields.append("deleted_at")

    if hasattr(teacher, "deleted_by"):
        teacher.deleted_by = actor_user
        update_fields.append("deleted_by")

    if hasattr(teacher, "delete_reason"):
        teacher.delete_reason = reason
        update_fields.append("delete_reason")

    if hasattr(teacher, "is_active"):
        teacher.is_active = False
        update_fields.append("is_active")

    if hasattr(teacher, "status"):
        status_choices = getattr(teacher._meta.get_field("status"), "choices", []) or []
        valid_values = {value for value, _label in status_choices}

        if "inactive" in valid_values:
            teacher.status = "inactive"
            update_fields.append("status")
        elif "INACTIVE" in valid_values:
            teacher.status = "INACTIVE"
            update_fields.append("status")

    if update_fields:
        teacher.save(update_fields=list(dict.fromkeys(update_fields)))

    audit_deleted(
        obj=teacher,
        module=TEACHER_AUDIT_MODULE,
        before=before,
        request=request,
        actor_user=actor_user,
        metadata={
            "permission_code": codes.TEACHERS_DELETE,
            "event": "teacher_soft_deleted",
            "reason": reason,
            **(metadata or {}),
        },
    )

    return teacher


@transaction.atomic
def restore_teacher(
    *,
    teacher: Teacher,
    actor_user=None,
    request: HttpRequest | None = None,
    metadata: dict | None = None,
) -> Teacher:
    actor_user = actor_user or get_actor_from_request(request)

    before = model_snapshot(teacher)
    update_fields = []

    if hasattr(teacher, "deleted_at"):
        teacher.deleted_at = None
        update_fields.append("deleted_at")

    if hasattr(teacher, "deleted_by"):
        teacher.deleted_by = None
        update_fields.append("deleted_by")

    if hasattr(teacher, "delete_reason"):
        teacher.delete_reason = ""
        update_fields.append("delete_reason")

    if hasattr(teacher, "is_active"):
        teacher.is_active = True
        update_fields.append("is_active")

    if hasattr(teacher, "status"):
        status_choices = getattr(teacher._meta.get_field("status"), "choices", []) or []
        valid_values = {value for value, _label in status_choices}

        if "active" in valid_values:
            teacher.status = "active"
            update_fields.append("status")
        elif "ACTIVE" in valid_values:
            teacher.status = "ACTIVE"
            update_fields.append("status")

    if update_fields:
        teacher.save(update_fields=list(dict.fromkeys(update_fields)))

    audit_restored(
        obj=teacher,
        module=TEACHER_AUDIT_MODULE,
        before=before,
        request=request,
        actor_user=actor_user,
        metadata={
            "permission_code": codes.TEACHERS_UPDATE,
            "event": "teacher_restored",
            **(metadata or {}),
        },
    )

    return teacher


def record_teacher_viewed(
    *,
    teacher: Teacher,
    actor_user=None,
    request: HttpRequest | None = None,
    metadata: dict | None = None,
):
    actor_user = actor_user or get_actor_from_request(request)

    return record_audit_event(
        request=request,
        actor_user=actor_user,
        action=AuditAction.OTHER,
        module=TEACHER_AUDIT_MODULE,
        obj=teacher,
        metadata={
            "permission_code": codes.TEACHERS_VIEW,
            "event": "teacher_viewed",
            **(metadata or {}),
        },
    )
