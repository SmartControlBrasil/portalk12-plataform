from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class AcademicYearStatus(models.TextChoices):
    PLANNED = "PLANNED", "Planejado"
    ACTIVE = "ACTIVE", "Ativo"
    CLOSED = "CLOSED", "Encerrado"
    ARCHIVED = "ARCHIVED", "Arquivado"


class ShiftType(models.TextChoices):
    MORNING = "MORNING", "Manhã"
    AFTERNOON = "AFTERNOON", "Tarde"
    EVENING = "EVENING", "Noite"
    FULL_TIME = "FULL_TIME", "Integral"
    OTHER = "OTHER", "Outro"


class ClassStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Ativa"
    INACTIVE = "INACTIVE", "Inativa"
    CLOSED = "CLOSED", "Encerrada"


class EnrollmentStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Ativa"
    TRANSFERRED = "TRANSFERRED", "Transferido"
    CANCELLED = "CANCELLED", "Cancelado"
    COMPLETED = "COMPLETED", "Concluído"


class AcademicYear(models.Model):
    school = models.ForeignKey(
        "schools.School",
        verbose_name="escola",
        on_delete=models.CASCADE,
        related_name="academic_years",
    )

    name = models.CharField(
        "nome",
        max_length=80,
        help_text="Exemplo: Ano letivo 2026.",
    )

    year = models.PositiveSmallIntegerField("ano")

    start_date = models.DateField("data de início", null=True, blank=True)
    end_date = models.DateField("data de término", null=True, blank=True)

    status = models.CharField(
        "status",
        max_length=20,
        choices=AcademicYearStatus.choices,
        default=AcademicYearStatus.PLANNED,
    )

    is_current = models.BooleanField("ano letivo atual", default=False)

    notes = models.TextField("observações", blank=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "ano letivo"
        verbose_name_plural = "anos letivos"
        ordering = ["-year", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "year", "name"],
                name="unique_academic_year_name_per_school",
            ),
        ]

    def __str__(self):
        return f"{self.school.name} - {self.name}"


class Shift(models.Model):
    school = models.ForeignKey(
        "schools.School",
        verbose_name="escola",
        on_delete=models.CASCADE,
        related_name="shifts",
    )

    name = models.CharField(
        "nome",
        max_length=80,
        help_text="Exemplo: Manhã, Tarde, Integral.",
    )

    shift_type = models.CharField(
        "tipo de turno",
        max_length=20,
        choices=ShiftType.choices,
        default=ShiftType.OTHER,
    )

    start_time = models.TimeField("horário de início", null=True, blank=True)
    end_time = models.TimeField("horário de término", null=True, blank=True)

    is_active = models.BooleanField("ativo", default=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "turno"
        verbose_name_plural = "turnos"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "name"],
                name="unique_shift_name_per_school",
            ),
        ]

    def __str__(self):
        return f"{self.school.name} - {self.name}"


class Classroom(models.Model):
    school = models.ForeignKey(
        "schools.School",
        verbose_name="escola",
        on_delete=models.CASCADE,
        related_name="classrooms",
    )

    name = models.CharField(
        "nome da sala",
        max_length=80,
        help_text="Exemplo: Sala 01, Laboratório Maker, Sala Infantil A.",
    )

    code = models.CharField("código", max_length=40, blank=True)

    capacity = models.PositiveSmallIntegerField("capacidade", null=True, blank=True)

    location = models.CharField(
        "localização",
        max_length=120,
        blank=True,
        help_text="Exemplo: Bloco A, 2º andar.",
    )

    is_active = models.BooleanField("ativa", default=True)

    notes = models.TextField("observações", blank=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "sala de aula"
        verbose_name_plural = "salas de aula"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "name"],
                name="unique_classroom_name_per_school",
            ),
            models.UniqueConstraint(
                fields=["school", "code"],
                name="unique_classroom_code_per_school",
                condition=~models.Q(code=""),
            ),
        ]

    def __str__(self):
        return f"{self.school.name} - {self.name}"


class SchoolClass(models.Model):
    school = models.ForeignKey(
        "schools.School",
        verbose_name="escola",
        on_delete=models.CASCADE,
        related_name="classes",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        verbose_name="ano letivo",
        on_delete=models.PROTECT,
        related_name="classes",
    )

    shift = models.ForeignKey(
        Shift,
        verbose_name="turno",
        on_delete=models.PROTECT,
        related_name="classes",
    )

    classroom = models.ForeignKey(
        Classroom,
        verbose_name="sala de aula",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classes",
    )

    responsible_teacher = models.ForeignKey(
        "teachers.Teacher",
        verbose_name="professor responsável",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responsible_classes",
    )

    name = models.CharField(
        "nome da turma",
        max_length=120,
        help_text="Exemplo: 5º Ano A, Infantil II B, 1º EM Robótica.",
    )

    grade = models.CharField(
        "série/ano",
        max_length=80,
        blank=True,
        help_text="Exemplo: 5º ano, Infantil II, 1º ano EM.",
    )

    code = models.CharField("código da turma", max_length=50, blank=True)

    max_students = models.PositiveSmallIntegerField(
        "limite de alunos",
        null=True,
        blank=True,
    )

    status = models.CharField(
        "status",
        max_length=20,
        choices=ClassStatus.choices,
        default=ClassStatus.ACTIVE,
    )

    notes = models.TextField("observações", blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="criado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_school_classes",
    )

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "turma"
        verbose_name_plural = "turmas"
        ordering = ["academic_year__year", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "academic_year", "name"],
                name="unique_class_name_per_school_year",
            ),
            models.UniqueConstraint(
                fields=["school", "academic_year", "code"],
                name="unique_class_code_per_school_year",
                condition=~models.Q(code=""),
            ),
        ]

    def __str__(self):
        return f"{self.name} - {self.academic_year.year}"

    @property
    def enrolled_students_count(self):
        return self.enrollments.filter(status=EnrollmentStatus.ACTIVE).count()

    @property
    def has_capacity_limit(self):
        return self.max_students is not None

    @property
    def is_full(self):
        if not self.has_capacity_limit:
            return False

        return self.enrolled_students_count >= self.max_students


class ClassEnrollment(models.Model):
    school_class = models.ForeignKey(
        SchoolClass,
        verbose_name="turma",
        on_delete=models.CASCADE,
        related_name="enrollments",
    )

    student = models.ForeignKey(
        "students.Student",
        verbose_name="aluno",
        on_delete=models.CASCADE,
        related_name="class_enrollments",
    )

    enrollment_date = models.DateField("data de entrada", null=True, blank=True)
    exit_date = models.DateField("data de saída", null=True, blank=True)

    status = models.CharField(
        "status",
        max_length=20,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.ACTIVE,
    )

    notes = models.TextField("observações", blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="criado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_class_enrollments",
    )

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "matrícula em turma"
        verbose_name_plural = "matrículas em turmas"
        ordering = ["school_class__name", "student__full_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school_class", "student"],
                name="unique_student_per_class",
            ),
        ]

    def __str__(self):
        return f"{self.student.display_name} - {self.school_class.name}"

    @property
    def school(self):
        return self.school_class.school