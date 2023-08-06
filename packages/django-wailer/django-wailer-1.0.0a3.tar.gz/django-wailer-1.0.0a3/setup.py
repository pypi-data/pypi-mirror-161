# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['wailer', 'wailer.migrations', 'wailer.templatetags']

package_data = \
{'': ['*'], 'wailer': ['templates/wailer/*']}

install_requires = \
['Django',
 'django-phonenumber-field[phonenumbers]>=6',
 'django-sms>=0.5',
 'premailer>=3']

setup_kwargs = {
    'name': 'django-wailer',
    'version': '1.0.0a3',
    'description': 'A Django emailing/texting utility',
    'long_description': "# Wailer\n\n![Unit Tests](https://github.com/WithAgency/Wailer/actions/workflows/tests.yml/badge.svg)\n![Documentation](https://readthedocs.com/projects/with-wailer/badge/?version=latest)\n\nWailer (WITH Mailer) is an utility that builds on top of Django's emailing\ncapabilities (and SMS through `django-sms`) in order to provide easy solutions\nto common emailing problems.\n\n- Inlining CSS of emails you send\n- Have direct-access URLs for those emails\n- Manage the localization (even from a server-side task)\n\n## Documentation\n\n[✨ **Documentation is there** ✨](https://with-wailer.readthedocs-hosted.com/en/latest/)\n",
    'author': 'Rémy Sanchez',
    'author_email': 'remy.sanchez@hyperthese.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/withagency/wailer',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
