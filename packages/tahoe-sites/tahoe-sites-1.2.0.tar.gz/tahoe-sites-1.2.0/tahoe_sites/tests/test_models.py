"""
Tests for models
"""
from unittest import mock

from django.contrib.sites.models import Site
from django.db.utils import IntegrityError
from django.test import TestCase
from organizations.models import Organization

from tahoe_sites.models import TahoeSite, UserOrganizationMapping
from tahoe_sites.tests.fatories import UserFactory
from tahoe_sites.tests.utils import create_organization_mapping
from tahoe_sites.zd_helpers import should_site_use_org_models


class DefaultsForTestsMixin(TestCase):
    """
    Mixin that creates some default objects
    """
    def create_organization(self, name, short_name, active=True):
        """
        helper to create an Organization object
        """
        return Organization.objects.create(
            name=name,
            description='{name} description'.format(name=name),
            active=active,
            short_name=short_name,
        )

    def create_django_site(self, domain):
        """
        helper to create a Site object
        """
        return Site.objects.create(domain=domain)

    def setUp(self) -> None:
        """
        Initialization
        """
        self.default_org = self.create_organization(
            name='test organization',
            short_name='TO'
        )
        self.default_django_site = self.create_django_site('dummy.com')
        if should_site_use_org_models():
            self.default_tahoe_site = None
            self.default_org.sites.add(self.default_django_site)
        else:
            self.default_tahoe_site = TahoeSite.objects.create(
                organization=self.default_org,
                site=self.default_django_site
            )

        self.default_user = UserFactory.create()


class TestUserOrganizationMapping(DefaultsForTestsMixin):
    """
    Tests for UserOrganizationMapping model
    """
    def test_is_user_already_mapped_false(self):
        """
        Verify that is_user_already_mapped return False if the user is not mapped to any organization yet
        """
        assert UserOrganizationMapping.objects.filter(user=self.default_user).count() == 0

        assert not UserOrganizationMapping.is_user_already_mapped(self.default_user)

    def test_is_user_already_mapped_true(self):
        """
        Verify that is_user_already_mapped return True if the user is already mapped to any organization
        """
        create_organization_mapping(user=self.default_user, organization=self.default_org)

        assert UserOrganizationMapping.objects.filter(user=self.default_user).count() == 1
        assert UserOrganizationMapping.is_user_already_mapped(self.default_user)

    def test_user_uniqueness_multiple_organizations(self):
        """
        Verify that can be mapped one once, no more
        """
        create_organization_mapping(user=self.default_user, organization=self.default_org)
        assert UserOrganizationMapping.objects.filter(user=self.default_user).count() == 1

        org2 = self.create_organization(name='organization2', short_name='O2')

        for organization in [self.default_org, org2]:
            with self.assertRaisesMessage(
                expected_exception=IntegrityError,
                expected_message='Cannot add user to organization. User already added to an organization!'
            ):
                create_organization_mapping(user=self.default_user, organization=organization)

    @mock.patch('tahoe_sites.models.UserOrganizationMapping.is_user_already_mapped', return_value=False)
    def test_save_new_record(self, mocked_method):
        """
        Verify that save method will call is_user_already_mapped to check for user uniqueness when creating new record
        """
        create_organization_mapping(user=self.default_user, organization=self.default_org)
        mocked_method.assert_called_with(user=self.default_user)

    def test_save_old_records(self):
        """
        Verify that save method will not call is_user_already_mapped when saving old records
        """
        mapping = create_organization_mapping(user=self.default_user, organization=self.default_org)

        with mock.patch('tahoe_sites.models.UserOrganizationMapping.is_user_already_mapped') as mocked_method:
            mapping.is_admin = not mapping.is_admin
            mapping.save()
        mocked_method.assert_not_called()

    def test_to_string(self):
        """
        Verify format of auto convert to string
        """
        mapping = create_organization_mapping(
            user=self.default_user,
            organization=self.default_org,
        )
        assert str(mapping) == 'UserOrganizationMapping<{email}, {short_name}>'.format(
            email=self.default_user.email,
            short_name=self.default_org.short_name,
        )
