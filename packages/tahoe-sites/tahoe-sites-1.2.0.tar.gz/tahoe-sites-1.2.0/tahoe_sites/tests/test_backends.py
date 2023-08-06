"""
Tests for Backend
"""
from unittest import mock

import ddt
from django.conf import settings
from django.test import TestCase

from tahoe_sites.api import create_tahoe_site
from tahoe_sites.backends import DefaultSiteBackend, OrganizationMemberBackend
from tahoe_sites.tests.fatories import UserFactory
from tahoe_sites.tests.utils import create_organization_mapping


class MixinTestBackendBase(TestCase):
    """
    Mixin to hold test defaults
    """
    backend_class = None

    def setUp(self):
        """
        Initialization
        """
        self.dummy_password = '123123'
        self.user = UserFactory()
        self.user.set_password(self.dummy_password)
        self.user.save()
        self.request = None

    def exec_auth(self):
        """
        Execute backend_class().authenticate method

        :return: result of authenticate method
        """
        with mock.patch('crum.get_current_request', return_value=self.request):
            return self.backend_class().authenticate(  # pylint: disable=not-callable
                request=self.request,
                username=self.user.username,
                password=self.dummy_password
            )


@ddt.ddt
class TestDefaultSiteBackend(MixinTestBackendBase):
    """
    Tests for DefaultSiteBackend
    """
    backend_class = DefaultSiteBackend

    @ddt.data(
        (False, None, False),
        (False, 99, False),
        (False, settings.SITE_ID, True),
        (True, None, True),
        (True, 99, True),
        (True, settings.SITE_ID, True),
    )
    @ddt.unpack
    def test_with_user(self, is_superuser, site_id, success_expected):
        """
        Verify that the backend allows/disallows authentication correctly according to is_superuser and current site
        """
        self.user.is_superuser = is_superuser
        self.user.save()
        self.request = mock.Mock(site=mock.Mock(id=site_id))

        self.assertEqual(self.exec_auth(), self.user if success_expected else None)

    @ddt.data(None, 99, settings.SITE_ID,)
    def test_no_user(self, site_id):
        """
        Verify that the backend disallows authentication without a user
        """
        self.user.username = None
        self.dummy_password = None
        self.request = mock.Mock(site=mock.Mock(id=site_id))

        self.assertIsNone(self.exec_auth())


@ddt.ddt
class TestOrganizationMemberBackend(MixinTestBackendBase):
    """
    Tests for OrganizationMemberBackend
    """
    backend_class = OrganizationMemberBackend

    @ddt.data(
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    )
    @ddt.unpack
    def test_member_and_no_member(self, is_active, is_member):
        """
        Verify that the backend allows/disallows authentication correctly according to the user being a member of
        the organization related to the site (regardless of being active or not)
        """
        info = create_tahoe_site(domain='test.org', short_name='TO')
        self.request = mock.Mock(site=info['site'])

        self.user.is_active = is_active
        self.user.save()
        if is_member:
            create_organization_mapping(self.user, info['organization'])

        self.assertEqual(self.exec_auth(), self.user if is_member else None)

    def test_superuser(self):
        """
        Verify that the backend disallows authentication when the user is superusers
        """
        self.user.is_superuser = True
        self.user.save()
        self.request = mock.Mock(site=mock.Mock(id=99))

        self.assertIsNone(self.exec_auth())

    def test_default_site(self):
        """
        Verify that the backend disallows authentication in default site
        """
        self.request = mock.Mock(site=mock.Mock(id=settings.SITE_ID))

        self.assertIsNone(self.exec_auth())
