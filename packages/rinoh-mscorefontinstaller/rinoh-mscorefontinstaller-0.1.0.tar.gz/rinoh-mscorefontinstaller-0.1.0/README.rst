rinoh-mscorefontinstaller
=========================

.. image:: http://img.shields.io/pypi/v/rinoh-mscorefontinstaller.svg
   :target: https://pypi.python.org/pypi/rinoh-mscorefontinstaller
   :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/rinoh-mscorefontinstaller.svg
   :target: https://pypi.python.org/pypi/rinoh-mscorefontinstaller
   :alt: Python version


This is a helper package to download and extract Microsoft's `Core fonts for the
Web`_. The fonts cannot be distributed as part of plain Python packages due the
restrictions imposed by the EULA_ for these fonts.

This package is set as a build/install-time requirement for the font packages,
so you should never need to install this package manually.

The `repository for this package`_ contains a script to create the distribution
packages for the fonts. See `DEVELOPING.rst`` for more information.


.. _Core fonts for the Web: https://en.wikipedia.org/wiki/Core_fonts_for_the_Web
.. _EULA: https://github.com/brechtm/corefonts/blob/master/LICENSE
.. _repository for this package: https://github.com/brechtm/rinoh-mscorefonts
