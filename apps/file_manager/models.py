from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class ManagedFileVisibility(models.TextChoices):
    PRIVATE = "PRIVATE", "Privado"
    SCHOOL_STAFF = "SCHOOL_STAFF", "Equipe da escola"
    TEACHERS = "TEACHERS", "Professores"
    GUARDIANS = "GUARDIANS", "Responsáveis"
    PUBLIC_SCHOOL = "PUBLIC_SCHOOL", "Público da escola"


class ManagedFileStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Ativo"
    ARCHIVED = "ARCHIVED", "Arquivado"
    DELETED = "DELETED", "Excluído"


class ManagedFileCategory(models.TextChoices):
    GENERAL = "GENERAL", "Geral"
    SCHOOL_DOCUMENT = "SCHOOL_DOCUMENT", "Documento da escola"
    STUDENT_DOCUMENT = "STUDENT_DOCUMENT", "Documento de aluno"
    TEACHER_DOCUMENT = "TEACHER_DOCUMENT", "Documento de professor"
    CLASS_MATERIAL = "CLASS_MATERIAL", "Material de aula"
    ANNOUNCEMENT = "ANNOUNCEMENT", "Comunicado"
    POLICY = "POLICY", "Política/regulamento"
    CONTRACT = "CONTRACT", "Contrato"
    IMAGE = "IMAGE", "Imagem"
    OTHER = "OTHER", "Outro"


class FileFolder(models.Model):
    school = models.ForeignKey(
        "schools.School",
        verbose_name="escola",
        on_delete=models.CASCADE,
        related_name="file_folders",
    )

    parent = models.ForeignKey(
        "self",
        verbose_name="pasta superior",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    name = models.CharField("nome", max_length=160)
    description = models.TextField("descrição", blank=True)

    visibility = models.CharField(
        "visibilidade",
        max_length=30,
        choices=ManagedFileVisibility.choices,
        default=ManagedFileVisibility.PRIVATE,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="criado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_file_folders",
    )

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "pasta de arquivos"
        verbose_name_plural = "pastas de arquivos"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "parent", "name"],
                name="unique_file_folder_name_per_parent",
            ),
        ]

    def __str__(self):
        return self.name


class ManagedFile(models.Model):
    school = models.ForeignKey(
        "schools.School",
        verbose_name="escola",
        on_delete=models.CASCADE,
        related_name="managed_files",
    )

    folder = models.ForeignKey(
        FileFolder,
        verbose_name="pasta",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="files",
    )

    title = models.CharField("título", max_length=180)

    category = models.CharField(
        "categoria",
        max_length=30,
        choices=ManagedFileCategory.choices,
        default=ManagedFileCategory.GENERAL,
    )

    file = models.FileField("arquivo", upload_to="file-manager/files/")

    description = models.TextField("descrição", blank=True)

    visibility = models.CharField(
        "visibilidade",
        max_length=30,
        choices=ManagedFileVisibility.choices,
        default=ManagedFileVisibility.PRIVATE,
    )

    status = models.CharField(
        "status",
        max_length=20,
        choices=ManagedFileStatus.choices,
        default=ManagedFileStatus.ACTIVE,
    )

    related_student = models.ForeignKey(
        "students.Student",
        verbose_name="aluno relacionado",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_files",
    )

    related_teacher = models.ForeignKey(
        "teachers.Teacher",
        verbose_name="professor relacionado",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_files",
    )

    related_class = models.ForeignKey(
        "classes.SchoolClass",
        verbose_name="turma relacionada",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_files",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="enviado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_managed_files",
    )

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "arquivo gerenciado"
        verbose_name_plural = "arquivos gerenciados"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def filename(self):
        if not self.file:
            return ""

        return self.file.name.split("/")[-1]

    @property
    def is_active(self):
        return self.status == ManagedFileStatus.ACTIVE


class FileShare(models.Model):
    file = models.ForeignKey(
        ManagedFile,
        verbose_name="arquivo",
        on_delete=models.CASCADE,
        related_name="shares",
    )

    shared_with_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="compartilhado com",
        on_delete=models.CASCADE,
        related_name="received_file_shares",
    )

    can_download = models.BooleanField("pode baixar", default=True)

    shared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="compartilhado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_file_shares",
    )

    expires_at = models.DateTimeField("expira em", null=True, blank=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "compartilhamento de arquivo"
        verbose_name_plural = "compartilhamentos de arquivos"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["file", "shared_with_user"],
                name="unique_file_share_per_user",
            ),
        ]

    def __str__(self):
        return f"{self.file.title} -> {self.shared_with_user}"