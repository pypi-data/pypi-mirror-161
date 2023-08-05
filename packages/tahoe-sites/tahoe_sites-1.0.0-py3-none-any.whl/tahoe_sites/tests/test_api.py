"""
Tests for APIs
"""
# pylint: disable=too-many-public-methods

import uuid
from unittest import mock

import ddt
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import MultipleObjectsReturned
from organizations.models import Organization, OrganizationCourse

from tahoe_sites import api
from tahoe_sites.models import TahoeSite, UserOrganizationMapping
from tahoe_sites.tests.fatories import UserFactory
from tahoe_sites.tests.test_models import DefaultsForTestsMixin
from tahoe_sites.tests.utils import create_organization_mapping


@ddt.ddt
class TestAPIHelpers(DefaultsForTestsMixin):
    """
    Tests for API helpers
    """
    def setUp(self):
        super().setUp()
        self.org1 = None
        self.org2 = None
        self.mapping = None
        self.org2_first_user = None
        self.org2_second_user = None

    def _prepare_mapping_data(self):
        """
        mapping:
            default_org --> default_user
            Org1        --> None
            Org2        --> org2_first_user  -----> self.mapping points here
            Org2        --> org2_second_user
        """
        self.org1 = self.create_organization(name='Org1', short_name='O1')
        self.org2 = self.create_organization(name='Org2', short_name='O2')
        self.org2_first_user = UserFactory.create()
        self.org2_second_user = UserFactory.create()

        create_organization_mapping(user=self.default_user, organization=self.default_org)
        self.mapping = create_organization_mapping(user=self.org2_first_user, organization=self.org2)
        create_organization_mapping(user=self.org2_second_user, organization=self.org2)

        # We have three organizations
        assert Organization.objects.count() == 3

    @pytest.mark.skipif(settings.FEATURES['TAHOE_SITES_USE_ORGS_MODELS'],
                        reason='Runs only when TAHOE_SITES_USE_ORGS_MODELS is off')
    def test_get_organization_by_uuid_without_org(self):
        """
        Test get_organization_by_uuid helper when edx-organizations customization is off
        """
        assert api.get_organization_by_uuid(self.default_tahoe_site.site_uuid) == self.default_org

    @pytest.mark.skipif(settings.FEATURES['TAHOE_SITES_USE_ORGS_MODELS'],
                        reason='Runs only when TAHOE_SITES_USE_ORGS_MODELS is off')
    def test_get_uuid_by_organization_without_org(self):
        """
        Test get_uuid_by_organization helper when edx-organizations customization is off
        """
        assert api.get_uuid_by_organization(self.default_org) == self.default_tahoe_site.site_uuid

    @pytest.mark.skipif(not settings.FEATURES['TAHOE_SITES_USE_ORGS_MODELS'],
                        reason='Runs only when TAHOE_SITES_USE_ORGS_MODELS is on')
    def test_get_organization_by_uuid_with_org(self):
        """
        Test get_organization_by_uuid helper when edx-organizations customization is on
        """
        assert api.get_organization_by_uuid(self.default_org.edx_uuid) == self.default_org

    @pytest.mark.skipif(not settings.FEATURES['TAHOE_SITES_USE_ORGS_MODELS'],
                        reason='Runs only when TAHOE_SITES_USE_ORGS_MODELS is on')
    def test_get_uuid_by_organization_with_org(self):
        """
        Test get_uuid_by_organization helper when edx-organizations customization is on
        """
        assert api.get_uuid_by_organization(self.default_org) == self.default_org.edx_uuid

    def test_get_organization_for_user_only_active_users(self):
        """
        Verify that get_organization_for_user helper returns only related to active user
        """
        self._prepare_mapping_data()

        # default_user is mapped to default_org
        assert api.get_organization_for_user(self.default_user) == self.default_org

        # org2_first_user is mapped to org2
        assert api.get_organization_for_user(self.org2_first_user) == self.org2

        # records with inactive user will not be returned
        self.org2_first_user.is_active = False
        self.org2_first_user.save()
        with self.assertRaises(expected_exception=Organization.DoesNotExist):
            api.get_organization_for_user(self.org2_first_user, fail_if_inactive=True)

    def test_get_organization_for_user_default(self):
        """
        Verify that get_organization_for_user helper returns the organization related to a user
        regardless of the user being active or not
        """
        self._prepare_mapping_data()

        self.default_user.is_active = False
        self.default_user.save()
        assert api.get_organization_for_user(self.default_user) == self.default_org

    def test_get_organization_for_user_without_admins(self):
        """
        Verify that get_organization_for_user helper can return all organization related to a user
        excluding organizations having that user as an admin
        """
        self._prepare_mapping_data()

        self.mapping.is_admin = True
        self.mapping.save()
        with self.assertRaises(expected_exception=Organization.DoesNotExist):
            api.get_organization_for_user(self.org2_first_user, fail_if_site_admin=True)

    def test_get_users_of_organization(self):
        """
        Verify that get_users_of_organization returns all active users related to an organization
        """
        self._prepare_mapping_data()

        # default_org is mapped to default_user
        assert list(api.get_users_of_organization(self.default_org)) == [self.default_user]

        # Org2 is mapped to two users
        assert list(api.get_users_of_organization(self.org2)) == [self.org2_first_user, self.org2_second_user]

        # inactive users will not be returned
        self.org2_first_user.is_active = False
        self.org2_first_user.save()
        assert list(api.get_users_of_organization(self.org2)) == [self.org2_second_user]

    def test_get_users_of_organization_with_inactive_users(self):
        """
        Verify that get_users_of_organization helper can return all user related to an organization
        including deactivated users
        """
        self._prepare_mapping_data()

        self.org2_first_user.is_active = False
        self.org2_first_user.save()
        assert list(api.get_users_of_organization(self.org2, without_inactive_users=False)) == [
            self.org2_first_user,
            self.org2_second_user
        ]

    def test_get_users_of_organization_without_admins(self):
        """
        Verify that get_users_of_organization helper can return all user related to an organization
        excluding admin users
        """
        self._prepare_mapping_data()

        self.mapping.is_admin = True
        self.mapping.save()
        assert list(api.get_users_of_organization(self.org2, without_site_admins=True)) == [self.org2_second_user]

    def test_is_active_admin_on_organization(self):
        """
        Verify that is_active_admin_on_organization helper returns True if the given user
        is an admin on the given organization
        """
        self._prepare_mapping_data()

        assert not api.is_active_admin_on_organization(user=self.org2_first_user, organization=self.org2)

        self.mapping.is_admin = True
        self.mapping.save()
        assert api.is_active_admin_on_organization(user=self.org2_first_user, organization=self.org2)

    @pytest.mark.skipif(not settings.FEATURES['TAHOE_SITES_USE_ORGS_MODELS'],
                        reason='Runs only when TAHOE_SITES_USE_ORGS_MODELS is on')
    def test_create_tahoe_site_by_link_with_org(self):
        """
        Verify that create_tahoe_site_by_link creates a TahoeSite with the given organization and site
        when edx-organizations customization is on
        """
        org = self.create_organization('dummy', 'DO')
        site = self.create_django_site('dummy.org')
        count = TahoeSite.objects.count()
        assert org.sites.count() == 0

        tahoe_site = api.create_tahoe_site_by_link(organization=org, site=site)
        assert tahoe_site is None
        assert TahoeSite.objects.count() == count
        assert org.sites.count() == 1
        assert org.sites.first() == site

    @pytest.mark.skipif(settings.FEATURES['TAHOE_SITES_USE_ORGS_MODELS'],
                        reason='Runs only when TAHOE_SITES_USE_ORGS_MODELS is off')
    def test_create_tahoe_site_by_link_without_org(self):
        """
        Verify that create_tahoe_site_by_link creates a TahoeSite with the given organization and site
        when edx-organizations customization is off
        """
        org = self.create_organization('dummy', 'DO')
        site = self.create_django_site('dummy.org')
        count = TahoeSite.objects.count()

        tahoe_site = api.create_tahoe_site_by_link(organization=org, site=site)
        assert TahoeSite.objects.count() == count + 1
        assert tahoe_site.organization == org
        assert tahoe_site.site == site

    @pytest.mark.skipif(not settings.FEATURES['TAHOE_SITES_USE_ORGS_MODELS'],
                        reason='Runs only when TAHOE_SITES_USE_ORGS_MODELS is on')
    @ddt.data(uuid.uuid4(), None)
    def test_create_tahoe_site_with_org(self, given_uuid):
        """
        Verify that create_tahoe_site creates a TahoeSite with the given organization/site information
        when edx-organizations customization is on
        """
        organization_count = Organization.objects.count()
        site_count = Site.objects.count()

        data = api.create_tahoe_site(domain='dummydomain.org', short_name='DDOMAIN', uuid=given_uuid)
        assert Organization.objects.count() == organization_count + 1
        assert Site.objects.count() == site_count + 1

        site = Site.objects.get(domain='dummydomain.org')
        organization = Organization.objects.get(short_name='DDOMAIN')
        self.assertDictEqual(data, {
            'site_uuid': given_uuid if given_uuid else organization.edx_uuid,
            'site': site,
            'organization': organization,
        })

        assert organization.sites.get() == site
        assert organization.name == 'DDOMAIN'
        assert organization.description == 'Organization of dummydomain.org (automatic)'

    @pytest.mark.skipif(settings.FEATURES['TAHOE_SITES_USE_ORGS_MODELS'],
                        reason='Runs only when TAHOE_SITES_USE_ORGS_MODELS is off')
    @ddt.data(uuid.uuid4(), None)
    def test_create_tahoe_site_without_org(self, given_uuid):
        """
        Verify that create_tahoe_site creates a TahoeSite with the given organization/site information
        when edx-organizations customization is off
        """
        tahoe_site_count = TahoeSite.objects.count()
        organization_count = Organization.objects.count()
        site_count = Site.objects.count()

        data = api.create_tahoe_site(domain='dummydomain.org', short_name='DDOMAIN', uuid=given_uuid)
        assert TahoeSite.objects.count() == tahoe_site_count + 1
        assert Organization.objects.count() == organization_count + 1
        assert Site.objects.count() == site_count + 1

        tahoe_site = TahoeSite.objects.get(organization__short_name='DDOMAIN')
        self.assertDictEqual(data, {
            'site_uuid': given_uuid if given_uuid else tahoe_site.site_uuid,
            'site': tahoe_site.site,
            'organization': tahoe_site.organization,
        })

        assert tahoe_site.organization.name == 'DDOMAIN'
        assert tahoe_site.organization.description == 'Organization of dummydomain.org (automatic)'

    def test_get_site_by_organization(self):
        """
        Verify that get_site_by_organization returns the related Organization of the given Site
        """
        assert api.get_site_by_organization(organization=self.default_org) == self.default_django_site

    def test_get_organization_by_site(self):
        """
        Verify that get_organization_by_site returns the related Site of the given Organization
        """
        assert api.get_organization_by_site(site=self.default_django_site) == self.default_org

    def test_get_organization_by_site_exception(self):
        """
        When a site is not linked with any organization; an Organization.DoesNotExist exception should
        be raised rather that TahoeSite.DoesNotExist
        """
        dummy_site = Site.objects.create(domain='dummy.org')
        with self.assertRaisesMessage(
            expected_exception=Organization.DoesNotExist,
            expected_message='Organization matching query does not exist'
        ):
            api.get_organization_by_site(site=dummy_site)

    def test_get_site_by_uuid(self):
        """
        Verify that get_site_by_uuid returns the related Site of the given UUID
        """
        assert api.get_site_by_uuid(
            site_uuid=api.get_uuid_by_organization(self.default_org)
        ) == self.default_django_site

    def test_get_uuid_by_site(self):
        """
        Verify that get_uuid_by_site returns the related UUID of the given Site
        """
        assert api.get_uuid_by_site(site=self.default_django_site) == api.get_uuid_by_organization(self.default_org)

    def test_get_current_site_use_crum(self):
        """
        Verify that get_current_site will use crum to get current request
        """
        with mock.patch(
            'tahoe_sites.api.crum.get_current_request',
            return_value=mock.Mock(site={'domain': 'test.org'})
        ) as mocked_current_request:
            self.assertEqual(api.get_current_site(), {'domain': 'test.org'})

        mocked_current_request.assert_called_with()

    def test_get_current_site_no_request_found(self):
        """
        Verify that get_current_site will return None if crum.get_current_request returns None for any reason!
        """
        with mock.patch('tahoe_sites.api.crum.get_current_request', return_value=None) as mocked_current_request:
            self.assertIsNone(api.get_current_site())

        mocked_current_request.assert_called_with()

    def test_get_site_by_request_none_request(self):
        """
        Verify that get_site_by_request will return None when the given request is None
        """
        self.assertIsNone(api.get_site_by_request(request=None))

    def test_get_site_by_request_no_site(self):
        """
        Verify that get_site_by_request will return None when no site found in the request
        """
        request = mock.Mock(site=None)
        self.assertIsNone(api.get_site_by_request(request))

    def test_get_site_by_request_with_site(self):
        """
        Verify that get_site_by_request will return the site in the request
        """
        request = mock.Mock(site={'domain': 'test.org'})
        self.assertIsNotNone(api.get_site_by_request(request))

    def test_update_admin_role_active_mapping(self):
        """
        Test update_admin_role_in_organization on active UserOrganizationMapping.
        """
        self._prepare_mapping_data()
        mapping = self.mapping
        mapping.is_admin = False
        mapping.save()

        user = mapping.user
        organization = mapping.organization

        # Set as admin.
        api.update_admin_role_in_organization(user, organization, set_as_admin=True)
        assert api.is_active_admin_on_organization(user, organization), 'Should set as admin'

        # Set as admin one more time. Shouldn't fail and should keep the user as admin.
        api.update_admin_role_in_organization(user, organization, set_as_admin=True)
        assert api.is_active_admin_on_organization(user, organization), 'Should keep the user as admin'

        # Set as non-admin.
        api.update_admin_role_in_organization(user, organization, set_as_admin=False)
        assert not api.is_active_admin_on_organization(user, organization), 'Should remove admin status'

    def test_update_admin_role_inactive_mapping(self):
        """
        Test update_admin_role_in_organization on inactive UserOrganizationMapping.
        """
        self._prepare_mapping_data()

        user = self.mapping.user
        user.is_active = False
        user.save()
        organization = self.mapping.organization

        # Set as admin, but for inactive.
        api.update_admin_role_in_organization(user, organization, set_as_admin=True)
        assert not api.is_active_admin_on_organization(user, organization), (
            'Should not be active admin, because the user is admin but is_active=False'
        )

    def test_update_admin_role_null_parameters(self):
        """
        Test update_admin_role_in_organization when having None parameters.
        """
        with pytest.raises(ValueError, match='Parameter `user` should not be None'):
            api.update_admin_role_in_organization(user=None, organization=object())

        with pytest.raises(ValueError, match='Parameter `organization` should not be None'):
            api.update_admin_role_in_organization(user=object(), organization=None)

    @mock.patch('tahoe_sites.api.get_organization_by_site')
    def test_get_current_organization(self, mock_get_organization_by_site):
        """
        Verify that get_current_organization calls get_organization_by_site to return the current site
        """
        site = Site.objects.create(domain='test.org')
        api.get_current_organization(request=mock.Mock(site=site))

        mock_get_organization_by_site.assert_called_with(site)

    def test_get_current_organization_main_site(self):
        """
        Verify that get_current_organization raises an exception if main-site is the current site
        """
        site = Site.objects.create(domain='test.org')
        with mock.patch.object(settings, 'SITE_ID', site.id):
            with self.assertRaisesMessage(
                expected_exception=Organization.DoesNotExist,
                expected_message='Tahoe Sites: Should not find organization of main site `settings.SITE_ID`'
            ):
                api.get_current_organization(request=mock.Mock(site=site))

    @ddt.data(True, False)
    def test_add_user_to_organization(self, is_admin):
        """
        Verify that add_user_to_organization maps the user to the organization with the given admin status
        """
        assert UserOrganizationMapping.objects.count() == 0

        api.add_user_to_organization(user=self.default_user, organization=self.default_org, is_admin=is_admin)
        assert UserOrganizationMapping.objects.count() == 1
        mapping = UserOrganizationMapping.objects.get()
        assert mapping.user == self.default_user
        assert mapping.organization == self.default_org
        assert mapping.is_admin == is_admin

    @ddt.data(
        (settings.SITE_ID, True),
        (settings.SITE_ID + 1, False),
        (None, False),
    )
    @ddt.unpack
    def test_is_main_site(self, site_id, expected_result):
        """
        Verify that is_main_site works correctly
        """
        self.assertEqual(api.is_main_site(site=mock.Mock(id=site_id)), expected_result)

    def test_is_main_site_none(self):
        """
        Verify that is_main_site returns False if the given site is None
        """
        self.assertFalse(api.is_main_site(site=None))

    def test_is_main_site_settings_is_none(self):
        """
        Verify that is_main_site returns False if settings.SITE_ID is None
        """
        with mock.patch.object(settings, 'SITE_ID', None):
            self.assertFalse(api.is_main_site(site=mock.Mock(id=99)))

    @staticmethod
    def add_organization_course(organization, course_id='dummy_key', active=True):
        """
        Helper to create an OrganizationCourse object
        """
        return OrganizationCourse.objects.create(
            course_id=course_id,
            organization=organization,
            active=active,
        )

    def test_get_organization_by_course(self):
        """
        Verify that get_organization_by_course returns the related organization of the given course
        """
        self.add_organization_course(organization=self.default_org)

        assert api.get_organization_by_course(course_id='dummy_key') == self.default_org

    def test_get_organization_by_course_inactive_link(self):
        """
        Verify that get_organization_by_course raises an exception if the course link is inactive
        """
        self.add_organization_course(organization=self.default_org, active=False)

        with self.assertRaises(expected_exception=Organization.DoesNotExist):
            api.get_organization_by_course(course_id='dummy_key')

    def test_get_organization_by_course_bad_course(self):
        """
        Verify that get_organization_by_course raises an exception if the course is not related to any organization
        (or maybe the course doesn't exist)
        """
        with self.assertRaises(expected_exception=Organization.DoesNotExist):
            api.get_organization_by_course(course_id='dummy_key')

    def test_get_organization_by_course_multi_organization(self):
        """
        Verify that get_organization_by_course raises an exception if the course is related to many organizations
        """
        second_org = self.create_organization(name='second_org', short_name='O2')
        self.add_organization_course(organization=self.default_org)
        self.add_organization_course(organization=second_org)

        with self.assertRaises(expected_exception=MultipleObjectsReturned):
            api.get_organization_by_course(course_id='dummy_key')

    def test_get_organization_by_course_only_one_active(self):
        """
        Verify that get_organization_by_course allows having multiple organization-course links if only one of them
        is active
        """
        second_org = self.create_organization(name='second_org', short_name='O2')
        third_org = self.create_organization(name='third_org', short_name='O3')

        self.add_organization_course(organization=second_org, active=False)
        self.add_organization_course(organization=third_org, active=False)
        self.add_organization_course(organization=self.default_org)

        assert api.get_organization_by_course(course_id='dummy_key') == self.default_org

    @ddt.data(True, False)
    def test_get_organization_user_by_email(self, user_is_active):
        """
        Verify that get_organization_user_by_email returns the correct user
        """
        self._prepare_mapping_data()
        self.default_user.is_active = user_is_active
        self.default_user.save()
        email = self.default_user.email

        # The email is related to default_org
        assert api.get_organization_user_by_email(email=email, organization=self.default_org) == self.default_user
        with pytest.raises(get_user_model().DoesNotExist):
            api.get_organization_user_by_email(email=email, organization=self.org2)

    def test_get_organization_user_by_email_no_inactive(self):
        """
        Verify that get_organization_user_by_email returns None if the user is inactive and none_if_inactive is set
        """
        self._prepare_mapping_data()
        self.default_user.is_active = False
        self.default_user.save()

        with pytest.raises(get_user_model().DoesNotExist):
            api.get_organization_user_by_email(
                email=self.default_user.email,
                organization=self.default_org,
                fail_if_inactive=True,
            )

    @ddt.data(True, False)
    def test_get_organization_user_by_username_or_email(self, user_is_active):
        """
        Verify that get_organization_user_by_username_or_email returns the correct user
        """
        self._prepare_mapping_data()
        self.default_user.is_active = user_is_active
        self.default_user.save()
        email = self.default_user.email
        username = self.default_user.username

        # The email is related to default_org
        assert api.get_organization_user_by_username_or_email(
            username_or_email=email,
            organization=self.default_org
        ) == self.default_user
        assert api.get_organization_user_by_username_or_email(
            username_or_email=username,
            organization=self.default_org
        ) == self.default_user

        with pytest.raises(get_user_model().DoesNotExist):
            api.get_organization_user_by_username_or_email(username_or_email=email, organization=self.org2)
        with pytest.raises(get_user_model().DoesNotExist):
            api.get_organization_user_by_username_or_email(username_or_email=username, organization=self.org2)

    def test_get_organization_user_by_username_or_email_no_inactive(self):
        """
        Verify that get_organization_user_by_username_or_email returns None if the user is inactive
        and none_if_inactive is set
        """
        self._prepare_mapping_data()
        self.default_user.is_active = False
        self.default_user.save()

        with pytest.raises(get_user_model().DoesNotExist):
            api.get_organization_user_by_username_or_email(
                username_or_email=self.default_user.email,
                organization=self.default_org,
                fail_if_inactive=True,
            )
        with pytest.raises(get_user_model().DoesNotExist):
            api.get_organization_user_by_username_or_email(
                username_or_email=self.default_user.username,
                organization=self.default_org,
                fail_if_inactive=True,
            )

    def test_is_exist_organization_user_by_email_exist(self):
        """
        Verify that is_exist_organization_user_by_email returns True if the email is in the organization
        """
        with mock.patch('tahoe_sites.api.get_organization_user_by_email', return_value=self.default_user):
            assert api.is_exist_organization_user_by_email(email='some_email', organization=mock.Mock())

    def test_is_exist_organization_user_by_email_not_exist(self):
        """
        Verify that is_exist_organization_user_by_email returns False if the email is in not the organization
        """
        with mock.patch('tahoe_sites.api.get_organization_user_by_email', side_effect=get_user_model().DoesNotExist):
            assert not api.is_exist_organization_user_by_email(email='some_email', organization=mock.Mock())

    @ddt.data(True, False)
    def test_deprecated_get_admin_users_queryset_by_email(self, is_active):
        """
        Verify that deprecated_get_admin_users_queryset_by_email returns the correct queryset
        """
        self.default_user.is_active = is_active
        self.default_user.save()

        # A new user with the same email address of self.default_user
        email = self.default_user.email
        user_same_email = UserFactory.create(email=email)

        mapping1 = create_organization_mapping(user=self.default_user, organization=self.default_org)
        mapping2 = create_organization_mapping(user=user_same_email, organization=self.default_org)

        mapping1.is_admin = True
        mapping1.save()
        assert list(api.deprecated_get_admin_users_queryset_by_email(email=email)) == [self.default_user]

        mapping2.is_admin = True
        mapping2.save()
        assert list(api.deprecated_get_admin_users_queryset_by_email(email=email)) == [
            self.default_user, user_same_email
        ]

    @ddt.data(True)
    def test_deprecated_is_existing_email_but_not_linked_yet(self, is_active):
        """
        Verify that deprecated_is_existing_email_but_not_linked_yet returns the correct result
        """
        email = 'testing.email.for.deprecated.method@example.com'
        assert not api.deprecated_is_existing_email_but_not_linked_yet(email=email)

        user = UserFactory.create(email=email)
        user.is_active = is_active
        user.save()
        assert api.deprecated_is_existing_email_but_not_linked_yet(email=email)

        create_organization_mapping(user=user, organization=self.default_org)
        assert not api.deprecated_is_existing_email_but_not_linked_yet(email=email)
