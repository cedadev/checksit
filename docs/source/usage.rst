Usage
=====

Simplest check
--------------

First, ``cd`` into the ``checksit`` repository and activate the environment ``checksit`` was installed into. As default, **checksit needs to be run from the top level of the checksit repository**. For installations that followed the directions on the installation page, that will look like

.. code-block::

   cd ~/checksit
   source venv/bin/activate

Then ``checksit`` can be run using the following

.. code-block::

   checksit check /name/of/file

where ``/name/of/file`` is replaced with the path to and name of the file you wish to check.

``checksit`` will then look at ``/name/of/file`` and attempt to find either a template file to compare against or a series of specs to match with, and then print out the results of the checks.

Specify Template
----------------

A specific template can be chosen for ``checksit`` to use using the ``-t/--template`` flag

.. code-block::

   checksit check -t my_template /name/of/file

If ``/name/of/file`` is a file which you might want to check other files against, a template can be created when checking ``/name/of/file`` by using the ``--auto-cache`` flag

.. code-block::

   checksit check --auto-cache /name/of/file

Specify Specs
-------------

A spec file, or number of spec files, can also be given to ``checksit`` to compare the file against, using the ``-s/--specs`` flag. These files, in YAML format, point to functions and define parameters that will be used to check the file with

.. code-block::

   checksit check -s specfile1,specfile2 /name/of/file

``checksit`` will still attempt to find a template, or use a given one, to check the file with. To only use specs, the template option can be switched off by specifying ``-t off``.

Brief other flags
-----------------

Coming soon...

