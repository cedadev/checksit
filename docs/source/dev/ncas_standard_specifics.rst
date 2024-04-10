NCAS Data Standards
===================

If given a file to check where the file name starts with ``ncas-``, as in the start of an NCAS
instrument name, and no template or specs are specified, then ``checksit`` will attempt to find specs
to check the file against depending on which NCAS Data Standard is being used.

NCAS-GENERAL
------------

Automatic use of spec files
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the file is a netCDF file with the ``Conventions`` global attribute containing one of ``NCAS-GENERAL``,
``NCAS-AMOF`` or ``NCAS-AMF`` it its value, the file is identified as needing to conform to the
``NCAS-GENERAL`` data standard. ``checksit`` then identifies which version of the standard is being
used, using the numbers that follow the standard identifier in the Conventions attribute.
The data product and deployment mode are obtained from the file, and specs for product and deployment
are added to specs for global attributes and file naming for that version of the standard.

Downloading of new versions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If specs for the version of the standard do not exist within ``specs/groups``, ``checksit`` will
attempt to download the vocabs for that version and create the spec files using the ``make_amof_specs``
function within ``checksit/make_specs.py``. However, if ``checksit`` cannot find the vocabs for that
version, or does not have permission to write into the ``specs/groups`` folder, then an error is
raised.

NCAS-IMAGE
----------

If instead of a netCDF file ``checksit`` is checking an image file, based on the file extension being
one of ``png``, ``jpg`` or ``jpeg`` (or uppercase versions), and the file has the
``XMP-photoshop:Instructions`` metadata tag with a value mentioning the NCAS Image Standard, then
``checksit`` will find specs related to NCAS-IMAGE. The version of the standard is identified using
the ``Instructions`` tag, and specs relating to either the ``photo`` or ``plot`` data product are
selected depending on the file name. The data product spec is combined with a global tags spec file
that covers tags required by the standard regardless of which data product is used.