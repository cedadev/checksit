Usage
=====

Basic use
---------

Assuming that ``checksit`` was installed following the guide on the
`installation page <install.html>`_, the command ``checksit`` should be available in
the terminal if the virtual environment is active. To check a file, the command
``check`` can be used, followed by the path to the file to check, for example:

.. code-block:: bash

   checksit check my-file.ext

``checksit`` will then look at the file, attempt to work out what template or specs to
check the file with, and then print out the results of the checks. See the
`understanding ouput page <understanding-output.html>`_ for more information on how to
read and interpret the output from ``checksit``..


How does ``checksit`` decide what checks to use?
------------------------------------------------

``checksit`` uses templates and specs to perform checks on files. A template is a file
with a similar structure to the file being checked, and specs are files that define
rules and vocabularies that the contents of the file being checked need to meet.

When checking a file, if no template or spec files are given in the ``check`` command,
``checksit`` will attempt to find the most suitable checks to use.
It does that with the following steps:
1. ``checksit`` looks to see if there are any file-specific checks that have been
   defined for that particular file. These include the checks for NCAS data standards.
   For more information on how these file-specific checks are determined, see the
   `file-specifics page <specifics.html>`_
2. If no file-specific checks are found, and template checks have not been turned off,
   ``checksit`` will look for a template file that matches the file being checked.
  - It finds a template file by first searching if the file to be checked matches
    against any known rules in the checksit config file with a defined template file to
    use (e.g. UKCP09 data).
  - If that doesn't produce a template file ``checksit`` searches the template cache,
    searching for a file with a similar name.
  - If a template file still isn't found, ``checksit`` uses a default template, called
    `ceda-base.yml`.


Manually specifying templates and specs
---------------------------------------

A specific template can be chosen for ``checksit`` to use by specifying the file with
the ``-t/--template`` flag when running the check command:

.. code-block:: bash

   checksit check --template=template-cache/rls_rcp85_land-cpm_uk_2.2km_01_day_19801201-19811130.cdl /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc

A spec file, or number of spec files, can also be given to ``checksit`` to compare the file against,
using the ``-s/--specs`` flag. These files, in YAML format, point to functions and define parameters
that will be used to check the file with

.. code-block::

   checksit check --specs=ceda-base /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc

.. note::
   Multiple spec files should be separated by commas, with no spaces, e.g.
   ``--specs=ceda-base,ceda-ukcp18``

Even with specs defined, ``checksit`` will still attempt to find a template, or use a
given one, to check the file with. To only use specs, the template option must be
switched off by specifying ``-t off``.


Where can I find specs to use?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Specs are provided with the ``checksit`` python package. Available specs can be seen in
the `GitHub repository <https://github.com/cedadev/checksit/checksit/data>`_ for
``checksit``.

.. note::
   When specifying specs, the path to the spec file should be given relative to the
   ``specs/groups`` folder, and without the file extension, e.g. ``--specs=ceda-base``
   or ``--specs=ncas-amof-2.0.0/amof-global-attrs``.


Multiple Files
--------------

If you want to check multiple files, you can do so by using the ``check-files`` command and list
all the files to check, for example:

.. code-block::

   checksit check-files /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20681201-20691130.nc

``checksit`` will check all files individually, meaning it could use different specs and/or template checks for each file, unless the template and/or specs are specifically given using the ``-t/--template`` and ``-s/--specs`` flags.

Brief other flags
-----------------

Some other options that can be given to the ``check`` and ``check-files`` commands include:
- ``-l/--log-mode``: whether ``checksit`` should output in "standard" (default) or "compact" mode.
- ``-w/--ignore-warnings``: if flag is given, warnings from file checks will not be printed in the output.
- ``-p/--skip-spellcheck``: if flag is given, spellcheck that attempts to find close matches to any failed checks will be skipped.

