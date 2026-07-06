from __future__ import annotations

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from apps.auditlog.models import AuditAction
from apps.auditlog.services import record_audit_event


@receiver(user_logged_in)
def audit_user_logged_in(sender, request, user, **kwargs):
    record_audit_event(
        request=request,
        actor_user=user,
        action=AuditAction.LOGIN_SUCCESS,
        module="accounts",
        object_type=user.__class__.__name__,
        object_id=str(user.pk),
        object_repr=getattr(user, "email", "") or getattr(user, "username", "") or str(user),
        metadata={
            "event": "user_logged_in",
        },
    )


@receiver(user_logged_out)
def audit_user_logged_out(sender, request, user, **kwargs):
    if user is None:
        return

    record_audit_event(
        request=request,
        actor_user=user,
        action=AuditAction.LOGOUT,
        module="accounts",
        object_type=user.__class__.__name__,
        object_id=str(user.pk),
        object_repr=getattr(user, "email", "") or getattr(user, "username", "") or str(user),
        metadata={
            "event": "user_logged_out",
        },
    )


@receiver(user_login_failed)
def audit_user_login_failed(sender, credentials, request, **kwargs):
    safe_credentials = {}

    for key, value in (credentials or {}).items():
        if key.lower() in {"password", "senha"}:
            safe_credentials[key] = "***"
        else:
            safe_credentials[key] = value

    record_audit_event(
        request=request,
        actor_user=None,
        action=AuditAction.LOGIN_FAILED,
        module="accounts",
        object_type="Authentication",
        object_id="",
        object_repr=str(safe_credentials.get("username") or safe_credentials.get("email") or "tentativa de login"),
        metadata={
            "event": "user_login_failed",
            "credentials": safe_credentials,
        },
    )
