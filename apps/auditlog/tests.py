from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import UserRole


User = get_user_model()


class UserActivityMiddlewareTests(TestCase):
    def test_authenticated_request_updates_last_activity(self):
        user = User.objects.create_user(
            username="activity_middleware_user",
            email="activity_middleware@test.local",
            password="PortalK12Teste123",
        )
        user.profile.role = UserRole.SCHOOL_DIRECTOR
        user.profile.is_active_profile = True
        user.profile.last_activity_at = None
        user.profile.last_activity_ip = None
        user.profile.last_activity_user_agent = ""
        user.profile.save()

        self.client.force_login(user)

        response = self.client.get(
            "/app/pages/cantina/",
            HTTP_USER_AGENT="PortalK12TestClient",
        )

        self.assertEqual(response.status_code, 200)

        user.profile.refresh_from_db()

        self.assertIsNotNone(user.profile.last_activity_at)
        self.assertTrue(user.profile.last_activity_user_agent)
