"""
Tests for zd_helper methods
"""
import pytest
from django.conf import settings
from django.test import SimpleTestCase

from tahoe_sites import zd_helpers


@pytest.mark.skipif(not settings.FEATURES['TAHOE_SITES_USE_ORGS_MODELS'],
                    reason='Runs only when TAHOE_SITES_USE_ORGS_MODELS is on')
class TestZDHelpersWithOrgs(SimpleTestCase):
    """
    Test ZDHelpers when TAHOE_SITES_USE_ORGS_MODELS flag is On
    """

    @staticmethod
    def test_should_site_use_org_models():
        """
        Test should_site_use_org_models
        """
        assert zd_helpers.should_site_use_org_models()

    @staticmethod
    def test_get_meta_managed():
        """
        Test get_meta_managed
        """
        assert not zd_helpers.get_meta_managed()

    @staticmethod
    def test_get_replacement_name():
        """
        Test get_replacement_name
        """
        assert zd_helpers.get_replacement_name('old_name') == 'old_name'

    @staticmethod
    def test_get_unique_together():
        """
        Test get_unique_together
        """
        assert zd_helpers.get_unique_together(('f1', 'f2')) is None


@pytest.mark.skipif(settings.FEATURES['TAHOE_SITES_USE_ORGS_MODELS'],
                    reason='Runs only when TAHOE_SITES_USE_ORGS_MODELS is off')
class TestZDHelpersWithoutOrgs(SimpleTestCase):
    """
    Test ZDHelpers when TAHOE_SITES_USE_ORGS_MODELS flag is On
    """
    @staticmethod
    def test_should_site_use_org_models():
        """
        Test should_site_use_org_models
        """
        assert not zd_helpers.should_site_use_org_models()

    @staticmethod
    def test_get_meta_managed():
        """
        Test get_meta_managed
        """
        assert zd_helpers.get_meta_managed()

    @staticmethod
    def test_get_replacement_name():
        """
        Test get_replacement_name
        """
        assert zd_helpers.get_replacement_name('old_name') is None

    @staticmethod
    def test_get_unique_together():
        """
        Test get_unique_together
        """
        assert zd_helpers.get_unique_together(('f1', 'f2')) == ('f1', 'f2')
