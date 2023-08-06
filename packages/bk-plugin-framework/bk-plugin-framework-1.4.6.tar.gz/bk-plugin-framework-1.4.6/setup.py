# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bk_plugin_framework',
 'bk_plugin_framework.hub',
 'bk_plugin_framework.kit',
 'bk_plugin_framework.runtime',
 'bk_plugin_framework.runtime.callback',
 'bk_plugin_framework.runtime.callback.celery',
 'bk_plugin_framework.runtime.callback.migrations',
 'bk_plugin_framework.runtime.loghub',
 'bk_plugin_framework.runtime.loghub.migrations',
 'bk_plugin_framework.runtime.schedule',
 'bk_plugin_framework.runtime.schedule.celery',
 'bk_plugin_framework.runtime.schedule.migrations',
 'bk_plugin_framework.services',
 'bk_plugin_framework.services.bpf_service',
 'bk_plugin_framework.services.bpf_service.api',
 'bk_plugin_framework.services.bpf_service.api.serializers',
 'bk_plugin_framework.services.bpf_service.management',
 'bk_plugin_framework.services.bpf_service.management.commands',
 'bk_plugin_framework.services.bpf_service.migrations',
 'bk_plugin_framework.services.debug_panel',
 'bk_plugin_framework.services.debug_panel.management.commands',
 'bk_plugin_framework.services.debug_panel.migrations',
 'bk_plugin_framework.utils']

package_data = \
{'': ['*'],
 'bk_plugin_framework.services.bpf_service.management.commands': ['data/*']}

install_requires = \
['apigw-manager[extra]>=1.0.6,<2.0.0',
 'bk-plugin-runtime==1.3.1',
 'pydantic>=1.0,<2.0',
 'werkzeug>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'bk-plugin-framework',
    'version': '1.4.6',
    'description': 'bk plugin python framework',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
