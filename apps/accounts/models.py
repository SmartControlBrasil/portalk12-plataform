from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserRole(models.TextChoices):
    SYSTEM_ADMIN = "SYSTEM_ADMIN", "Administrador do Sistema"
    SCHOOL_DIRECTOR = "SCHOOL_DIRECTOR", "Diretor da Escola"
    TEACHER = "TEACHER", "Professor"
    COLLABORATOR = "COLLABORATOR", "Colaborador"
    GUARDIAN = "GUARDIAN", "Responsável"
    STUDENT = "STUDENT", "Aluno"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="usuário",
        on_delete=models.CASCADE,
        related_name="profile",
    )

    school = models.ForeignKey(
        "schools.School",
        verbose_name="escola",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_profiles",
    )

    role = models.CharField(
        "perfil de acesso",
        max_length=32,
        choices=UserRole.choices,
        default=UserRole.COLLABORATOR,
    )

    phone = models.CharField("telefone", max_length=32, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=32, blank=True)

    job_title = models.CharField("cargo/função", max_length=120, blank=True)

    must_change_password = models.BooleanField(
        "deve trocar senha no próximo acesso",
        default=False,
    )

    is_active_profile = models.BooleanField("perfil ativo", default=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "perfil de usuário"
        verbose_name_plural = "perfis de usuários"
        ordering = ["user__first_name", "user__username"]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_role_display()}"

    @property
    def is_system_admin(self):
        return self.role == UserRole.SYSTEM_ADMIN or self.user.is_superuser

    @property
    def is_school_director(self):
        return self.role == UserRole.SCHOOL_DIRECTOR

    @property
    def is_teacher(self):
        return self.role == UserRole.TEACHER

    @property
    def is_collaborator(self):
        return self.role == UserRole.COLLABORATOR

    @property
    def can_manage_school_data(self):
        return self.is_system_admin or self.is_school_director

    @property
    def can_manage_teachers(self):
        return self.is_system_admin or self.is_school_director

    @property
    def can_manage_students(self):
        return self.is_system_admin or self.is_school_director

    @property
    def can_view_students(self):
        return self.is_system_admin or self.is_school_director or self.is_teacher

    @property
    def can_manage_visitors(self):
        return self.is_system_admin or self.is_school_director or self.is_teacher


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        return

    if hasattr(instance, "profile"):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)