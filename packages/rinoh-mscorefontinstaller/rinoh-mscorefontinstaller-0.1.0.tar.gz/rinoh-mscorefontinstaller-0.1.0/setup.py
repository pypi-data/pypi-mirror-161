# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['rinoh_mscorefontinstaller']
install_requires = \
['hachoir==3.1.3']

setup_kwargs = {
    'name': 'rinoh-mscorefontinstaller',
    'version': '0.1.0',
    'description': "Helper package to install Microsoft's Core fonts for the Web",
    'long_description': "rinoh-mscorefontinstaller\n=========================\n\n.. image:: http://img.shields.io/pypi/v/rinoh-mscorefontinstaller.svg\n   :target: https://pypi.python.org/pypi/rinoh-mscorefontinstaller\n   :alt: PyPI\n\n.. image:: https://img.shields.io/pypi/pyversions/rinoh-mscorefontinstaller.svg\n   :target: https://pypi.python.org/pypi/rinoh-mscorefontinstaller\n   :alt: Python version\n\n\nThis is a helper package to download and extract Microsoft's `Core fonts for the\nWeb`_. The fonts cannot be distributed as part of plain Python packages due the\nrestrictions imposed by the EULA_ for these fonts.\n\nThis package is set as a build/install-time requirement for the font packages,\nso you should never need to install this package manually.\n\nThe `repository for this package`_ contains a script to create the distribution\npackages for the fonts. See `DEVELOPING.rst`` for more information.\n\n\n.. _Core fonts for the Web: https://en.wikipedia.org/wiki/Core_fonts_for_the_Web\n.. _EULA: https://github.com/brechtm/corefonts/blob/master/LICENSE\n.. _repository for this package: https://github.com/brechtm/rinoh-mscorefonts\n",
    'author': 'Brecht Machiels',
    'author_email': 'brecht@mos6581.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/brechtm/rinoh-mscorefonts',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
