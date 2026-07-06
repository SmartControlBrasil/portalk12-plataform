from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class MessageAudience(models.TextChoices):
    SCHOOL = "school", "Toda a escola"
    CLASS = "class", "Turma"
    STUDENT = "student", "Aluno"
    GUARDIAN = "guardian", "Responsável"
    TEACHER = "teacher", "Professor"
    STAFF = "staff", "Equipe interna"
    CUSTOM = "custom", "Personalizado"


class MessagePriority(models.TextChoices):
    LOW = "low", "Baixa"
    NORMAL = "normal", "Normal"
    HIGH = "high", "Alta"
    URGENT = "urgent", "Urgente"


class MessageStatus(models.TextChoices):
    DRAFT = "draft", "Rascunho"
    SENT = "sent", "Enviada"
    ARCHIVED = "archived", "Arquivada"
    CANCELLED = "cancelled", "Cancelada"


class MessageRecipientStatus(models.TextChoices):
    PENDING = "pending", "Pendente"
    DELIVERED = "delivered", "Entregue"
    READ = "read", "Lida"
    FAILED = "failed", "Falhou"


class Message(models.Model):
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="escola",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_messages",
        verbose_name="remetente",
    )

    title = models.CharField(
        max_length=180,
        verbose_name="título",
    )
    body = models.TextField(
        verbose_name="mensagem",
    )
    audience = models.CharField(
        max_length=30,
        choices=MessageAudience.choices,
        default=MessageAudience.CUSTOM,
        verbose_name="público",
    )
    priority = models.CharField(
        max_length=20,
        choices=MessagePriority.choices,
        default=MessagePriority.NORMAL,
        verbose_name="prioridade",
    )
    status = models.CharField(
        max_length=20,
        choices=MessageStatus.choices,
        default=MessageStatus.DRAFT,
        verbose_name="status",
    )

    requires_read_confirmation = models.BooleanField(
        default=False,
        verbose_name="exige confirmação de leitura",
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="enviada em",
    )
    archived_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="arquivada em",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="criada em",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="atualizada em",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "mensagem"
        verbose_name_plural = "mensagens"
        indexes = [
            models.Index(fields=["school", "status", "created_at"]),
            models.Index(fields=["school", "audience", "created_at"]),
            models.Index(fields=["sender", "created_at"]),
            models.Index(fields=["priority", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.title

    def mark_as_sent(self):
        self.status = MessageStatus.SENT
        self.sent_at = timezone.now()
        self.save(update_fields=["status", "sent_at", "updated_at"])


class MessageRecipient(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="recipients",
        verbose_name="mensagem",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages",
        verbose_name="usuário destinatário",
    )

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="message_recipients",
        verbose_name="aluno relacionado",
    )

    status = models.CharField(
        max_length=20,
        choices=MessageRecipientStatus.choices,
        default=MessageRecipientStatus.PENDING,
        verbose_name="status",
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="entregue em",
    )
    first_read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="primeira leitura em",
    )
    last_read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="última leitura em",
    )
    read_count = models.PositiveIntegerField(
        default=0,
        verbose_name="quantidade de leituras",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="criado em",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="atualizado em",
    )

    class Meta:
        ordering = ["message", "user"]
        verbose_name = "destinatário da mensagem"
        verbose_name_plural = "destinatários da mensagem"
        constraints = [
            models.UniqueConstraint(
                fields=["message", "user", "student"],
                name="unique_message_recipient_user_student",
            )
        ]
        indexes = [
            models.Index(fields=["user", "status", "created_at"]),
            models.Index(fields=["message", "status"]),
            models.Index(fields=["student", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.message}"

    def mark_delivered(self):
        if not self.delivered_at:
            self.delivered_at = timezone.now()

        if self.status == MessageRecipientStatus.PENDING:
            self.status = MessageRecipientStatus.DELIVERED

        self.save(update_fields=["status", "delivered_at", "updated_at"])

    def mark_read(self):
        now = timezone.now()

        if not self.delivered_at:
            self.delivered_at = now

        if not self.first_read_at:
            self.first_read_at = now

        self.last_read_at = now
        self.read_count += 1
        self.status = MessageRecipientStatus.READ

        self.save(
            update_fields=[
                "status",
                "delivered_at",
                "first_read_at",
                "last_read_at",
                "read_count",
                "updated_at",
            ]
        )


class MessageReadReceipt(models.Model):
    recipient = models.ForeignKey(
        MessageRecipient,
        on_delete=models.CASCADE,
        related_name="read_receipts",
        verbose_name="destinatário",
    )
    read_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="message_read_receipts",
        verbose_name="lido por",
    )
    read_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="lido em",
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
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="metadados",
    )

    class Meta:
        ordering = ["-read_at"]
        verbose_name = "comprovante de leitura"
        verbose_name_plural = "comprovantes de leitura"
        indexes = [
            models.Index(fields=["recipient", "read_at"]),
            models.Index(fields=["read_by", "read_at"]),
        ]

    def __str__(self) -> str:
        return f"Leitura de {self.recipient} em {self.read_at:%d/%m/%Y %H:%M}"
