"""
Tests for admin module
"""
from django.test import TestCase

from tahoe_sites import admin


class TestAdmin(TestCase):
    """
    Tests for admin form registration
    """
    @staticmethod
    def test_admin_module():
        """
        Verify that admin registration is going fine
        """
        assert bool(admin)
