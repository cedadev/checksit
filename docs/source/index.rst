checksit
========

checksit is a tool that provides auto-checking of files against a range of available checks.
Originally designed to be used against the NCAS Data Standards to provide conformancy checking,
it has evolved to be more generic and can accomodate other compliance checking options too.

On a basic level a user can point the checksit tool at a given file and it will attempt to run
some basic checks based on some matches that it will try to perform. 
Other options include specifying the particular checks to run or to compare with known 'good' files.

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Users' Guide:

   install
   usage
   specifics

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Developers' Guide:

   dev/where_does_checksit_do_it
   dev/specs
   dev/templates
   dev/vocabs
   dev/ncas_standard_specifics
   dev/api

.. toctree::
   :caption: Links
   :hidden:

   GitHub <https://github.com/cedadev/checksit>
