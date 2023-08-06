import sys
import yaml

import django
from django.conf import settings as django_settings
from djangoldp.conf.ldpsettings import LDPSettings
from djangoldp.tests.server_settings import yaml_config

# this is where we configure the server settings that we will run our tests with
config = {
    # add the packages to the reference list
    'ldppackages': ['modeltranslation', 'djangoldp_circle', 'djangoldp_project', 'djangoldp_conversation', 'djangoldp_community',
                    'djangoldp_skill', 'djangoldp_joboffer', 'djangoldp_community.tests'],

    # required values for server
    'server': {
        'AUTH_USER_MODEL': 'tests.User',
        'REST_FRAMEWORK': {
            'DEFAULT_PAGINATION_CLASS': 'djangoldp.pagination.LDPPagination',
            'PAGE_SIZE': 5
        },
        # map the config of the core settings (avoid asserts to fail)
        'SITE_URL': 'http://happy-dev.fr',
        'BASE_URL': 'http://happy-dev.fr',
        'SEND_BACKLINKS': False,
        'JABBER_DEFAULT_HOST': None,
        'PERMISSIONS_CACHE': False,
        'ANONYMOUS_USER_NAME': None,
        'SERIALIZER_CACHE': False
    }
}
ldpsettings = LDPSettings(config)
ldpsettings.config = yaml.safe_load(yaml_config)

django_settings.configure(ldpsettings)

django.setup()
from django.test.runner import DiscoverRunner

test_runner = DiscoverRunner(verbosity=1)

# this is where we link our test classes to the runner
failures = test_runner.run_tests([
    'djangoldp_community.tests.tests_model',
    'djangoldp_community.tests.tests_permissions',
])
if failures:
    sys.exit(failures)
