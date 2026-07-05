from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class TeacherStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Ativo"
    INACTIVE = "INACTIVE", "Inativo"
    ON_LEAVE = "ON_LEAVE", "Afastado"


class TeacherContractType(models.TextChoices):
    CLT = "CLT", "CLT"
    PJ = "PJ", "Pessoa Jurídica"
    TEMPORARY = "TEMPORARY", "Temporário"
    INTERN = "INTERN", "Estagiário"
    OTHER = "OTHER", "Outro"


class EducationLevel(models.TextChoices):
    TECHNICAL = "TECHNICAL", "Técnico"
    UNDERGRADUATE = "UNDERGRADUATE", "Graduação"
    SPECIALIZATION = "SPECIALIZATION", "Especialização"
    MBA = "MBA", "MBA"
    MASTER = "MASTER", "Mestrado"
    DOCTORATE = "DOCTORATE", "Doutorado"
    POST_DOCTORATE = "POST_DOCTORATE", "Pós-doutorado"
    OTHER = "OTHER", "Outro"


class Teacher(models.Model):
    school = models.ForeignKey(
        "schools.School",
        verbose_name="escola",
        on_delete=models.CASCADE,
        related_name="teachers",
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="usuário de acesso",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teacher_profile",
        help_text="Usuário usado para login do professor no PortalK12.",
    )

    full_name = models.CharField("nome completo", max_length=180)
    preferred_name = models.CharField("nome de exibição", max_length=120, blank=True)

    document = models.CharField("CPF/RG", max_length=32, blank=True)
    registration_number = models.CharField("matrícula funcional", max_length=50, blank=True)

    email = models.EmailField("e-mail", blank=True)
    phone = models.CharField("telefone", max_length=32, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=32, blank=True)

    birth_date = models.DateField("data de nascimento", null=True, blank=True)

    main_subject = models.CharField("disciplina principal", max_length=120, blank=True)
    subjects = models.CharField(
        "disciplinas",
        max_length=255,
        blank=True,
        help_text="Exemplo: Matemática, Física, Robótica.",
    )

    contract_type = models.CharField(
        "tipo de contrato",
        max_length=20,
        choices=TeacherContractType.choices,
        default=TeacherContractType.OTHER,
    )

    admission_date = models.DateField("data de admissão", null=True, blank=True)

    status = models.CharField(
        "status",
        max_length=20,
        choices=TeacherStatus.choices,
        default=TeacherStatus.ACTIVE,
    )

    notes = models.TextField("observações", blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="criado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_teachers",
    )

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "professor"
        verbose_name_plural = "professores"
        ordering = ["full_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "registration_number"],
                name="unique_teacher_registration_per_school",
                condition=~models.Q(registration_number=""),
            ),
            models.UniqueConstraint(
                fields=["school", "document"],
                name="unique_teacher_document_per_school",
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
        return self.user_id is not None


class TeacherEducation(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        verbose_name="professor",
        on_delete=models.CASCADE,
        related_name="educations",
    )

    level = models.CharField(
        "nível",
        max_length=30,
        choices=EducationLevel.choices,
        default=EducationLevel.UNDERGRADUATE,
    )

    course_name = models.CharField("curso/formação", max_length=180)
    institution = models.CharField("instituição", max_length=180, blank=True)

    start_year = models.PositiveSmallIntegerField("ano de início", null=True, blank=True)
    end_year = models.PositiveSmallIntegerField("ano de conclusão", null=True, blank=True)

    is_completed = models.BooleanField("concluído", default=True)

    certificate_file = models.FileField(
        "certificado/diploma",
        upload_to="teachers/education/",
        null=True,
        blank=True,
    )

    notes = models.TextField("observações", blank=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "formação do professor"
        verbose_name_plural = "formações dos professores"
        ordering = ["-end_year", "level", "course_name"]

    def __str__(self):
        return f"{self.teacher.display_name} - {self.course_name}"
        