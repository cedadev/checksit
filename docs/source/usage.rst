Usage
=====

Simplest check
--------------

First, ``cd`` into the ``checksit`` repository and activate the environment ``checksit`` was
installed into. **As default, checksit needs to be run from the top level of the checksit
repository**. For installations that followed the directions on the installation page, that
will look like

.. code-block::

   cd ~/checksit
   source venv/bin/activate

Then ``checksit`` can be run using the following, as an example:

.. code-block::

   checksit check /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc 

``checksit`` will then look at the file given and attempt to find either a template file to
compare against or a series of specs to match with, and then print out the results of the checks.

Specify Template
----------------

A specific template can be chosen for ``checksit`` to use using the ``-t/--template`` flag

.. code-block::

   checksit check --template=template-cache/rls_rcp85_land-cpm_uk_2.2km_01_day_19801201-19811130.cdl /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc

If the file being checked is a file which you might want to check other files against, a template
can be created when checking this file by using the ``--auto-cache`` flag, e.g.

.. code-block::

   checksit check --auto-cache /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc

Specify Specs
-------------

A spec file, or number of spec files, can also be given to ``checksit`` to compare the file against,
using the ``-s/--specs`` flag. These files, in YAML format, point to functions and define parameters
that will be used to check the file with

.. code-block::

   checksit check --specs=ceda-base /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc

``checksit`` will still attempt to find a template, or use a given one, to check the file with. To
only use specs, the template option can be switched off by specifying ``-t off``.

Brief other flags
-----------------

Coming soon...

