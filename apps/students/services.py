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
from apps.students.models import Student


STUDENT_AUDIT_MODULE = "students"


def get_actor_from_request(request: HttpRequest | None):
    if request is None:
        return None

    user = getattr(request, "user", None)

    if user and getattr(user, "is_authenticated", False):
        return user

    return None


@transaction.atomic
def create_student(
    *,
    data: dict[str, Any],
    actor_user=None,
    request: HttpRequest | None = None,
    metadata: dict | None = None,
) -> Student:
    """
    Cria aluno com auditoria.

    Importante:
    - data deve conter os campos esperados pelo model Student.
    - A validação de formulário/view continua fora deste service por enquanto.
    """
    actor_user = actor_user or get_actor_from_request(request)

    student = Student.objects.create(**data)

    audit_created(
        obj=student,
        module=STUDENT_AUDIT_MODULE,
        request=request,
        actor_user=actor_user,
        metadata={
            "permission_code": codes.STUDENTS_CREATE,
            "event": "student_created",
            **(metadata or {}),
        },
    )

    return student


@transaction.atomic
def update_student(
    *,
    student: Student,
    data: dict[str, Any],
    actor_user=None,
    request: HttpRequest | None = None,
    metadata: dict | None = None,
) -> Student:
    """
    Atualiza aluno com auditoria.

    Campos inexistentes no model são ignorados para evitar quebra em evolução de formulário.
    """
    actor_user = actor_user or get_actor_from_request(request)

    before = model_snapshot(student)

    changed_fields = []

    for field_name, value in data.items():
        if not hasattr(student, field_name):
            continue

        current_value = getattr(student, field_name)

        if current_value != value:
            setattr(student, field_name, value)
            changed_fields.append(field_name)

    if changed_fields:
        student.save(update_fields=changed_fields)

        audit_updated(
            obj=student,
            module=STUDENT_AUDIT_MODULE,
            before=before,
            request=request,
            actor_user=actor_user,
            metadata={
                "permission_code": codes.STUDENTS_UPDATE,
                "event": "student_updated",
                "changed_fields": changed_fields,
                **(metadata or {}),
            },
        )

    return student


@transaction.atomic
def soft_delete_student(
    *,
    student: Student,
    actor_user=None,
    request: HttpRequest | None = None,
    reason: str = "",
    metadata: dict | None = None,
) -> Student:
    """
    Inativa/remove logicamente um aluno com auditoria.

    Compatível com diferentes formatos de model:
    - se existir deleted_at/deleted_by/delete_reason, usa esses campos;
    - se existir is_active, marca como False;
    - se existir status, tenta usar INACTIVE como padrão sem forçar enum específico.
    """
    actor_user = actor_user or get_actor_from_request(request)

    before = model_snapshot(student)

    update_fields = []

    if hasattr(student, "deleted_at"):
        student.deleted_at = timezone.now()
        update_fields.append("deleted_at")

    if hasattr(student, "deleted_by"):
        student.deleted_by = actor_user
        update_fields.append("deleted_by")

    if hasattr(student, "delete_reason"):
        student.delete_reason = reason
        update_fields.append("delete_reason")

    if hasattr(student, "is_active"):
        student.is_active = False
        update_fields.append("is_active")

    if hasattr(student, "status"):
        status_choices = getattr(student._meta.get_field("status"), "choices", []) or []
        valid_values = {value for value, _label in status_choices}

        if "inactive" in valid_values:
            student.status = "inactive"
            update_fields.append("status")
        elif "INACTIVE" in valid_values:
            student.status = "INACTIVE"
            update_fields.append("status")

    if update_fields:
        student.save(update_fields=list(dict.fromkeys(update_fields)))

    audit_deleted(
        obj=student,
        module=STUDENT_AUDIT_MODULE,
        before=before,
        request=request,
        actor_user=actor_user,
        metadata={
            "permission_code": codes.STUDENTS_DELETE,
            "event": "student_soft_deleted",
            "reason": reason,
            **(metadata or {}),
        },
    )

    return student


@transaction.atomic
def restore_student(
    *,
    student: Student,
    actor_user=None,
    request: HttpRequest | None = None,
    metadata: dict | None = None,
) -> Student:
    """
    Restaura aluno inativado/removido logicamente com auditoria.
    """
    actor_user = actor_user or get_actor_from_request(request)

    before = model_snapshot(student)

    update_fields = []

    if hasattr(student, "deleted_at"):
        student.deleted_at = None
        update_fields.append("deleted_at")

    if hasattr(student, "deleted_by"):
        student.deleted_by = None
        update_fields.append("deleted_by")

    if hasattr(student, "delete_reason"):
        student.delete_reason = ""
        update_fields.append("delete_reason")

    if hasattr(student, "is_active"):
        student.is_active = True
        update_fields.append("is_active")

    if hasattr(student, "status"):
        status_choices = getattr(student._meta.get_field("status"), "choices", []) or []
        valid_values = {value for value, _label in status_choices}

        if "active" in valid_values:
            student.status = "active"
            update_fields.append("status")
        elif "ACTIVE" in valid_values:
            student.status = "ACTIVE"
            update_fields.append("status")

    if update_fields:
        student.save(update_fields=list(dict.fromkeys(update_fields)))

    audit_restored(
        obj=student,
        module=STUDENT_AUDIT_MODULE,
        before=before,
        request=request,
        actor_user=actor_user,
        metadata={
            "permission_code": codes.STUDENTS_UPDATE,
            "event": "student_restored",
            **(metadata or {}),
        },
    )

    return student


def record_student_viewed(
    *,
    student: Student,
    actor_user=None,
    request: HttpRequest | None = None,
    metadata: dict | None = None,
):
    """
    Registra visualização de aluno.

    Atenção:
    - Não deve ser chamado em toda listagem para não gerar volume absurdo.
    - Usar em telas sensíveis, como detalhe completo do aluno.
    """
    actor_user = actor_user or get_actor_from_request(request)

    return record_audit_event(
        request=request,
        actor_user=actor_user,
        action=AuditAction.OTHER,
        module=STUDENT_AUDIT_MODULE,
        obj=student,
        metadata={
            "permission_code": codes.STUDENTS_VIEW,
            "event": "student_viewed",
            **(metadata or {}),
        },
    )
