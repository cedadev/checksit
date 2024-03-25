Vocabs
======

Location
--------

Vocab files are stored in the ``checksit/vocabs`` folder, and can be grouped in folders within this
directory.

Format
------

Vocab files are stored as JSON files. When a key has a number of acceptable options, these are grouped
in a list format, e.g.

.. code-block:: json

   {
     "featureType": ["timeSeries","timeSeriesProfile","trajectory"],
   }

