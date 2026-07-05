from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class CollaboratorStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Ativo"
    INACTIVE = "INACTIVE", "Inativo"
    ON_LEAVE = "ON_LEAVE", "Afastado"


class CollaboratorContractType(models.TextChoices):
    CLT = "CLT", "CLT"
    PJ = "PJ", "Pessoa Jurídica"
    TEMPORARY = "TEMPORARY", "Temporário"
    INTERN = "INTERN", "Estagiário"
    OUTSOURCED = "OUTSOURCED", "Terceirizado"
    OTHER = "OTHER", "Outro"


class CollaboratorDepartment(models.TextChoices):
    ADMINISTRATION = "ADMINISTRATION", "Administrativo"
    SECRETARIAT = "SECRETARIAT", "Secretaria"
    COORDINATION = "COORDINATION", "Coordenação"
    INSPECTION = "INSPECTION", "Inspetoria"
    CAFETERIA = "CAFETERIA", "Cantina"
    CLEANING = "CLEANING", "Limpeza"
    SECURITY = "SECURITY", "Segurança"
    MAINTENANCE = "MAINTENANCE", "Manutenção"
    TRANSPORT = "TRANSPORT", "Transporte"
    IT = "IT", "Tecnologia"
    OTHER = "OTHER", "Outro"


class Collaborator(models.Model):
    school = models.ForeignKey(
        "schools.School",
        verbose_name="escola",
        on_delete=models.CASCADE,
        related_name="collaborators",
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="usuário de acesso",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collaborator_profile",
        help_text="Usuário usado para login do colaborador no PortalK12, quando houver.",
    )

    full_name = models.CharField("nome completo", max_length=180)
    preferred_name = models.CharField("nome de exibição", max_length=120, blank=True)

    document = models.CharField("CPF/RG", max_length=32, blank=True)
    registration_number = models.CharField("matrícula funcional", max_length=50, blank=True)

    email = models.EmailField("e-mail", blank=True)
    phone = models.CharField("telefone", max_length=32, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=32, blank=True)

    birth_date = models.DateField("data de nascimento", null=True, blank=True)

    department = models.CharField(
        "setor",
        max_length=30,
        choices=CollaboratorDepartment.choices,
        default=CollaboratorDepartment.OTHER,
    )

    job_title = models.CharField(
        "cargo/função",
        max_length=120,
        help_text="Exemplo: Secretária, Inspetor, Auxiliar de limpeza, Porteiro.",
    )

    contract_type = models.CharField(
        "tipo de contrato",
        max_length=20,
        choices=CollaboratorContractType.choices,
        default=CollaboratorContractType.OTHER,
    )

    admission_date = models.DateField("data de admissão", null=True, blank=True)
    termination_date = models.DateField("data de desligamento", null=True, blank=True)

    status = models.CharField(
        "status",
        max_length=20,
        choices=CollaboratorStatus.choices,
        default=CollaboratorStatus.ACTIVE,
    )

    can_access_system = models.BooleanField(
        "pode acessar o sistema",
        default=False,
        help_text="Marque se este colaborador terá login no PortalK12.",
    )

    notes = models.TextField("observações", blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="criado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_collaborators",
    )

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "colaborador"
        verbose_name_plural = "colaboradores"
        ordering = ["full_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "registration_number"],
                name="unique_collaborator_registration_per_school",
                condition=~models.Q(registration_number=""),
            ),
            models.UniqueConstraint(
                fields=["school", "document"],
                name="unique_collaborator_document_per_school",
                condition=~models.Q(document=""),
            ),
        ]

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return self.preferred_name or self.full_name

    @property
    def has_login_access(self):
        return self.user_id is not None and self.can_access_system