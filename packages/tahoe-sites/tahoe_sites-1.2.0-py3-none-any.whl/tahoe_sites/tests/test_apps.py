"""
Tests TahoeSitesConfig Open edX configuration.
"""
# pylint: disable=duplicate-code
from tahoe_sites.apps import TahoeSitesConfig


def test_app_config():
    """
    Verify that the app is compatible with edx plugins
    """
    assert TahoeSitesConfig.plugin_app == {
        'url_config': {
            'lms.djangoapp': {
                'namespace': 'tahoe_sites',
                'app_name': 'tahoe_sites',
                'regex': '^tahoe-sites/',
            },
            'cms.djangoapp': {
                'namespace': 'tahoe_sites',
                'app_name': 'tahoe_sites',
                'regex': '^tahoe-sites/',
            }
        },
        'settings_config': {
            'lms.djangoapp': {
                'production': {
                    'relative_path': 'settings.common_production',
                },
            },
            'cms.djangoapp': {
                'production': {
                    'relative_path': 'settings.common_production',
                },
            },
        },
    }, 'Should initiate the app as an Open edX plugin.'
