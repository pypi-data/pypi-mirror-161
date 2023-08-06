"""
External Python API helpers goes here.

Those APIs should be stable and abstract internal model changes.
Non-stable APIs they should be placed in the `helpers.py` module instead.


### API Contract:

Those APIs should be stable and abstract internal model changes.
Non-stable APIs they should be placed in the `helpers.py` module instead.
### API Contract:
 * The parameters of existing functions should change in a backward compatible way:
   - No parameters should be removed from the function
   - New parameters should have safe defaults
 * For breaking changes, new functions should be created
"""
import crum
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.db.models import Q
from organizations import api as organizations_api
from organizations.models import Organization, OrganizationCourse

from tahoe_sites import zd_helpers
from tahoe_sites.models import TahoeSite, UserOrganizationMapping


def get_organization_by_uuid(organization_uuid):
    """
    Get an organization object from it's uuid

    :param organization_uuid: uuid to filter on
    :return: organization of the given uuid
    """
    if zd_helpers.should_site_use_org_models():
        return Organization.objects.get(edx_uuid=organization_uuid)
    return TahoeSite.objects.get(site_uuid=organization_uuid).organization


def get_uuid_by_organization(organization):
    """
    Get the uuid when from it's related organization

    :param organization: organization to filter on
    :return: uuid of the given organization
    """
    if zd_helpers.should_site_use_org_models():
        return organization.edx_uuid
    return TahoeSite.objects.get(organization=organization).site_uuid


def get_organization_for_user(user, fail_if_inactive=False, fail_if_site_admin=False):
    """
    Return the organization related to the given user. By default, it will return the related organization regardless
    of the user being active or not

    :param user: user to filter on
    :param fail_if_inactive: Fail if the user is inactive (default = False). If set to <True>; and exception
            will be raised when the user is inactive (Organization.DoesNotExist)
    :param fail_if_site_admin: Fail if the user is an admin on the organization (default = False)
    :return: Organization objects related to the given user
    """
    if fail_if_inactive:
        extra_params = {'user__is_active': True}
    else:
        extra_params = {}
    if fail_if_site_admin:
        extra_params['is_admin'] = False

    return Organization.objects.get(
        pk__in=UserOrganizationMapping.objects.filter(user=user, **extra_params).values('organization_id')
    )


def get_users_of_organization(organization, without_inactive_users=True, without_site_admins=False):
    """
    Return users related to the given organization. By default, all active users will be
    returned including admin users

    :param organization: organization to filter on
    :param without_inactive_users: exclude inactive users from the result (default = True)
    :param without_site_admins: exclude admin users from the result (default = False)
    :return: User objects related to the given organization
    """
    if without_inactive_users:
        extra_params = {'user__is_active': True}
    else:
        extra_params = {}
    if without_site_admins:
        extra_params['is_admin'] = False
    return get_user_model().objects.filter(
        pk__in=UserOrganizationMapping.objects.filter(organization=organization, **extra_params).values('user_id')
    )


def is_active_admin_on_organization(user, organization):
    """
    Check if the given user is an admin on the given organizations

    :param user: user to filter on
    :param organization:  organization to filter on
    :return: <True> if user is an admin on the organization, <False> otherwise
    """
    return UserOrganizationMapping.objects.filter(
        user=user,
        organization=organization,
        is_admin=True,
        user__is_active=True,
    ).exists()


def create_tahoe_site_by_link(organization, site):
    """
    Link a site to an organization. Together they are a tahoe-site

    :param organization: Organization object to be linked
    :param site: Site object to be linked
    :return: TahoeSite object
    """
    if zd_helpers.should_site_use_org_models():
        organization.sites.add(site)
        return None
    return TahoeSite.objects.create(organization=organization, site=site)


