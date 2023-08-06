"""
App configuration model
"""
from django.apps import AppConfig


class TahoeSitesConfig(AppConfig):
    """
    Configuration model
    """
    name = 'tahoe_sites'

    plugin_app = {
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
    }
