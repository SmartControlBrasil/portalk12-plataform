from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class VisitorStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Ativo"
    BLOCKED = "BLOCKED", "Bloqueado"
    WATCHLIST = "WATCHLIST", "Atenção"


class VisitorDocumentType(models.TextChoices):
    RG = "RG", "RG"
    CPF = "CPF", "CPF"
    CNH = "CNH", "CNH"
    PASSPORT = "PASSPORT", "Passaporte"
    COMPANY_BADGE = "COMPANY_BADGE", "Crachá da empresa"
    OTHER = "OTHER", "Outro"


class VisitPurpose(models.TextChoices):
    MEETING = "MEETING", "Reunião"
    STUDENT_PICKUP = "STUDENT_PICKUP", "Retirada de aluno"
    STUDENT_DROPOFF = "STUDENT_DROPOFF", "Entrega de aluno"
    SERVICE_PROVIDER = "SERVICE_PROVIDER", "Prestador de serviço"
    DELIVERY = "DELIVERY", "Entrega"
    EVENT = "EVENT", "Evento"
    INTERVIEW = "INTERVIEW", "Entrevista"
    OTHER = "OTHER", "Outro"


class VisitStatus(models.TextChoices):
    SCHEDULED = "SCHEDULED", "Agendada"
    CHECKED_IN = "CHECKED_IN", "Entrada registrada"
    CHECKED_OUT = "CHECKED_OUT", "Saída registrada"
    CANCELLED = "CANCELLED", "Cancelada"
    DENIED = "DENIED", "Negada"


class Visitor(models.Model):
    school = models.ForeignKey(
        "schools.School",
        verbose_name="escola",
        on_delete=models.CASCADE,
        related_name="visitors",
    )

    full_name = models.CharField("nome completo", max_length=180)

    document_type = models.CharField(
        "tipo de documento",
        max_length=30,
        choices=VisitorDocumentType.choices,
        default=VisitorDocumentType.CPF,
    )

    document_number = models.CharField("número do documento", max_length=50, blank=True)

    phone = models.CharField("telefone", max_length=32, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=32, blank=True)
    email = models.EmailField("e-mail", blank=True)

    company_name = models.CharField(
        "empresa/organização",
        max_length=180,
        blank=True,
        help_text="Use para prestadores de serviço, entregadores, fornecedores ou visitantes corporativos.",
    )

    photo = models.ImageField(
        "foto do visitante",
        upload_to="visitors/photos/",
        null=True,
        blank=True,
    )

    status = models.CharField(
        "status",
        max_length=20,
        choices=VisitorStatus.choices,
        default=VisitorStatus.ACTIVE,
    )

    notes = models.TextField("observações", blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="criado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_visitors",
    )

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "visitante"
        verbose_name_plural = "visitantes"
        ordering = ["full_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "document_type", "document_number"],
                name="unique_visitor_document_per_school",
                condition=~models.Q(document_number=""),
            ),
        ]

    def __str__(self):
        return self.full_name

    @property
    def is_blocked(self):
        return self.status == VisitorStatus.BLOCKED

    @property
    def requires_attention(self):
        return self.status in {
            VisitorStatus.BLOCKED,
            VisitorStatus.WATCHLIST,
        }


class Visit(models.Model):
    school = models.ForeignKey(
        "schools.School",
        verbose_name="escola",
        on_delete=models.CASCADE,
        related_name="visits",
    )

    visitor = models.ForeignKey(
        Visitor,
        verbose_name="visitante",
        on_delete=models.CASCADE,
        related_name="visits",
    )

    purpose = models.CharField(
        "motivo da visita",
        max_length=30,
        choices=VisitPurpose.choices,
        default=VisitPurpose.OTHER,
    )

    purpose_description = models.CharField(
        "descrição do motivo",
        max_length=220,
        blank=True,
        help_text="Exemplo: reunião com coordenação, manutenção do portão, retirada autorizada.",
    )

    related_student = models.ForeignKey(
        "students.Student",
        verbose_name="aluno relacionado",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_visits",
    )

    host_teacher = models.ForeignKey(
        "teachers.Teacher",
        verbose_name="professor visitado",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hosted_visits",
    )

    host_collaborator = models.ForeignKey(
        "collaborators.Collaborator",
        verbose_name="colaborador visitado",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hosted_visits",
    )

    authorized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="autorizado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="authorized_visits",
    )

    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="entrada registrada por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="checked_in_visits",
    )

    checked_out_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="saída registrada por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="checked_out_visits",
    )

    scheduled_at = models.DateTimeField("data/hora agendada", null=True, blank=True)
    checked_in_at = models.DateTimeField("entrada em", null=True, blank=True)
    checked_out_at = models.DateTimeField("saída em", null=True, blank=True)

    badge_number = models.CharField("número do crachá", max_length=40, blank=True)

    vehicle_plate = models.CharField(
        "placa do veículo",
        max_length=20,
        blank=True,
        help_text="Use apenas quando a escola controlar acesso de veículos.",
    )

    status = models.CharField(
        "status da visita",
        max_length=20,
        choices=VisitStatus.choices,
        default=VisitStatus.SCHEDULED,
    )

    denial_reason = models.TextField("motivo da negativa", blank=True)
    notes = models.TextField("observações", blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="criado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_visits",
    )

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "visita"
        verbose_name_plural = "visitas"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.visitor.full_name} - {self.get_purpose_display()}"

    @property
    def is_open(self):
        return self.status == VisitStatus.CHECKED_IN and self.checked_out_at is None

    @property
    def is_finished(self):
        return self.status == VisitStatus.CHECKED_OUT and self.checked_out_at is not None


class VisitorDocument(models.Model):
    visitor = models.ForeignKey(
        Visitor,
        verbose_name="visitante",
        on_delete=models.CASCADE,
        related_name="documents",
    )

    title = models.CharField("título", max_length=180)

    document_type = models.CharField(
        "tipo de documento",
        max_length=30,
        choices=VisitorDocumentType.choices,
        default=VisitorDocumentType.OTHER,
    )

    file = models.FileField("arquivo", upload_to="visitors/documents/")

    description = models.TextField("descrição", blank=True)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="enviado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_visitor_documents",
    )

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "documento do visitante"
        verbose_name_plural = "documentos dos visitantes"
        ordering = ["visitor__full_name", "title"]

    def __str__(self):
        return f"{self.visitor.full_name} - {self.title}"