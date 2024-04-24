File specific actions
=====================

``checksit`` has some specific actions depending on the file given.

NCAS-GENERAL
------------

Files that are designed to the NCAS-GENERAL standard are recognised by ``checksit``\ , and specs
referring to the correct version of the standard are automatically searched for and used by
``checksit``\ , with specs to include checking file name format, global attributes, dimensions
and variables for the used deployment mode and data product. For example, for a file with data
from an automatic weather station (\ ``ncas-aws-10``\ ) using version 2.0.0 of the standard,

.. code-block::

   checksit check ncas-aws-10_iao_20231117_surface-met_v1.0.nc

is the same as

.. code-block::

   checksit check -t off -s ncas-amof-2.0.0/amof-file-name,ncas-amof-2.0.0/amof-common-land,ncas-amof-2.0.0/amof-surface-met,ncas-amof-2.0.0/amof-global-attrs ncas-aws-10_iao_20231117_surface-met_v1.0.nc

NCAS-IMAGE
----------

The NCAS-IMAGE standard is also identified by ``checksit``\ , and the appropriate specs can be
found to check both global tags and photo or plot specific tags, i.e.

.. code-block::

   checksit check ncas-cam-9_cao_20231117_photo_v1.0.nc

is the same as

.. code-block::

   checksit check -t off -s ncas-image-1.0.0/amof-image-global-attrs,ncas-image-1.0.0/amof-photo ncas-cam-9_cao_20231117_photo_v1.0.nc

NCAS-Radar
----------

The NCAS-Radar standard is also recognised by ``checksit``\ , with the correct specs identified and
used if no template or spec options are specified. Unlike the NCAS-GENERAL and NCAS-IMAGE standards,
NCAS-Radar does not have specific data product specs, instead there are a number of different spec
files covering different areas of the standard. These spec files are:

.. code-block::

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
