""" Django admin pages for organization models """
from django.contrib import admin

from tahoe_sites.models import UserOrganizationMapping


@admin.register(UserOrganizationMapping)
class UserOrganizationMappingAdmin(admin.ModelAdmin):
    """
    Many to many admin for Organization/User membership.
    """
    list_display = [
        'email',
        'username',
        'organization_name',
        'is_admin',
    ]

    search_fields = [
        'user__email',
        'user__username',
        'organization__name',
        'organization__short_name',
    ]

    list_filter = [
        'user__is_active',
        'is_admin',
    ]

    @staticmethod
    def email(mapping):
        """
        Display email

        :param mapping: UserOrganizationMapping object
        :return: email
        """
        return mapping.user.email

    @staticmethod
    def username(mapping):
        """
        Display username

        :param mapping: UserOrganizationMapping object
        :return: username
        """
        return mapping.user.username

    @staticmethod
    def organization_name(mapping):
        """
        Display organization_name

        :param mapping: UserOrganizationMapping object
        :return: short_name as organization_name
        """
        return mapping.organization.short_name
