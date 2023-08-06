# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bk_plugin_runtime', 'bk_plugin_runtime.config']

package_data = \
{'': ['*'],
 'bk_plugin_runtime': ['static/*',
                       'static/account/*',
                       'static/admin/css/*',
                       'static/admin/fonts/*',
                       'static/admin/img/*',
                       'static/admin/img/gis/*',
                       'static/admin/js/*',
                       'static/admin/js/admin/*',
                       'static/admin/js/vendor/jquery/*',
                       'static/admin/js/vendor/xregexp/*',
                       'static/assets/*',
                       'static/assets/css/*',
                       'static/assets/fonts/*',
                       'static/assets/img/*',
                       'static/assets/js/*',
                       'static/djcelery/*',
                       'static/images/*',
                       'static/js/*',
                       'static/open/*',
                       'static/open/css/*',
                       'static/open/img/*',
                       'static/remote/*',
                       'static/remote/artDialog-6.0.4/*',
                       'static/remote/artDialog-6.0.4/css/*',
                       'static/remote/artDialog-6.0.4/new/css/*',
                       'static/remote/artDialog-6.0.4/new/js/*',
                       'static/remote/artdialog/*',
                       'static/remote/artdialog/skins/*',
                       'static/remote/artdialog/skins/icons/*',
                       'static/remote/jquery/*',
                       'static/remote/v3/assets/bootstrap-3.3.4/css/*',
                       'static/remote/v3/assets/bootstrap-3.3.4/fonts/*',
                       'static/remote/v3/assets/bootstrap-3.3.4/js/*',
                       'static/remote/v3/assets/jquery-ui-1.11.0.custom/*',
                       'static/remote/v3/assets/jquery-ui-1.11.0.custom/external/jquery/*',
                       'static/remote/v3/assets/jquery-ui-1.11.0.custom/images/*',
                       'static/remote/v3/assets/js/*',
                       'static/remote/v3/bk/css/*',
                       'static/remote/v3/bk/js/*',
                       'templates/*',
                       'templates/admin/*']}

install_requires = \
['Django>=2.2.6,<3.0.0',
 'blueapps==4.2.4',
 'celery>=4.4.0,<5.0.0',
 'ddtrace>=0.14.1,<0.15.0',
 'django-celery-beat>=2.0.0,<3.0.0',
 'django-celery-results>=1.2.1,<2.0.0',
 'django-cors-headers>=3.8.0,<4.0.0',
 'django-dbconn-retry>=0.1.5,<0.2.0',
 'djangorestframework>=3.12.4,<4.0.0',
 'drf-yasg>=1.20.0,<2.0.0',
 'gunicorn>=19.6.0,<20.0.0',
 'raven>=6.5.0,<7.0.0',
 'redis>=2.10.5,<3.0.0']

setup_kwargs = {
    'name': 'bk-plugin-runtime',
    'version': '1.3.1',
    'description': 'bk plugin python django runtime',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
