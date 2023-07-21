What where and how?
===================

Description on some of the key parts of checksit, how they work, what to add/edit

checksit working directory
--------------------------

By default, checksit needs to be run from the top level of the checksit repository. This can be changed by editing the ``basedir`` value in ``checksit/etc/checksit.ini`` to the location of the checksit repository before installing checksit.

Readers
-------

One of the first things ``checksit`` has to do is read the file that it is being asked to check. Within ``checksit/readers`` are a number of Python scripts which includes a class that will read the file into a format suitable for ``checksit``\ , with , and a ``read`` function that returns the class in that file. This ``read`` function is called in ``checksit/check.py``.

Functions for specs
-------------------

Functions used by checks from spec files are in ``checksit/generic.py``. These functions take a dictionary representation of the data file (as made by the ``to_dict`` function in the reader class), the parameters that are needed for the function which have values defined in the spec file, plus the ``skip_spellcheck`` variable, which should have the default value of ``False`` (alternatively, ``**kwargs`` could be included in the function parameters instead of ``skip_spellcheck`` if the spellchecking functionality is not required). The ``skip_spellcheck`` parameter is added to the specs by ``checksit``\ , and does not need to be included in the spec YAML files. 

The spellchecking functionality aims to spot if a file might have a spelling error in. For example, if a spec states that there should be a variable called ``time`` in the file, but one is not found, it will then look for slight misspellings of ``time``\ , although requiring the first letter to be correct. The function that does this is called ``search_close_match`` and is in the ``checksit/generic.py`` file, and can be called from other functions within this file.

vocabs checks
-------------

``checksit`` allows for templates and specs to define checks against known vocabularies. These vocabs are stored as JSON files within ``checksit/vocabs``\ , and can be grouped into folders within this directory. This folder is referenced through ``checksit`` as ``__vocabs__``. Defining a vocab check could look like 

.. code-block::

   variables:
     time: __vocabs__:AMF_CVs/2.0.0/AMF_product_common_variable_land:product_common_variable_land:time

which states that the ``time`` variable must match the vocab found in ``checksit/vocabs/AMF_CFs/2.0.0/AMF_product_common_variable_land.json`` (note the ``.json`` extension is excluded when specifying the vocab file), using the data in that file located by the ``product_common_variable_land`` key and then the ``time`` key.

An option is also included for a vocab match of one value out of many. For example,

.. code-block::

   platform: __vocabs__:AMF_CVs/2.0.0/AMF_platform:platform:__all__

specifies ``platform`` should match one of the values found under the ``platform`` key in ``checksit/vocabs/AMF_CVs/2.0.0/AMF_platform.json``\ , and 

.. code-block::

   source: __vocabs__:AMF_CVs/2.0.0/AMF_ncas_instrument:ncas_instrument:__all__:description

requires ``source`` to match any of the ``description`` tags nested under the ``ncas_instrument`` key in ``checksit/vocabs/AMF_CVs/2.0.0/AMF_ncas_instrument.json``. In these cases, ``__all__`` acts similarly to the wildcard ``*`` in bash, but only one instance of ``__all__`` is allowed.

rules checks
------------

``checksit`` also has a number of rules it can check values against when doing template and spec checks, managed by the ``Rules`` class in ``checksit/rules/rules.py``. There are four types of rules:


* ``type-rule``\ : checks the value is of the correct type, e.g. integer, float or string
* ``regex``\ : checks the value matches a given regular expression
* ``regex-rule``: checks the value matches a pre-defined regex. These are: 

.. list-table::
   :header-rows: 1

   * - ``regex-rule``
     - regular expression
   * - "integer"
     - ``r"-?\d+"``
   * - "valid-email"
     - ``r"[^@\s]+@[^@\s]+\.[^\s@]+"``
   * - "valid-url"
     - ``r"https?://[^\s]+\.[^\s]*[^\s\.](/[^\s]+)?"``
   * - "valid-url-or-na"
     - ``r"(https?://[^\s]+.[^\s]*\ `^\s. </[^\s]+>`_\ )" + _NOT_APPLICABLE_RULES``
   * - "match:vN.M"
     - ``r"v\d\.\d"``
   * - "datetime"
     - ``"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?"``
   * - "datetime-or-na"
     - ``"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(.\d+)?)" + _NOT_APPLICABLE_RULES``
   * - "number"
     - ``r"-?\d+(\.\d+)?"``


where ``NOT_APPLICABLE_RULES`` cover phrases such as "Not Available", "Not applicable", "N/A" and others similar.


* ``rule-func``\ : checks the value against a pre-defined function, which are defined in ``checksit/rules/rule_funcs.py``. Rule functions defined in this file include, for example ``match_one_of``\ , where a value mush match one option from a list, and ``string_of_length``\ , where a string must be of a defined length or longer (e.g. ``5`` or ``5+``\ ).


