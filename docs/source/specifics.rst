File specific actions
=====================

``checksit`` has some specific actions depending on the file given.

NCAS Data
---------

If the ``checksit check`` command is given a file and no template or specs are
specified, then ``checksit`` will try to identify if the file is meant to comply with
one of the NCAS standards (NCAS-General, NCAS-Radar or NCAS-Image). ``checksit`` will
designate a file as an "NCAS standard" file if one of the following conditions is met:

* The file contains the global attribute "Conventions" and the value of this attribute
  contains "NCAS-" (case insensitive match).
* The file contains the "XMP-photoshop:Instructions" metadata tag and the value of this
  tag contains "National Centre for Atmospheric Science" (case insensitive match).
* The name of the file starts with "ncas-" (case sensitive match).

If any of these conditions match, then ``checksit`` will try to identify which NCAS
standard the file is meant to comply with.


NCAS-General
^^^^^^^^^^^^

If the name of the file ends with `.nc`, and the file contains the global attribute
"Conventions" with a value that contains one of "NCAS-General", "NCAS-AMOF", or
"NCAS-AMF" (case insensitive match), then the file is designated as an NCAS-General
file. ``checksit`` then determines which specs are needed to perform the correct
checks, including checking file name format, global attributes, dimensions, and
variables used for the deployment mode and data product.

For example, for a file with data from an automatic weather station
(\ ``ncas-aws-10``\ ) using version 2.0.0 of the standard,

.. code-block:: bash

   checksit check ncas-aws-10_iao_20231117_surface-met_v1.0.nc

is the same as

.. code-block:: bash

   checksit check -t off -s ncas-amof-2.0.0/amof-file-name,ncas-amof-2.0.0/amof-common-land,ncas-amof-2.0.0/amof-surface-met,ncas-amof-2.0.0/amof-global-attrs ncas-aws-10_iao_20231117_surface-met_v1.0.nc


NCAS-Radar
^^^^^^^^^^

If the file name ends with `.nc`, and the file contains the global attribute
"Conventions" with a value that contains "NCAS-Radar" (case insensitive match), then
the file is identified as an NCAS-Radar file. There are a number of different spec
files that cover different areas of the standard which ``checksit`` will use to check
against the files. These spec files are:

.. code-block:: bash

  coordinate-variables
  dimensions
  global-attrs
  global-variables
  instrument-parameters
  location-variables
  moment-variables
  radar-calibration
  radar-parameters
  sensor-pointing-variables
  sweep-variables


NCAS-Image
^^^^^^^^^^

If the name of the file ends with one of `.png`, `.jpg`, or `.jpeg` (case insensitive
match), and the file contains the "XMP-photoshop:Instructions" metadata tag with a
value that contains "National Centre for Atmospheric Science" (case insensitive match),
then the file is identified as an NCAS-Image file. The appropriate specs are then found
to check both global tags and photo or plot specific tags. For example,

.. code-block:: bash

   checksit check ncas-cam-9_cao_20231117_photo_v1.0.nc

is the same as

.. code-block:: bash

   checksit check -t off -s ncas-image-1.0.0/amof-image-global-attrs,ncas-image-1.0.0/amof-photo ncas-cam-9_cao_20231117_photo_v1.0.nc
