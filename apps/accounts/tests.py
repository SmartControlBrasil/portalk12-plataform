from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts import permission_codes as codes
from apps.accounts.models import (
    AccessGroup,
    AccessGroupPermission,
    UserAccessGroup,
    UserPermissionOverride,
    UserRole,
)
from apps.accounts.services.permission_service import can
from apps.schools.models import School


User = get_user_model()


class PermissionServiceTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name="Escola Teste Permissões",
            slug="escola-teste-permissoes",
        )

    def make_user(self, username, role, *, is_staff=False, is_superuser=False):
        user = User.objects.create_user(
            username=username,
            email=f"{username}@test.local",
            password="PortalK12Teste123",
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        user.profile.school = self.school
        user.profile.role = role
        user.profile.is_active_profile = True
        user.profile.save()
        return user

    def test_teacher_cannot_create_student_by_default(self):
        user = self.make_user("teacher_default", UserRole.TEACHER)

        self.assertTrue(can(user, codes.STUDENTS_VIEW))
        self.assertFalse(can(user, codes.STUDENTS_CREATE))

    def test_group_permission_allows_teacher_to_create_student(self):
        user = self.make_user("teacher_group_allowed", UserRole.TEACHER)

        group = AccessGroup.objects.create(
            school=self.school,
            name="Secretaria",
            description="Grupo da secretaria",
        )
        AccessGroupPermission.objects.create(
            group=group,
            permission_code=codes.STUDENTS_CREATE,
            allowed=True,
        )
        UserAccessGroup.objects.create(
            user=user,
            group=group,
            assigned_by=user,
        )

        self.assertTrue(can(user, codes.STUDENTS_CREATE))

    def test_individual_block_overrides_group_allow(self):
        user = self.make_user("teacher_blocked", UserRole.TEACHER)

        group = AccessGroup.objects.create(
            school=self.school,
            name="Secretaria Bloqueio",
        )
        AccessGroupPermission.objects.create(
            group=group,
            permission_code=codes.STUDENTS_CREATE,
            allowed=True,
        )
        UserAccessGroup.objects.create(
            user=user,
            group=group,
            assigned_by=user,
        )
        UserPermissionOverride.objects.create(
            user=user,
            school=self.school,
            permission_code=codes.STUDENTS_CREATE,
            allowed=False,
            reason="Teste de precedência",
            assigned_by=user,
        )

        self.assertFalse(can(user, codes.STUDENTS_CREATE))

    def test_individual_allow_grants_permission_without_group(self):
        user = self.make_user("teacher_individual_allowed", UserRole.TEACHER)

        UserPermissionOverride.objects.create(
            user=user,
            school=self.school,
            permission_code=codes.STUDENTS_CREATE,
            allowed=True,
            reason="Delegação individual",
            assigned_by=user,
        )

        self.assertTrue(can(user, codes.STUDENTS_CREATE))

    def test_inactive_group_membership_does_not_grant_permission(self):
        user = self.make_user("teacher_inactive_group", UserRole.TEACHER)

        group = AccessGroup.objects.create(
            school=self.school,
            name="Secretaria Inativa",
        )
        AccessGroupPermission.objects.create(
            group=group,
            permission_code=codes.STUDENTS_CREATE,
            allowed=True,
        )
        UserAccessGroup.objects.create(
            user=user,
            group=group,
            assigned_by=user,
            is_active=False,
        )

        self.assertFalse(can(user, codes.STUDENTS_CREATE))

    def test_inactive_override_does_not_grant_permission(self):
        user = self.make_user("teacher_inactive_override", UserRole.TEACHER)

        UserPermissionOverride.objects.create(
            user=user,
            school=self.school,
            permission_code=codes.STUDENTS_CREATE,
            allowed=True,
            reason="Override inativo",
            assigned_by=user,
            is_active=False,
        )

        self.assertFalse(can(user, codes.STUDENTS_CREATE))

    def test_director_has_school_management_permissions_by_base_role(self):
        user = self.make_user("director_base", UserRole.SCHOOL_DIRECTOR)

        self.assertTrue(can(user, codes.STUDENTS_CREATE))
        self.assertTrue(can(user, codes.TEACHERS_CREATE))
        self.assertTrue(can(user, codes.SCHOOL_PERMISSIONS_MANAGE))
        self.assertTrue(can(user, codes.AUDITLOG_VIEW))

    def test_collaborator_only_has_cantina_view_by_default(self):
        user = self.make_user("collaborator_base", UserRole.COLLABORATOR)

        self.assertTrue(can(user, codes.CANTINA_VIEW))
        self.assertFalse(can(user, codes.STUDENTS_VIEW))
        self.assertFalse(can(user, codes.FILES_VIEW))

    def test_superuser_can_do_everything(self):
        user = self.make_user(
            "superuser_permissions",
            UserRole.COLLABORATOR,
            is_staff=True,
            is_superuser=True,
        )

        self.assertTrue(can(user, codes.STUDENTS_DELETE))
        self.assertTrue(can(user, codes.SCHOOL_ADMIN_GRANT))
        self.assertTrue(can(user, codes.AUDITLOG_EXPORT))
