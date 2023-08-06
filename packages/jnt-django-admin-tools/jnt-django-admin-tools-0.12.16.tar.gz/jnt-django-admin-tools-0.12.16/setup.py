# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['jnt_admin_tools',
 'jnt_admin_tools.admin',
 'jnt_admin_tools.admin.mixins',
 'jnt_admin_tools.dashboard',
 'jnt_admin_tools.dashboard.management',
 'jnt_admin_tools.dashboard.management.commands',
 'jnt_admin_tools.dashboard.migrations',
 'jnt_admin_tools.dashboard.templatetags',
 'jnt_admin_tools.helpers',
 'jnt_admin_tools.menu',
 'jnt_admin_tools.menu.admin',
 'jnt_admin_tools.menu.migrations',
 'jnt_admin_tools.menu.templatetags',
 'jnt_admin_tools.templatetags',
 'jnt_admin_tools.theming',
 'jnt_admin_tools.theming.templatetags']

package_data = \
{'': ['*'],
 'jnt_admin_tools': ['locale/ar/LC_MESSAGES/*',
                     'locale/bg/LC_MESSAGES/*',
                     'locale/bn/LC_MESSAGES/*',
                     'locale/ca/LC_MESSAGES/*',
                     'locale/cs/LC_MESSAGES/*',
                     'locale/da/LC_MESSAGES/*',
                     'locale/de/LC_MESSAGES/*',
                     'locale/el/LC_MESSAGES/*',
                     'locale/en/LC_MESSAGES/*',
                     'locale/es/LC_MESSAGES/*',
                     'locale/es_AR/LC_MESSAGES/*',
                     'locale/fi/LC_MESSAGES/*',
                     'locale/fr/LC_MESSAGES/*',
                     'locale/he/LC_MESSAGES/*',
                     'locale/hu/LC_MESSAGES/*',
                     'locale/it/LC_MESSAGES/*',
                     'locale/ja/LC_MESSAGES/*',
                     'locale/nl/LC_MESSAGES/*',
                     'locale/pl/LC_MESSAGES/*',
                     'locale/pt/LC_MESSAGES/*',
                     'locale/pt_BR/LC_MESSAGES/*',
                     'locale/ru/LC_MESSAGES/*',
                     'locale/sk/LC_MESSAGES/*',
                     'locale/sv/LC_MESSAGES/*',
                     'locale/tr/LC_MESSAGES/*',
                     'locale/uk/LC_MESSAGES/*',
                     'locale/zh_CN/LC_MESSAGES/*',
                     'locale/zh_TW/LC_MESSAGES/*',
                     'static/jnt_admin_tools/images/*',
                     'static/jnt_admin_tools/js/*',
                     'templates/admin/jnt_admin_tools/*'],
 'jnt_admin_tools.dashboard': ['static/jnt_admin_tools/css/*',
                               'static/jnt_admin_tools/css/jquery/*',
                               'static/jnt_admin_tools/css/jquery/images/*',
                               'static/jnt_admin_tools/js/*',
                               'static/jnt_admin_tools/js/jquery/*',
                               'templates/admin/*',
                               'templates/jnt_admin_tools/dashboard/*',
                               'templates/jnt_admin_tools/dashboard/modules/*'],
 'jnt_admin_tools.menu': ['static/jnt_admin_tools/css/*',
                          'static/jnt_admin_tools/js/*',
                          'templates/admin/*',
                          'templates/jnt_admin_tools/menu/*'],
 'jnt_admin_tools.theming': ['static/jnt_admin_tools/css/*',
                             'static/jnt_admin_tools/images/*',
                             'templates/admin/*']}

install_requires = \
['django>=3', 'jnt-django-toolbox']

setup_kwargs = {
    'name': 'jnt-django-admin-tools',
    'version': '0.12.16',
    'description': 'Improved django admin interface',
    'long_description': None,
    'author': 'Junte',
    'author_email': 'tech@junte.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
