"""
Helpers used for Zero Downtime process. This file should be removed at the end
"""
from django.conf import settings


def should_site_use_org_models():
    """
    Returns the value of TAHOE_SITES_USE_ORGS_MODELS feature flag

    :return: boolean value of TAHOE_SITES_USE_ORGS_MODELS being set or not
    """
    return settings.FEATURES.get('TAHOE_SITES_USE_ORGS_MODELS', True)


def get_meta_managed():
    """
    According to the value of TAHOE_SITES_USE_ORGS_MODELS feature flag, return <True> if the flag
    is set, otherwise return <False>

    :return: <True> if TAHOE_SITES_USE_ORGS_MODELS is set, otherwise <False>
    """
    return not should_site_use_org_models()


def get_replacement_name(old_name):
    """
    Used for database migration and declaration. Returns the given string
    only if TAHOE_SITES_USE_ORGS_MODELS flag is set

    :param old_name: replacement string
    :return: <old_name> if TAHOE_SITES_USE_ORGS_MODELS is set, otherwise <None>
    """
    return old_name if should_site_use_org_models() else None


def get_unique_together(unique_together):
    """
    Used for database migration and declaration. Returns the given field names
    only if TAHOE_SITES_USE_ORGS_MODELS is NOT set

    :param unique_together: unique_together list
    :return: <unique_together> if TAHOE_SITES_USE_ORGS_MODELS is set, otherwise <None>
    """
    return unique_together if not should_site_use_org_models() else None
