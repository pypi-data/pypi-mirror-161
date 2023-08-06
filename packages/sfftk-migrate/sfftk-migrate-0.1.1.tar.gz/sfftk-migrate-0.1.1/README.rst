========================================================
``sfftk-migrate``: Utility to Update Old EMDB-SFF Files
========================================================

.. image:: https://badge.fury.io/py/sfftk-migrate.svg
   :target: https://badge.fury.io/py/sfftk-migrate

.. image:: https://img.shields.io/pypi/pyversions/sfftk-migrate
   :alt: PyPI - Python Version

.. image:: https://travis-ci.org/emdb-empiar/sfftk-migrate.svg?branch=master
    :target: https://travis-ci.org/emdb-empiar/sfftk-migrate

.. image:: https://readthedocs.org/projects/sfftk-migrate/badge/?version=latest
   :target: https://sfftk-migrate.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/emdb-empiar/sfftk-migrate/badge.svg?branch=master
   :target: https://coveralls.io/github/emdb-empiar/sfftk-migrate?branch=master

-------------
About
-------------

``sfftk-migrate`` is a utility for *migrating EMDB-SFF files* from older to the latest version of the data model
(see `https://emdb-empiar.github.io/EMDB-SFF/ <https://emdb-empiar.github.io/EMDB-SFF/>`_ for the latest version).
It currently only supports migrations of XML (``.sff``) files from EMDB-SFF ``v0.7.0.dev0``.

-------------
Usage
-------------

The main entry point for this utility is the ``sff-migrate`` command. Please consult the command-line help using:

.. code-block:: bash

    ~$ sff-migrate -h
    usage: sff-migrate [-h] [-t TARGET_VERSION] [-o OUTFILE] [-v] [-l] [-s]
                       [infile]

    Upgrade EMDB-SFF files to more recent schema

    positional arguments:
      infile                input XML file

    optional arguments:
      -h, --help            show this help message and exit
      -t TARGET_VERSION, --target-version TARGET_VERSION
                            the target version to migrate to [default: 0.8.0.dev1]
      -o OUTFILE, --outfile OUTFILE
                            outfile file [default: <infile>_<target>.xml]
      -v, --verbose         verbose output [default: False]
      -l, --list-versions   list supported versions [default: False]
      -s, --show-version    show the version of the input file [default: False]


Migrating is simple:

.. code-block:: bash

    ~$ sff-migrate file.sff

List supported versions:

.. code-block:: bash

    ~$ sff-migrate -l
    versions migratable to 0.8.0.dev1:
    * 0.7.0.dev0

Show the file's version:

.. code-block:: bash

    ~$ sff-migrate -s sfftk_migrate/data/xml/emd_1547.sff
    file sfftk_migrate/data/xml/emd_1547.sff is of version 0.7.0.dev0

    ~$ sff-migrate -s sfftk_migrate/data/xml/emd_1547_v0.8.0.dev1.sff
    file sfftk_migrate/data/xml/emd_1547_v0.8.0.dev1.sff is of version v0.8.0.dev0

-------------
License
-------------

``sfftk-migrate`` is free and open source software released under the terms of the Apache License,
Version 2.0. Source code is copyright **EMBL-European Bioinformatics Institute (EMBL-EBI) 2020**.

Source code is available from the Github repository:
`https://github.com/emdb-empiar/sfftk-migrate <https://github.com/emdb-empiar/sfftk-migrate>`_
