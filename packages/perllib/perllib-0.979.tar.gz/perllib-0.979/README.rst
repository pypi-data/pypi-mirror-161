=======
perllib
=======


.. image:: https://img.shields.io/pypi/v/perllib.svg
        :target: https://pypi.python.org/pypi/perllib

.. image:: https://img.shields.io/travis/snoopyjc/perllib.svg
        :target: https://travis-ci.com/snoopyjc/perllib

.. image:: https://readthedocs.org/projects/perllib/badge/?version=latest
        :target: https://perllib.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




Library functions to support pythonizer


* Free software: GNU General Public License v3
* Documentation: https://perllib.readthedocs.io.


Features
--------

* Perl library functions typically return 1 on success and undef on failure, whereas python library functions raise exceptions on failure.  Also, perl automatically converts variables from strings to numbers and vice-versa when referenced in the appropriate context.  In perl, global variables are truly global across files and are organized by package name, where in python global variables have file scope.  In addition, perl has autovivification, which means that arrays and hash tables magically appear out of whole cloth when referenced.  This library supports all of those features and allows the "pythonizer" perl to python translator generate code that is fairly readable.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
