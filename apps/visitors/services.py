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
from apps.visitors.models import Visitor


VISITOR_AUDIT_MODULE = "visitors"


def get_actor_from_request(request: HttpRequest | None):
    if request is None:
        return None

    user = getattr(request, "user", None)

    if user and getattr(user, "is_authenticated", False):
        return user

    return None


@transaction.atomic
def create_visitor(
    *,
    data: dict[str, Any],
    actor_user=None,
    request: HttpRequest | None = None,
    metadata: dict | None = None,
) -> Visitor:
    actor_user = actor_user or get_actor_from_request(request)

    visitor = Visitor.objects.create(**data)

    audit_created(
        obj=visitor,
        module=VISITOR_AUDIT_MODULE,
        request=request,
        actor_user=actor_user,
        metadata={
            "permission_code": codes.VISITORS_CREATE,
            "event": "visitor_created",
            **(metadata or {}),
        },
    )

    return visitor


@transaction.atomic
def update_visitor(
    *,
    visitor: Visitor,
    data: dict[str, Any],
    actor_user=None,
    request: HttpRequest | None = None,
    metadata: dict | None = None,
) -> Visitor:
    actor_user = actor_user or get_actor_from_request(request)

    before = model_snapshot(visitor)
    changed_fields = []

    for field_name, value in data.items():
        if not hasattr(visitor, field_name):
            continue

        current_value = getattr(visitor, field_name)

        if current_value != value:
            setattr(visitor, field_name, value)
            changed_fields.append(field_name)

    if changed_fields:
        visitor.save(update_fields=changed_fields)

        audit_updated(
            obj=visitor,
            module=VISITOR_AUDIT_MODULE,
            before=before,
            request=request,
            actor_user=actor_user,
            metadata={
                "permission_code": codes.VISITORS_UPDATE,
                "event": "visitor_updated",
                "changed_fields": changed_fields,
                **(metadata or {}),
            },
        )

    return visitor


@transaction.atomic
def soft_delete_visitor(
    *,
    visitor: Visitor,
    actor_user=None,
    request: HttpRequest | None = None,
    reason: str = "",
    metadata: dict | None = None,
) -> Visitor:
    actor_user = actor_user or get_actor_from_request(request)

    before = model_snapshot(visitor)
    update_fields = []

    if hasattr(visitor, "deleted_at"):
        visitor.deleted_at = timezone.now()
        update_fields.append("deleted_at")

    if hasattr(visitor, "deleted_by"):
        visitor.deleted_by = actor_user
        update_fields.append("deleted_by")

    if hasattr(visitor, "delete_reason"):
        visitor.delete_reason = reason
        update_fields.append("delete_reason")

    if hasattr(visitor, "is_active"):
        visitor.is_active = False
        update_fields.append("is_active")

    if hasattr(visitor, "status"):
        status_choices = getattr(visitor._meta.get_field("status"), "choices", []) or []
        valid_values = {value for value, _label in status_choices}

        if "inactive" in valid_values:
            visitor.status = "inactive"
            update_fields.append("status")
        elif "INACTIVE" in valid_values:
            visitor.status = "INACTIVE"
            update_fields.append("status")

    if update_fields:
        visitor.save(update_fields=list(dict.fromkeys(update_fields)))

    audit_deleted(
        obj=visitor,
        module=VISITOR_AUDIT_MODULE,
        before=before,
        request=request,
        actor_user=actor_user,
        metadata={
            "permission_code": codes.VISITORS_DELETE,
            "event": "visitor_soft_deleted",
            "reason": reason,
            **(metadata or {}),
        },
    )

    return visitor


@transaction.atomic
def restore_visitor(
    *,
    visitor: Visitor,
    actor_user=None,
    request: HttpRequest | None = None,
    metadata: dict | None = None,
) -> Visitor:
    actor_user = actor_user or get_actor_from_request(request)

    before = model_snapshot(visitor)
    update_fields = []

    if hasattr(visitor, "deleted_at"):
        visitor.deleted_at = None
        update_fields.append("deleted_at")

    if hasattr(visitor, "deleted_by"):
        visitor.deleted_by = None
        update_fields.append("deleted_by")

    if hasattr(visitor, "delete_reason"):
        visitor.delete_reason = ""
        update_fields.append("delete_reason")

    if hasattr(visitor, "is_active"):
        visitor.is_active = True
        update_fields.append("is_active")

    if hasattr(visitor, "status"):
        status_choices = getattr(visitor._meta.get_field("status"), "choices", []) or []
        valid_values = {value for value, _label in status_choices}

        if "active" in valid_values:
            visitor.status = "active"
            update_fields.append("status")
        elif "ACTIVE" in valid_values:
            visitor.status = "ACTIVE"
            update_fields.append("status")

    if update_fields:
        visitor.save(update_fields=list(dict.fromkeys(update_fields)))

    audit_restored(
        obj=visitor,
        module=VISITOR_AUDIT_MODULE,
        before=before,
        request=request,
        actor_user=actor_user,
        metadata={
            "permission_code": codes.VISITORS_UPDATE,
            "event": "visitor_restored",
            **(metadata or {}),
        },
    )

    return visitor


def record_visitor_viewed(
    *,
    visitor: Visitor,
    actor_user=None,
    request: HttpRequest | None = None,
    metadata: dict | None = None,
):
    actor_user = actor_user or get_actor_from_request(request)

    return record_audit_event(
        request=request,
        actor_user=actor_user,
        action=AuditAction.OTHER,
        module=VISITOR_AUDIT_MODULE,
        obj=visitor,
        metadata={
            "permission_code": codes.VISITORS_VIEW,
            "event": "visitor_viewed",
            **(metadata or {}),
        },
    )
