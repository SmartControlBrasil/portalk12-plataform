from __future__ import annotations

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.auditlog.models import AuditAction
from apps.auditlog.services import record_audit_event
from apps.accounts.models import (
    AccessGroup,
    AccessGroupPermission,
    UserAccessGroup,
    UserPermissionOverride,
)


AUDITED_FIELDS = {
    AccessGroup: [
        "name",
        "description",
        "is_system_default",
        "is_active",
    ],
    AccessGroupPermission: [
        "permission_code",
        "allowed",
    ],
    UserAccessGroup: [
        "is_active",
    ],
    UserPermissionOverride: [
        "permission_code",
        "allowed",
        "reason",
        "is_active",
    ],
}


def snapshot(instance):
    fields = AUDITED_FIELDS.get(instance.__class__, [])
    return {field: getattr(instance, field, None) for field in fields}


def changed_values(before: dict, after: dict):
    return {
        field: {
            "before": before.get(field),
            "after": after.get(field),
        }
        for field in after
        if before.get(field) != after.get(field)
    }


def actor_for(instance):
    if isinstance(instance, AccessGroup):
        return instance.created_by

    if isinstance(instance, AccessGroupPermission):
        return instance.group.created_by

    if isinstance(instance, UserAccessGroup):
        return instance.assigned_by

    if isinstance(instance, UserPermissionOverride):
        return instance.assigned_by

    return None


def school_for(instance):
    if isinstance(instance, AccessGroup):
        return instance.school

    if isinstance(instance, AccessGroupPermission):
        return instance.group.school

    if isinstance(instance, UserAccessGroup):
        return instance.group.school

    if isinstance(instance, UserPermissionOverride):
        return instance.school

    return None


def module_object_repr(instance):
    if isinstance(instance, AccessGroup):
        return f"Grupo de acesso: {instance.name}"

    if isinstance(instance, AccessGroupPermission):
        return f"{instance.group.name} -> {instance.permission_code}"

    if isinstance(instance, UserAccessGroup):
        return f"{instance.user} -> {instance.group.name}"

    if isinstance(instance, UserPermissionOverride):
        return f"{instance.user} -> {instance.permission_code}"

    return str(instance)


def action_for(instance, created: bool):
    if created:
        if isinstance(instance, AccessGroupPermission):
            return (
                AuditAction.PERMISSION_GRANTED
                if instance.allowed
                else AuditAction.PERMISSION_REVOKED
            )

        if isinstance(instance, UserPermissionOverride):
            return (
                AuditAction.PERMISSION_GRANTED
                if instance.allowed
                else AuditAction.PERMISSION_REVOKED
            )

        if isinstance(instance, UserAccessGroup):
            return AuditAction.PERMISSION_GRANTED

        return AuditAction.CREATED

    if isinstance(instance, AccessGroupPermission):
        return (
            AuditAction.PERMISSION_GRANTED
            if instance.allowed
            else AuditAction.PERMISSION_REVOKED
        )

    if isinstance(instance, UserPermissionOverride):
        return (
            AuditAction.PERMISSION_GRANTED
            if instance.allowed
            else AuditAction.PERMISSION_REVOKED
        )

    if isinstance(instance, UserAccessGroup) and not instance.is_active:
        return AuditAction.PERMISSION_REVOKED

    return AuditAction.UPDATED


@receiver(pre_save, sender=AccessGroup)
@receiver(pre_save, sender=AccessGroupPermission)
@receiver(pre_save, sender=UserAccessGroup)
@receiver(pre_save, sender=UserPermissionOverride)
def store_permission_before_snapshot(sender, instance, **kwargs):
    if not instance.pk:
        instance._audit_before = {}
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        instance._audit_before = {}
        return

    instance._audit_before = snapshot(old_instance)


@receiver(post_save, sender=AccessGroup)
@receiver(post_save, sender=AccessGroupPermission)
@receiver(post_save, sender=UserAccessGroup)
@receiver(post_save, sender=UserPermissionOverride)
def audit_permission_model_saved(sender, instance, created, **kwargs):
    before = getattr(instance, "_audit_before", {})
    after = snapshot(instance)

    if not created and not changed_values(before, after):
        return

    metadata = {
        "event": "permission_model_saved",
        "model": sender.__name__,
        "created": created,
        "changes": changed_values(before, after),
    }

    if isinstance(instance, AccessGroupPermission):
        metadata["permission_code"] = instance.permission_code
        metadata["allowed"] = instance.allowed
        metadata["group_id"] = instance.group_id

    if isinstance(instance, UserAccessGroup):
        metadata["target_user_id"] = instance.user_id
        metadata["group_id"] = instance.group_id

    if isinstance(instance, UserPermissionOverride):
        metadata["target_user_id"] = instance.user_id
        metadata["permission_code"] = instance.permission_code
        metadata["allowed"] = instance.allowed

    record_audit_event(
        actor_user=actor_for(instance),
        school=school_for(instance),
        action=action_for(instance, created),
        module="accounts.permissions",
        obj=instance,
        object_repr=module_object_repr(instance),
        changes_before=before,
        changes_after=after,
        metadata=metadata,
    )
