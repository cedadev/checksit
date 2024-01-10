File specific actions
=====================

``checksit`` has some specific actions depending on the file given.

NCAS-GENERAL
------------

Files that conform to the NCAS-GENERAL standard are recognised by ``checksit``\ , and specs referring to the correct version of the standard are automatically searched for and used by ``checksit``\ , with specs to include checking file name format, global attributes, dimensions and variables for the used deployment mode and data product. For example, for a file with data from an automatic weather station (\ ``ncas-aws-10``\ ) using version 2.0.0 of the standard,

.. code-block::

   checksit check ncas-aws-10_iao_20231117_surface-met_v1.0.nc

is the same as

.. code-block::

   checksit check -t off -s ncas-amof-2.0.0/amof-file-name,ncas-amof-2.0.0/amof-common-land,ncas-amof-2.0.0/amof-surface-met,ncas-amof-2.0.0/amof-global-attrs ncas-aws-10_iao_20231117_surface-met_v1.0.nc

NCAS-IMAGE
----------

Coming soon...


