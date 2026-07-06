from __future__ import annotations

from typing import Iterable

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpRequest

from apps.auditlog.models import AuditAction
from apps.auditlog.services import get_client_ip, get_user_agent, record_audit_event
from apps.communications.models import (
    Message,
    MessageAudience,
    MessagePriority,
    MessageReadReceipt,
    MessageRecipient,
    MessageRecipientStatus,
    MessageStatus,
)


User = get_user_model()


@transaction.atomic
def create_message(
    *,
    school,
    sender,
    title: str,
    body: str,
    audience: str = MessageAudience.CUSTOM,
    priority: str = MessagePriority.NORMAL,
    requires_read_confirmation: bool = False,
    recipients: Iterable = (),
    related_student=None,
    send_now: bool = False,
    request: HttpRequest | None = None,
) -> Message:
    message = Message.objects.create(
        school=school,
        sender=sender,
        title=title,
        body=body,
        audience=audience,
        priority=priority,
        requires_read_confirmation=requires_read_confirmation,
        status=MessageStatus.DRAFT,
    )

    recipient_objects = [
        MessageRecipient(
            message=message,
            user=recipient,
            student=related_student,
            status=MessageRecipientStatus.PENDING,
        )
        for recipient in recipients
    ]

    if recipient_objects:
        MessageRecipient.objects.bulk_create(recipient_objects, ignore_conflicts=True)

    record_audit_event(
        request=request,
        actor_user=sender,
        school=school,
        action=AuditAction.CREATED,
        module="communications",
        obj=message,
        changes_after={
            "title": title,
            "audience": audience,
            "priority": priority,
            "requires_read_confirmation": requires_read_confirmation,
            "recipient_count": len(recipient_objects),
            "status": MessageStatus.DRAFT,
        },
        metadata={
            "event": "message_created",
        },
    )

    if send_now:
        send_message(message=message, actor_user=sender, request=request)

    return message


@transaction.atomic
def send_message(
    *,
    message: Message,
    actor_user=None,
    request: HttpRequest | None = None,
) -> Message:
    previous_status = message.status

    message.mark_as_sent()

    message.recipients.filter(status=MessageRecipientStatus.PENDING).update(
        status=MessageRecipientStatus.DELIVERED,
        delivered_at=message.sent_at,
    )

    record_audit_event(
        request=request,
        actor_user=actor_user or message.sender,
        school=message.school,
        action=AuditAction.MESSAGE_SENT,
        module="communications",
        obj=message,
        changes_before={
            "status": previous_status,
        },
        changes_after={
            "status": message.status,
            "sent_at": message.sent_at.isoformat() if message.sent_at else None,
            "recipient_count": message.recipients.count(),
        },
        metadata={
            "event": "message_sent",
        },
    )

    return message


@transaction.atomic
def mark_message_read(
    *,
    recipient: MessageRecipient,
    read_by,
    request: HttpRequest | None = None,
    metadata: dict | None = None,
) -> MessageReadReceipt:
    previous_status = recipient.status
    previous_read_count = recipient.read_count

    recipient.mark_read()

    receipt = MessageReadReceipt.objects.create(
        recipient=recipient,
        read_by=read_by,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        metadata=metadata or {},
    )

    record_audit_event(
        request=request,
        actor_user=read_by,
        school=recipient.message.school,
        action=AuditAction.MESSAGE_READ,
        module="communications",
        obj=recipient.message,
        changes_before={
            "recipient_status": previous_status,
            "read_count": previous_read_count,
        },
        changes_after={
            "recipient_status": recipient.status,
            "read_count": recipient.read_count,
            "first_read_at": recipient.first_read_at.isoformat() if recipient.first_read_at else None,
            "last_read_at": recipient.last_read_at.isoformat() if recipient.last_read_at else None,
        },
        metadata={
            "event": "message_read",
            "recipient_id": recipient.id,
            "receipt_id": receipt.id,
        },
    )

    return receipt


def unread_recipients_for_message(message: Message):
    return message.recipients.exclude(status=MessageRecipientStatus.READ)


def read_recipients_for_message(message: Message):
    return message.recipients.filter(status=MessageRecipientStatus.READ)


def pending_recipients_for_user(user):
    return MessageRecipient.objects.filter(
        user=user,
        message__status=MessageStatus.SENT,
    ).exclude(status=MessageRecipientStatus.READ)
