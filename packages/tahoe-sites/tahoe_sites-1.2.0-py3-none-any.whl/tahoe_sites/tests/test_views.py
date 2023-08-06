"""
Tests for v1 views
"""
from django.urls import reverse
from rest_framework.authtoken.models import Token
from organizations.serializers import OrganizationSerializer

from tahoe_sites.tests.test_models import DefaultsForTestsMixin


class TestOrganizationViewSet(DefaultsForTestsMixin):
    """
    Tests for OrganizationViewSet view
    """
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse(
            'tahoe_sites_organization-detail',
            args=[self.default_org.short_name],
        )

    def test_result_with_token(self):
        """
        Verify that the correct result is returned when a valid token is provided
        """
        self.default_user.is_staff = True
        self.default_user.save()

        token = Token.objects.create(user=self.default_user)
        headers = {
            'HTTP_AUTHORIZATION': 'Token ' + token.key,
        }
        response = self.client.get(self.url, **headers)
        assert response.status_code == 200
        assert response.data == OrganizationSerializer(self.default_org).data

    def test_result_without_token(self):
        """
        Verify that 401 is returned when a no valid token is provided
        """
        response = self.client.get(self.url)
        assert response.status_code == 401
