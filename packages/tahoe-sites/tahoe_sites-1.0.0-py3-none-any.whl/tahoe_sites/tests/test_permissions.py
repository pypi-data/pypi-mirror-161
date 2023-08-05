"""
Tests for permissions
"""
from unittest import mock
import ddt
from django.test import TestCase

from tahoe_sites.permissions import IsStaffOrSuperuser
from tahoe_sites.tests.fatories import UserFactory


@ddt.ddt
class TestIsStaffOrSuperuser(TestCase):
    """
    Tests for IsStaffOrSuperUser permission
    """
    @ddt.data(
        (False, False),
        (True, False),
        (False, True),
        (True, True),
    )
    @ddt.unpack
    def test_is_user_already_mapped_false(self, is_staff, is_superuser):
        """
        Verify that IsStaffOrSuperuser returns the correct result
        """
        user = UserFactory(is_staff=is_staff, is_superuser=is_superuser)
        request = mock.Mock(user=user)
        assert IsStaffOrSuperuser().has_permission(request=request, view=mock.Mock()) == is_staff or is_superuser

    def test_must_be_active(self):
        """
        Verify that IsStaffOrSuperuser returns <False> if the user in not active
        """
        user = UserFactory(is_staff=True, is_superuser=True, is_active=False)
        request = mock.Mock(user=user)
        assert not IsStaffOrSuperuser().has_permission(request=request, view=mock.Mock())
