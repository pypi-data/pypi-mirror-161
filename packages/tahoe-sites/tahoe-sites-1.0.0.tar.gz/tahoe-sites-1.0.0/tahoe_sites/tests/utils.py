"""
Utility helpers for tests
"""
from tahoe_sites.models import UserOrganizationMapping


def create_organization_mapping(user, organization, is_admin=False):
    """
    Create an UserOrganizationMapping object

    :param user: user to be mapped
    :param organization: organization to be mapped
    :param is_admin: set user as admin or not, default is False
    :return: the created UserOrganizationMapping object
    """
    return UserOrganizationMapping.objects.create(
        user=user,
        organization=organization,
        is_admin=is_admin,
    )