def create_tahoe_site(domain, short_name, uuid=None):
    """
    Centralized method to create the site objects in both `tahoe-sites` and `edx-organizations`.
    Other pieces like SiteConfigurations are out of the scope of this helper.

    :param domain: Site domain.
    :param short_name: Organization short name, course key component and site name.
    :param uuid: UUID string or object. Used to identify organizations and sites across Tahoe services.
    :return: dict with `site` `organization` and `uuid` fields.
    """
    organization_data = {
        'name': short_name,
        'short_name': short_name,
        'description': 'Organization of {domain} (automatic)'.format(domain=domain),
    }

    if uuid and zd_helpers.should_site_use_org_models():
        organization_data['edx_uuid'] = uuid

    organization_serialized = organizations_api.add_organization(organization_data)
    organization = Organization.objects.get(pk=organization_serialized['id'])

    site = Site.objects.create(domain=domain, name=short_name)

    if zd_helpers.should_site_use_org_models():
        returned_uuid = organization.edx_uuid
        organization.sites.add(site)
    else:
        extra = {'site_uuid': uuid} if uuid else {}
        returned_uuid = TahoeSite.objects.create(
            organization=organization,
            site=site,
            **extra,
        ).site_uuid

    return {
        'site_uuid': returned_uuid,
        'site': site,
        'organization': Organization.objects.get(pk=organization_serialized['id']),
    }


def update_admin_role_in_organization(user, organization, set_as_admin=False):
    """
    Update the user role in an organization to an admin or a learner.

    This API helper is _not_ concerned about the `is_active` status, because other
    helpers like `is_active_admin_on_organization` should take care of the `is_active` status.
    """
    # Sanity check for params to ensure we're updating a single entry at once.
    if not user:
        raise ValueError('Parameter `user` should not be None')

    if not organization:
        raise ValueError('Parameter `organization` should not be None')

    UserOrganizationMapping.objects.filter(
        user=user,
        organization=organization,
    ).update(
        is_admin=set_as_admin,
    )


def add_user_to_organization(user, organization, is_admin=False):
    """
    Add user to an organization.
    """
    UserOrganizationMapping.objects.create(
        user=user,
        organization=organization,
        is_admin=is_admin,
    )


def get_site_by_organization(organization):
    """
    Get the site by its related organization

    :param organization: Organization object to filter on
    :return: Site object related to the given organization
    """
    if zd_helpers.should_site_use_org_models():
        return organization.sites.first()
    return TahoeSite.objects.get(organization=organization).site


def get_organization_by_site(site):
    """
    Get the organization by its related site

    :param site: Site object to filter on
    :return: Organization object related to the given site
    """
    if zd_helpers.should_site_use_org_models():
        return Organization.objects.get(sites__in=[site])

    try:
        result = TahoeSite.objects.get(site=site).organization
    except TahoeSite.DoesNotExist:
        raise Organization.DoesNotExist(  # pylint: disable=raise-missing-from
            'Organization matching query does not exist'
        )
    else:
        return result


def get_site_by_uuid(site_uuid):
    """
    Get the site by its related UUID

    :param site_uuid: UUID to filter on
    :return: Site object related to the given UUID
    """
    if zd_helpers.should_site_use_org_models():
        return Organization.objects.get(edx_uuid=site_uuid).sites.get()
    return TahoeSite.objects.get(site_uuid=site_uuid).site


def get_uuid_by_site(site):
    """
    Get the site by its related UUID

    :param site: Site object to filter on
    :return: UUID related to the given site
    """
    if zd_helpers.should_site_use_org_models():
        return Organization.objects.get(sites__in=[site]).edx_uuid
    return TahoeSite.objects.get(site=site).site_uuid


def get_site_by_request(request):
    """
    Return the current site from the given request

    :param request: request to get the site from
    :return: site value in the request
    """
    return getattr(request, 'site', None)


def get_current_site():
    """
    Return the current site using crum

    :return: site value in the request
    """
    return get_site_by_request(request=crum.get_current_request())


