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
    last_activity_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="última atividade",
    )
    last_activity_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP da última atividade",
    )
    last_activity_user_agent = models.TextField(
        blank=True,
        verbose_name="navegador/dispositivo da última atividade",
    )


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

class AccessGroup(models.Model):
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="access_groups",
        verbose_name="escola",
    )
    name = models.CharField(
        max_length=120,
        verbose_name="nome",
    )
    description = models.TextField(
        blank=True,
        verbose_name="descrição",
    )
    is_system_default = models.BooleanField(
        default=False,
        verbose_name="grupo padrão do sistema",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="ativo",
    )
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_access_groups",
        verbose_name="criado por",
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
        verbose_name = "grupo de acesso"
        verbose_name_plural = "grupos de acesso"
        ordering = ["school", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "name"],
                name="unique_access_group_name_per_school",
            )
        ]

    def __str__(self):
        return f"{self.school} - {self.name}"


class AccessGroupPermission(models.Model):
    group = models.ForeignKey(
        AccessGroup,
        on_delete=models.CASCADE,
        related_name="permissions",
        verbose_name="grupo",
    )
    permission_code = models.CharField(
        max_length=120,
        verbose_name="código da permissão",
    )
    allowed = models.BooleanField(
        default=True,
        verbose_name="permitido",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="criado em",
    )

    class Meta:
        verbose_name = "permissão do grupo"
        verbose_name_plural = "permissões do grupo"
        ordering = ["group", "permission_code"]
        constraints = [
            models.UniqueConstraint(
                fields=["group", "permission_code"],
                name="unique_permission_code_per_access_group",
            )
        ]

    def __str__(self):
        status = "permitido" if self.allowed else "bloqueado"
        return f"{self.group} - {self.permission_code} ({status})"


class UserAccessGroup(models.Model):
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="access_group_memberships",
        verbose_name="usuário",
    )
    group = models.ForeignKey(
        AccessGroup,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name="grupo",
    )
    assigned_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_access_groups",
        verbose_name="atribuído por",
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="atribuído em",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="ativo",
    )

    class Meta:
        verbose_name = "grupo do usuário"
        verbose_name_plural = "grupos do usuário"
        ordering = ["user", "group"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "group"],
                name="unique_user_access_group",
            )
        ]

    def __str__(self):
        return f"{self.user} -> {self.group}"


class UserPermissionOverride(models.Model):
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="permission_overrides",
        verbose_name="usuário",
    )
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="user_permission_overrides",
        verbose_name="escola",
    )
    permission_code = models.CharField(
        max_length=120,
        verbose_name="código da permissão",
    )
    allowed = models.BooleanField(
        default=True,
        verbose_name="permitido",
        help_text="Use permitido=True para liberar e permitido=False para bloquear uma permissão específica.",
    )
    reason = models.TextField(
        blank=True,
        verbose_name="motivo",
    )
    assigned_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_permission_overrides",
        verbose_name="atribuído por",
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="atribuído em",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="ativo",
    )

    class Meta:
        verbose_name = "permissão individual"
        verbose_name_plural = "permissões individuais"
        ordering = ["user", "permission_code"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "school", "permission_code"],
                name="unique_user_permission_override_per_school",
            )
        ]

    def __str__(self):
        status = "permitido" if self.allowed else "bloqueado"
        return f"{self.user} - {self.permission_code} ({status})"


class AccessGroup(models.Model):
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="access_groups",
        verbose_name="escola",
    )
    name = models.CharField(
        max_length=120,
        verbose_name="nome",
    )
    description = models.TextField(
        blank=True,
        verbose_name="descrição",
    )
    is_system_default = models.BooleanField(
        default=False,
        verbose_name="grupo padrão do sistema",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="ativo",
    )
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_access_groups",
        verbose_name="criado por",
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
        verbose_name = "grupo de acesso"
        verbose_name_plural = "grupos de acesso"
        ordering = ["school", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "name"],
                name="unique_access_group_name_per_school",
            )
        ]

    def __str__(self):
        return f"{self.school} - {self.name}"


class AccessGroupPermission(models.Model):
    group = models.ForeignKey(
        AccessGroup,
        on_delete=models.CASCADE,
        related_name="permissions",
        verbose_name="grupo",
    )
    permission_code = models.CharField(
        max_length=120,
        verbose_name="código da permissão",
    )
    allowed = models.BooleanField(
        default=True,
        verbose_name="permitido",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="criado em",
    )

    class Meta:
        verbose_name = "permissão do grupo"
        verbose_name_plural = "permissões do grupo"
        ordering = ["group", "permission_code"]
        constraints = [
            models.UniqueConstraint(
                fields=["group", "permission_code"],
                name="unique_permission_code_per_access_group",
            )
        ]

    def __str__(self):
        status = "permitido" if self.allowed else "bloqueado"
        return f"{self.group} - {self.permission_code} ({status})"


class UserAccessGroup(models.Model):
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="access_group_memberships",
        verbose_name="usuário",
    )
    group = models.ForeignKey(
        AccessGroup,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name="grupo",
    )
    assigned_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_access_groups",
        verbose_name="atribuído por",
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="atribuído em",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="ativo",
    )

    class Meta:
        verbose_name = "grupo do usuário"
        verbose_name_plural = "grupos do usuário"
        ordering = ["user", "group"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "group"],
                name="unique_user_access_group",
            )
        ]

    def __str__(self):
        return f"{self.user} -> {self.group}"


class UserPermissionOverride(models.Model):
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="permission_overrides",
        verbose_name="usuário",
    )
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="user_permission_overrides",
        verbose_name="escola",
    )
    permission_code = models.CharField(
        max_length=120,
        verbose_name="código da permissão",
    )
    allowed = models.BooleanField(
        default=True,
        verbose_name="permitido",
        help_text="Use permitido=True para liberar e permitido=False para bloquear uma permissão específica.",
    )
    reason = models.TextField(
        blank=True,
        verbose_name="motivo",
    )
    assigned_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_permission_overrides",
        verbose_name="atribuído por",
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="atribuído em",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="ativo",
    )

    class Meta:
        verbose_name = "permissão individual"
        verbose_name_plural = "permissões individuais"
        ordering = ["user", "permission_code"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "school", "permission_code"],
                name="unique_user_permission_override_per_school",
            )
        ]

    def __str__(self):
        status = "permitido" if self.allowed else "bloqueado"
        return f"{self.user} - {self.permission_code} ({status})"
