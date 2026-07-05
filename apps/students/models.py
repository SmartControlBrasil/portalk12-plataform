from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class StudentStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Ativo"
    INACTIVE = "INACTIVE", "Inativo"
    TRANSFERRED = "TRANSFERRED", "Transferido"
    GRADUATED = "GRADUATED", "Concluído"
    SUSPENDED = "SUSPENDED", "Suspenso"


class StudentGender(models.TextChoices):
    FEMALE = "FEMALE", "Feminino"
    MALE = "MALE", "Masculino"
    OTHER = "OTHER", "Outro"
    NOT_INFORMED = "NOT_INFORMED", "Não informado"


class GuardianRelationship(models.TextChoices):
    MOTHER = "MOTHER", "Mãe"
    FATHER = "FATHER", "Pai"
    GRANDMOTHER = "GRANDMOTHER", "Avó"
    GRANDFATHER = "GRANDFATHER", "Avô"
    AUNT = "AUNT", "Tia"
    UNCLE = "UNCLE", "Tio"
    LEGAL_GUARDIAN = "LEGAL_GUARDIAN", "Responsável legal"
    OTHER = "OTHER", "Outro"


class StudentDocumentType(models.TextChoices):
    RG = "RG", "RG"
    CPF = "CPF", "CPF"
    BIRTH_CERTIFICATE = "BIRTH_CERTIFICATE", "Certidão de nascimento"
    VACCINATION_CARD = "VACCINATION_CARD", "Carteira de vacinação"
    SCHOOL_RECORD = "SCHOOL_RECORD", "Histórico escolar"
    MEDICAL_REPORT = "MEDICAL_REPORT", "Laudo médico"
    AUTHORIZATION = "AUTHORIZATION", "Autorização"
    OTHER = "OTHER", "Outro"


class Student(models.Model):
    school = models.ForeignKey(
        "schools.School",
        verbose_name="escola",
        on_delete=models.CASCADE,
        related_name="students",
    )

    full_name = models.CharField("nome completo", max_length=180)
    preferred_name = models.CharField("nome de exibição", max_length=120, blank=True)

    registration_number = models.CharField("RA/matrícula", max_length=50, blank=True)
    document = models.CharField("CPF/RG", max_length=32, blank=True)

    birth_date = models.DateField("data de nascimento", null=True, blank=True)
    gender = models.CharField(
        "gênero",
        max_length=20,
        choices=StudentGender.choices,
        default=StudentGender.NOT_INFORMED,
    )

    email = models.EmailField("e-mail do aluno", blank=True)
    phone = models.CharField("telefone do aluno", max_length=32, blank=True)

    current_grade = models.CharField(
        "série/ano atual",
        max_length=80,
        blank=True,
        help_text="Exemplo: 5º ano, 1º ano EM, Infantil II.",
    )

    current_shift = models.CharField(
        "turno atual",
        max_length=80,
        blank=True,
        help_text="Exemplo: Manhã, Tarde, Integral.",
    )

    status = models.CharField(
        "status",
        max_length=20,
        choices=StudentStatus.choices,
        default=StudentStatus.ACTIVE,
    )

    enrollment_date = models.DateField("data de matrícula", null=True, blank=True)

    zip_code = models.CharField("CEP", max_length=16, blank=True)
    address = models.CharField("endereço", max_length=220, blank=True)
    number = models.CharField("número", max_length=20, blank=True)
    complement = models.CharField("complemento", max_length=120, blank=True)
    district = models.CharField("bairro", max_length=120, blank=True)
    city = models.CharField("cidade", max_length=120, blank=True)
    state = models.CharField("UF", max_length=2, blank=True)

    has_medical_condition = models.BooleanField("possui condição médica", default=False)
    medical_condition_notes = models.TextField("observações médicas", blank=True)

    has_allergy = models.BooleanField("possui alergia", default=False)
    allergy_notes = models.TextField("observações sobre alergias", blank=True)

    uses_medication = models.BooleanField("usa medicamento contínuo", default=False)
    medication_notes = models.TextField("observações sobre medicamentos", blank=True)

    emergency_contact_name = models.CharField("contato de emergência", max_length=180, blank=True)
    emergency_contact_phone = models.CharField("telefone de emergência", max_length=32, blank=True)

    image_use_authorized = models.BooleanField(
        "uso de imagem autorizado",
        default=False,
        help_text="Autorização do responsável para uso de imagem conforme política da escola.",
    )

    exit_authorized = models.BooleanField(
        "saída autorizada",
        default=False,
        help_text="Indica se o aluno possui autorização registrada para saída conforme regras da escola.",
    )

    notes = models.TextField("observações", blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="criado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_students",
    )

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "aluno"
        verbose_name_plural = "alunos"
        ordering = ["full_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "registration_number"],
                name="unique_student_registration_per_school",
                condition=~models.Q(registration_number=""),
            ),
            models.UniqueConstraint(
                fields=["school", "document"],
                name="unique_student_document_per_school",
                condition=~models.Q(document=""),
            ),
        ]

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return self.preferred_name or self.full_name


class StudentGuardian(models.Model):
    student = models.ForeignKey(
        Student,
        verbose_name="aluno",
        on_delete=models.CASCADE,
        related_name="guardians",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="usuário de acesso",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_guardian_profiles",
        help_text="Usuário usado para login do responsável no PortalK12, quando houver.",
    )

    full_name = models.CharField("nome completo", max_length=180)
    relationship = models.CharField(
        "parentesco",
        max_length=30,
        choices=GuardianRelationship.choices,
        default=GuardianRelationship.LEGAL_GUARDIAN,
    )

    document = models.CharField("CPF/RG", max_length=32, blank=True)
    email = models.EmailField("e-mail", blank=True)
    phone = models.CharField("telefone", max_length=32, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=32, blank=True)

    is_primary = models.BooleanField("responsável principal", default=False)
    can_pick_up_student = models.BooleanField("autorizado a retirar o aluno", default=False)
    receives_notifications = models.BooleanField("recebe comunicados", default=True)

    notes = models.TextField("observações", blank=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "responsável do aluno"
        verbose_name_plural = "responsáveis dos alunos"
        ordering = ["-is_primary", "full_name"]

    def __str__(self):
        return f"{self.full_name} - {self.student.display_name}"


class StudentDocument(models.Model):
    student = models.ForeignKey(
        Student,
        verbose_name="aluno",
        on_delete=models.CASCADE,
        related_name="documents",
    )

    document_type = models.CharField(
        "tipo de documento",
        max_length=30,
        choices=StudentDocumentType.choices,
        default=StudentDocumentType.OTHER,
    )

    title = models.CharField("título", max_length=180)
    file = models.FileField("arquivo", upload_to="students/documents/")

    description = models.TextField("descrição", blank=True)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="enviado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_student_documents",
    )

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "documento do aluno"
        verbose_name_plural = "documentos dos alunos"
        ordering = ["student__full_name", "title"]

    def __str__(self):
        return f"{self.student.display_name} - {self.title}"