def get_current_organization(request):
    """
    Return a single organization for the current site.

    :param request:
    :raise Site.DoesNotExist when the site isn't found.
    :raise Organization.DoesNotExist when the organization isn't found.
    :raise Organization.MultipleObjectsReturned when more than one organization is returned.
    :return Organization.
    """
    current_site = get_site_by_request(request)

    if is_main_site(get_site_by_request(request)):
        raise Organization.DoesNotExist('Tahoe Sites: Should not find organization of main site `settings.SITE_ID`')

    return get_organization_by_site(current_site)


def is_main_site(site):
    """
    Returns True if the given site is the default one. Returns False otherwise

    :param site: site to check
    :return: boolean, check result
    """
    main_site_id = getattr(settings, 'SITE_ID', None)
    return main_site_id and site and site.id == main_site_id


def get_organization_by_course(course_id):
    """
    Get the organization related to the given course. This method raises an error if the course is linked to
    many organizations

    :param course_id: course to get the organization for it
    :return: the related organization
    """
    return Organization.objects.filter(
        pk__in=OrganizationCourse.objects.filter(
            course_id=str(course_id),
            active=True,
        ).values_list('organization_id', flat=True)
    ).get()


def get_organization_user_by_email(email, organization, fail_if_inactive=False):
    """
    Get the user owning the given email address in the given organization. With an option to return None if
    the user is inactive

    :param email: user's email to search for
    :param organization: organization to filter on
    :param fail_if_inactive: when <True>; the method will fail if the user is inactive. (default is False)
    :return: user object
    """
    if fail_if_inactive:
        extra_params = {'user__is_active': True}
    else:
        extra_params = {}

    return get_user_model().objects.get(
        pk__in=UserOrganizationMapping.objects.filter(organization=organization, **extra_params).values('user_id'),
        email=email,
    )


def get_organization_user_by_username_or_email(username_or_email, organization, fail_if_inactive=False):
    """
    Get the user owning the given email address in the given organization. With an option to return None if
    the user is inactive

    :param username_or_email: user's username or email to search for
    :param organization: organization to filter on
    :param fail_if_inactive: when <True>; the method will fail if the user is inactive. (default is False)
    :return: user object
    """
    if fail_if_inactive:
        extra_params = {'user__is_active': True}
    else:
        extra_params = {}

    return get_user_model().objects.get(
        Q(email=username_or_email) | Q(username=username_or_email),
        pk__in=UserOrganizationMapping.objects.filter(organization=organization, **extra_params).values('user_id'),
    )


def is_exist_organization_user_by_email(email, organization, must_be_active=False):
    """
    Check if the user owning the given email address in the given organization exists or Not

    :param email: user's email to search for
    :param organization: organization to filter on
    :param must_be_active: when <True>; the method will return (False) if the user is inactive. (default is False)
    :return: boolean
    """
    try:
        user = get_organization_user_by_email(email=email, organization=organization, fail_if_inactive=must_be_active)
    except get_user_model().DoesNotExist:
        user = None
    return user is not None


def deprecated_is_existing_email_but_not_linked_yet(email):
    """
    TODO: This method os a temporary one; to be removed after integrating IDP with Studio
    Check if the given email is related to an existing user but not linked to any site yet

    :param email: user's email to filter on
    :return: boolean
    """
    return get_user_model().objects.filter(
        email=email,
    ).exclude(
        pk__in=UserOrganizationMapping.objects.filter().values('user_id'),
    ).exists()


def deprecated_get_admin_users_queryset_by_email(email):
    """
    TODO: This method os a temporary one; to be removed after integrating IDP with Studio
    Get a queryset of users where the given email represents an admin, regardless of being active or not

    :param email: user's email to filter on
    :return: users queryset
    """
    return get_user_model().objects.filter(
        id__in=UserOrganizationMapping.objects.filter(
            user__email=email,
            is_admin=True
        ).values_list('user_id', flat=True)
    )
