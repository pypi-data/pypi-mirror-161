====
acct
====

.. image:: https://img.shields.io/badge/made%20with-pop-teal
   :alt: Made with pop, a Python implementation of Plugin Oriented Programming
   :target: https://pop.readthedocs.io/

.. image:: https://img.shields.io/badge/made%20with-python-yellow
   :alt: Made with Python
   :target: https://www.python.org/

Simple and secure account management

=====
USAGE
=====

Yaml files containing confidential information can be encrypted for use inside of `acct` base applications.
This is an example of what an `acct` credentials file might look like.

credentials.yml

.. code-block:: yaml

    provider:
      profile_name:
        username: XXXXXXXXXXXX
        password: XXXXXXXXXXXX
        api_key: XXXXXXXXXXXXXXXXXXX

Next use the `acct` command to encrypt this file using the fernet algorithm:

.. code-block:: bash

    $ acct encrypt credentials.yml
    YeckEnWEGOjBDVxxytw13AsdLgquzhCtFHOs7kDsna8=

The `acct` command can also be used to decrypt the encrypted file:

.. code-block:: bash

    $ acct decrypt credentials.yml.fernet --output=yaml --acct-key="YeckEnWEGOjBDVxxytw13AsdLgquzhCtFHOs7kDsna8="

The fernet plugin is the default for encryption, but other plugins may be added.
To use the AES plugin change the previous commands to:

.. code-block:: bash

    $ acct encrypt --crypto-plugin aesgcm256 credentials.yml
    YeckEnWEGOjBDVxxytw13AsdLgquzhCtFHOs7kDsna8=
    $ acct decrypt --crypto-plugin aesgcm256 credentials.yml.aesgcm256 --output=yaml --acct-key="YeckEnWEGOjBDVxxytw13AsdLgquzhCtFHOs7kDsna8="


What is POP?
------------

This project is built with `pop <https://pop.readthedocs.io/>`__, a Python-based
implementation of *Plugin Oriented Programming (POP)*. POP seeks to bring
together concepts and wisdom from the history of computing in new ways to solve
modern computing problems.

For more information:

* `Intro to Plugin Oriented Programming (POP) <https://pop-book.readthedocs.io/en/latest/>`__
* `pop-awesome <https://gitlab.com/saltstack/pop/pop-awesome>`__
* `pop-create <https://gitlab.com/saltstack/pop/pop-create/>`__

Getting Started
===============

Prerequisites
-------------

* Python 3.6+
* git *(if installing from source, or contributing to the project)*

Installation
------------

.. note::

   If wanting to contribute to the project, and setup your local development
   environment, see the ``CONTRIBUTING.rst`` document in the source repository
   for this project.

If wanting to use ``acct``, you can do so by either
installing from PyPI or from source.

Acknowledgements
================

* `Img Shields <https://shields.io>`__ for making repository badges easy.
