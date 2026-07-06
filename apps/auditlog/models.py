from __future__ import annotations

from django.conf import settings
from django.db import models


class AuditAction(models.TextChoices):
    CREATED = "created", "Criado"
    UPDATED = "updated", "Atualizado"
    DELETED = "deleted", "Excluído"
    RESTORED = "restored", "Restaurado"

    LOGIN_SUCCESS = "login_success", "Login realizado"
    LOGIN_FAILED = "login_failed", "Falha de login"
    LOGOUT = "logout", "Logout"

    PERMISSION_GRANTED = "permission_granted", "Permissão concedida"
    PERMISSION_REVOKED = "permission_revoked", "Permissão removida"
    ROLE_CHANGED = "role_changed", "Perfil alterado"

    MESSAGE_SENT = "message_sent", "Mensagem enviada"
    MESSAGE_READ = "message_read", "Mensagem lida"

    FILE_UPLOADED = "file_uploaded", "Arquivo enviado"
    FILE_DELETED = "file_deleted", "Arquivo excluído"

    OTHER = "other", "Outra ação"


class AuditLog(models.Model):
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="escola",
    )
    actor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="usuário responsável",
    )
    actor_role = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="perfil do usuário",
    )

    action = models.CharField(
        max_length=80,
        choices=AuditAction.choices,
        default=AuditAction.OTHER,
        verbose_name="ação",
    )
    module = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="módulo",
    )

    object_type = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="tipo do registro",
    )
    object_id = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="id do registro",
    )
    object_repr = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="representação do registro",
    )

    changes_before = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="dados anteriores",
    )
    changes_after = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="dados novos",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="metadados",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="endereço IP",
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="navegador/dispositivo",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="criado em",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "log de auditoria"
        verbose_name_plural = "logs de auditoria"
        indexes = [
            models.Index(fields=["school", "created_at"]),
            models.Index(fields=["actor_user", "created_at"]),
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["module", "created_at"]),
            models.Index(fields=["object_type", "object_id"]),
        ]

    def __str__(self) -> str:
        actor = self.actor_user or "sistema"
        target = self.object_repr or self.object_type or "registro"
        return f"{self.get_action_display()} por {actor} em {target}"
