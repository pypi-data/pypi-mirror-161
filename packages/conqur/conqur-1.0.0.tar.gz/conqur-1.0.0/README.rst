======
ConQuR
======


.. image:: https://img.shields.io/pypi/v/conqur
        :target: https://pypi.org/pypi/conqur

.. image:: https://readthedocs.org/projects/conqur/badge/?version=latest
        :target: https://conqur.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




Batch effects removal for microbiome data via conditional quantile regression on Python.


* Free software: MIT license
* Documentation: https://conqur.readthedocs.io.


Description
-----------

We implement in Python the batch effect removal algorithm described in Ling_et_al_.

Implementation_ used in the paper is written in R. This implementation attempts to
be as close as possible, but has some new features (see Features for details).

Features
--------

This implementation supports

* using non-negative float features, batch and covariate variables;

* using logistic regression with an L2 penalty;

* using arbitrary quantiles in quantile regression.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _Ling_et_al: https://www.biorxiv.org/content/10.1101/2021.09.23.461592v1
.. _Implementation: https://github.com/wdl2459/ConQuR
