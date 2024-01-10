Templates
=========

Location
--------

Template files are stored within the ``template-cache`` folder at the top level of the ``checksit`` repository.

Format
------

Template files can be saved in a number of formats. Using the ``--auto-cache`` flag when checking a netCDF file will create a template as a CDL file, as is output by ``ncdump -h``. Templates can also be saved as a YAML file, with references to ``__vocabs__`` and ``__rules__`` included.
