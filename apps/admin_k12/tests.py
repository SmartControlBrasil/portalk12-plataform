from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import UserRole


User = get_user_model()


class AdminK12PageAccessTests(TestCase):
    def make_user(self, username, role, *, is_staff=False, is_superuser=False):
        user = User.objects.create_user(
            username=username,
            email=f"{username}@test.local",
            password="PortalK12Teste123",
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        user.profile.role = role
        user.profile.is_active_profile = True
        user.profile.save()
        return user

    def assert_page_statuses(self, user, expected_statuses):
        self.client.force_login(user)

        for url, expected_status in expected_statuses.items():
            with self.subTest(user=user.username, url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_director_can_access_school_admin_pages(self):
        user = self.make_user("director_access", UserRole.SCHOOL_DIRECTOR)

        self.assert_page_statuses(
            user,
            {
                "/app/pages/students/": 200,
                "/app/pages/add-student/": 200,
                "/app/pages/teachers/": 200,
                "/app/pages/add-teacher/": 200,
                "/app/pages/classes/": 200,
                "/app/pages/visitors/": 200,
                "/app/pages/cantina/": 200,
                "/app/pages/file-manager/": 200,
            },
        )

    def test_teacher_has_limited_access(self):
        user = self.make_user("teacher_access", UserRole.TEACHER)

        self.assert_page_statuses(
            user,
            {
                "/app/pages/students/": 200,
                "/app/pages/add-student/": 403,
                "/app/pages/teachers/": 200,
                "/app/pages/add-teacher/": 403,
                "/app/pages/classes/": 200,
                "/app/pages/visitors/": 200,
                "/app/pages/cantina/": 200,
                "/app/pages/file-manager/": 200,
            },
        )

    def test_collaborator_has_restricted_access(self):
        user = self.make_user("collaborator_access", UserRole.COLLABORATOR)

        self.assert_page_statuses(
            user,
            {
                "/app/pages/students/": 403,
                "/app/pages/add-student/": 403,
                "/app/pages/teachers/": 403,
                "/app/pages/add-teacher/": 403,
                "/app/pages/classes/": 403,
                "/app/pages/visitors/": 403,
                "/app/pages/cantina/": 200,
                "/app/pages/file-manager/": 403,
            },
        )

    def test_legacy_cafeteria_and_food_pages_are_not_allowed(self):
        user = self.make_user("director_legacy_pages", UserRole.SCHOOL_DIRECTOR)
        self.client.force_login(user)

        expected_statuses = {
            "/app/pages/cantina/": 200,
            "/app/pages/cafeteria/": 404,
            "/app/pages/food/": 404,
        }

        for url, expected_status in expected_statuses.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get("/app/pages/cantina/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/django-admin/login/", response["Location"])
