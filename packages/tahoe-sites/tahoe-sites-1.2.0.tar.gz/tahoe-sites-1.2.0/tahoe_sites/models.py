"""
Package models goes here
"""
import uuid

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.signals import pre_save
from django.db.utils import IntegrityError
from django.dispatch import receiver
from organizations.models import Organization

from tahoe_sites import zd_helpers


class UserOrganizationMapping(models.Model):
    """
    User membership in an organization.

    Tahoe's fundamental multi-site relationship.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='+')

    # TODO: Remove after production deployment
    #       https://github.com/appsembler/tahoe-sites/issues/27
    _deprecated_field_is_active = models.BooleanField(
        default=True,
        db_column='is_active',
    )

    is_admin = models.BooleanField(
        default=False,
        # TODO: Remove once we migrate off edx-organizations tables
        db_column=zd_helpers.get_replacement_name('is_amc_admin'),
    )

    class Meta:
        app_label = 'tahoe_sites'
        managed = zd_helpers.get_meta_managed()
        db_table = zd_helpers.get_replacement_name('organizations_userorganizationmapping')

    def __str__(self):
        """
        Converts the object into a string

        :return: string representation of the object
        """
        return 'UserOrganizationMapping<{email}, {organization}>'.format(
            email=self.user.email,  # pylint: disable=no-member
            organization=self.organization.short_name,
        )

    @classmethod
    def is_user_already_mapped(cls, user):
        """
        Check if the user already mapped to an organization or not (regardless of active/admin statuses)

        :param user: User to check
        :return: <True> if the user already mapped to an organization, <False> otherwise
        """
        return cls.objects.filter(user=user).exists()


@receiver(pre_save, sender=UserOrganizationMapping)
def prevent_adding_user_to_two_organizations(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """
    Prevent adding the same user to two organizations.

    TODO: Use `user = models.OneToOneField()` instead of this check.
    """
    if not instance.pk and instance.is_user_already_mapped(user=instance.user):
        raise IntegrityError('Cannot add user to organization. User already added to an organization!')


class TahoeSite(models.Model):
    """
    Handle Site UUID
    """
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
    )
    site_uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
    )

    class Meta:
        app_label = 'tahoe_sites'
