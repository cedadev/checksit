Specs
=====

Location
--------

Spec files are saved within the ``specs/groups`` folder at the top level of the ``checksit`` repository. Files can be grouped within folders in this directory if required.

Format of spec file
-------------------

Spec files are in YAML format, and are split into sections by function calls. An example section from a YAML spec file might look like

.. code-block:: yaml

   required-global-attrs:
     func: checksit.generic.check_global_attrs
     params:
       defined_attrs:
         - source
         - title
       vocab_attrs:
         Conventions: __vocabs__:cf-netcdf:Conventions
         another_attribute: __vocabs__:attribute_vocabs

Line 1: ``required-global-attrs`` is a label which must be unique within the file.

Line 2: ``func: checksit.generic.check_global_attrs`` points to the function that will be used, in this case it's the ``check_global_attrs`` function within the ``checksit/generic.py`` file.

Line 3: ``params`` indicates the following section is the parameters that will be passed to the function.

Line 4: ``defined_attrs`` is the name of a parameter in the function

Lines 5-6: ``source`` and ``title`` are the values being passed to the parameter. As they have a proceeding ``-``\ , they are parsed as a list, i.e. ``['source', 'title']``

Line 7: ``vocab_attrs`` is another parameter in the function

Line 8-9: Values for the ``vocab_attrs`` parameter. As these do not have a ``-`` proceeding, they are parsed as a dictionary, i.e. ``{'Conventions': '__vocabs__:cf-netcdf:Conventions', 'another_attribute': '__vocabs__:attribute_vocabs'}``

..

   Note that ``__vocabs__`` is the reference to the vocabs directory - see the vocabs page for more info.


Any number of these sections can be included in the same spec file, provided each has different labels.

