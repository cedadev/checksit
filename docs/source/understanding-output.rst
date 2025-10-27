Understanding output from checksit
==================================

After successfully running ``checksit check`` on a data file, you will receive output in the terminal that summarises the results of the checks performed. This output includes information about the template used, the specification files applied, and the data file being checked, as well as detailed results of the checks. An example of such output is displayed below.

.. code-block:: text

    Running with:
        Template: OFF
        Spec Files: ['ncas-amof-2.1.0/amof-file-name', 'ncas-amof-2.1.0/amof-common-land', 'ncas-amof-2.1.0/amof-mean-winds', 'ncas-amof-2.1.0/amof-global-attrs']
        Datafile: ncas-sonic-6_cvao_20241101_mean-winds_v1.0.nc


    ---------------- Running checks ------------------

    [FAILED] with 3 errors:

        01. [variable**************:wind_speed]: Attribute 'units' must have definition 'm s-1', not 'mph'.
        02. [variable**************:beaufort_scale]: Invalid variable 'beaufort_scale' found in file.
        03. [global-attributes:******:processing_software_url]*** Value 'Python' does not match regex rule: 'valid-url' - Example valid value 'https://github.com'.

    [WARNING] 6 warnings about file:

        01. [variable**************:wind_speed_of_gust]: Optional variable does not exist in file.
        02. [variable**************:wind_gust_from_direction]: Optional variable does not exist in file.
        03. [variable**************:upward_air_velocity]: Optional variable does not exist in file.
        04. [variable**************:sonic_air_temperature]: Optional variable does not exist in file.
        05. [variable**************:qc_flag_sonic_temperature]: Optional variable does not exist in file.
        06. [variable**************:qc_flag_wind_component_upward_air_velocity]: Optional variable does not exist in file.

There are three sections to the output: the configuration checksit ran with, any errors found, and any warnings generated.

Configuration
-------------

.. code-block:: text

    Running with:
        Template: OFF
        Spec Files: ['ncas-amof-2.1.0/amof-file-name', 'ncas-amof-2.1.0/amof-common-land', 'ncas-amof-2.1.0/amof-mean-winds', 'ncas-amof-2.1.0/amof-global-attrs']
        Datafile: ncas-sonic-6_cvao_20241101_mean-winds_v1.0.nc


    ---------------- Running checks ------------------


This section summarises the configuration used when running checksit, including:

* The template file used, if any, or "OFF" if template checking was disabled.
* The list of specification files applied during the checks, or "None" if none used.
* The data file that was checked.

Errors
------

.. code-block:: text

    [FAILED] with 3 errors:

        01. [variable**************:wind_speed]: Attribute 'units' must have definition 'm s-1', not 'mph'.
        02. [variable**************:beaufort_scale]: Invalid variable 'beaufort_scale' found in file.
        03. [global-attributes:******:processing_software_url]*** Value 'Python' does not match regex rule: 'valid-url' - Example valid value 'https://github.com'.

This section lists any errors found during the checks. Each error includes information about where in the file the error is found (e.g., variable name, global attribute), a description of the error, and details about what was expected versus what was found. Fixing these errors is required for a file to be compliant with the specified checks. If no errors are found, this section of the output is not printed, and the line ``[INFO] File is compliant!`` is printed at the bottom of the checksit output.

Warnings
--------

.. code-block:: text

    [WARNING] 6 warnings about file:

        01. [variable**************:wind_speed_of_gust]: Optional variable does not exist in file.
        02. [variable**************:wind_gust_from_direction]: Optional variable does not exist in file.
        03. [variable**************:upward_air_velocity]: Optional variable does not exist in file.
        04. [variable**************:sonic_air_temperature]: Optional variable does not exist in file.
        05. [variable**************:qc_flag_sonic_temperature]: Optional variable does not exist in file.
        06. [variable**************:qc_flag_wind_component_upward_air_velocity]: Optional variable does not exist in file.

This section provides any warnings about the file that were generated during the checks. Warnings indicate potential issues or missing optional elements that do not prevent the file from being compliant but may require attention. Each warning includes similar information as errors, detailing where the warning applies and what the issue is. If no warnings are found, this section of the output is not printed.
