"""
Authentication backends for Tahoe's multi-tenancy.
"""
from django.contrib.auth.backends import AllowAllUsersModelBackend, ModelBackend
from organizations.models import Organization

from tahoe_sites.api import is_main_site, get_current_site, get_organization_by_site, get_organization_for_user


class DefaultSiteBackend(ModelBackend):
    """
    User can log in to the default/root site (edx.appsembler.com) because it is required during the signup.
    Also, superusers (appsembler admins) can log into any site.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate superusers only.
        """
        user = super().authenticate(request, username, password, **kwargs)

        if user:
            if user.is_superuser or is_main_site(get_current_site()):
                return user
        return None


class OrganizationMemberBackend(AllowAllUsersModelBackend):
    """Backend for organization based authentication

    This class is an extension of Django's `AllowAllUserModelBackend`

    This class checks that the user to authenticate belongs to one of the
    organizations in the specified site

    This class extends `AllowAllUserModelBackend` instead of `ModelBackend`
    because users need to be able to authenticate when the `user.is_active` is
    `False`. The reason for this is that Open edX has an email verification
    scheme that uses `User.is_active` in order to prevent user activity until
    the users have verified their email. Effectively, edx-platform LMS user
    authentication state is used to manage authorization state.

    The key problem is that Django's `django.contrib.auth.backends.ModelBackend`
    is called with `not user.is_active` and Ironwood introduced a check to test
    authentication on a not yet authorized user. This breaks Tahoe multisite
    behavior. Extending `AllowAllUsersModelBackend` restores correct behavior.

    For further reference, see settings files and read Django documentation for
    `AUTHENTICATION_BACKENDS`
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate organization learners.
        """
        user = super().authenticate(request, username, password, **kwargs)

        result = None
        site = get_current_site()
        if not is_main_site(site) and user and not user.is_superuser:
            try:
                # `get_organization_for_user` never return `None` but raises DoesNotExist if no organization is found
                user_organization = get_organization_for_user(user=user)
                if get_organization_by_site(site=site) == user_organization:
                    result = user
            except Organization.DoesNotExist:
                # Don't fail if the user is not a member. Just prevent authentication
                pass

        return result
