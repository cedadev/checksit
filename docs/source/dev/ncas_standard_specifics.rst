NCAS Data Standards
===================

NCAS-GENERAL
------------

Automatic use of spec files
^^^^^^^^^^^^^^^^^^^^^^^^^^^

When given a file to check and no template option has been specified, ``checksit/check.py`` looks to see if the file is a netCDF file, and if so if it has a Conventions global attribute with ``NCAS-GENERAL``, ``NCAS-AMOF`` or ``NCAS-AMF`` it its value, identifying the file as needing to conform to the ``NCAS-GENERAL`` data standard. ``checksit`` then identifies which version of the standard is being used, using the numbers that follow the standard identifier in the Conventions attribute. The data product and deployment mode are obtained from the file, and specs for product and deployment are added to specs for global attributes and file naming for that version of the standard.

Downloading of new versions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If specs for the version of the standard do not exist within ``specs/groups``, ``checksit`` will attempt to download the vocabs for that version and create the spec files using the ``make_amof_specs`` function within ``checksit/make_specs.py``. However, if ``checksit`` cannot find the vocabs for that version, or does not have permission to write into the ``specs/groups`` folder, then an error is raised.

