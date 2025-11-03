# checksit

[![Documentation Status](https://readthedocs.org/projects/checksit/badge/?version=latest)](https://checksit.readthedocs.io/en/latest)

File-checking made simple

## Installation

Create a venv, then install, either directly from GitHub:
```
pip install git+https://github.com/cedadev/checksit.git
```
or clone the repository and install
```
git clone https://github.com/cedadev/checksit
cd checksit
pip install .
```


## Usage

A brief description of how to use checksit is given here. For more detail, visit the [documentation site](https://checksit.readthedocs.io/en/latest).

checksit is comprised of four key components - [check](#checksit-check), [describe](#checksit-describe), [show-specs](#checksit-show-specs), and [summary](#checksit-summary)


## checksit check

Check file against a template.

### Basic Usage

```
checksit check /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc
```
* Checks format of file.
* checksit searches its template cache for a similar file to compare against


### Main Features

#### Define template
```
checksit check --template=template-cache/rls_rcp85_land-cpm_uk_2.2km_01_day_19801201-19811130.cdl /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc
```
* Use `--template` flag to define a template to use
* Template can be in template-cache or any file user has access to
* Note: cdl files are a representation of a netCDF file, being the output from `ncdump -h` on the netCDF file


#### Map variable names
```
checksit check -m cltAnom=cloud_area_fraction /gws/nopw/j04/cmip6_prep_vol1/ukcp18/data/land-prob/v20211110/uk/25km/rcp85/sample/b8110/30y/cltAnom/mon/v20211110/cltAnom_rcp85_land-prob_uk_25km_sample_b8110_30y_mon_20091201-20991130.nc
```
* Allows mapping of variable name, for the case that the name of a variable is different between the file to be checked and the template
* Format - `-m <template variable name>=<file variable name>`
* Multiple mappings should be comma separated


#### Ignore attributes
```
checksit check --ignore-attrs=global_attributes:time_coverage_start,global_attributes:time_coverage_end,global_attributes:tracking_id /neodc/esacci/sea_ice/data/sea_ice_thickness/L3C/envisat/v2.0/SH/2012/ESACCI-SEAICE-L3C-SITHICK-RA2_ENVISAT-SH50KMEASE2-201202-fv2.0.nc
```
* Define attributes to ignore in checking


#### Define additional rules for checking
```
checksit check --rules=global_attributes:id=rule-func:match-file-name:lowercase:no-extension /neodc/esacci/sea_ice/data/sea_ice_thickness/L3C/envisat/v2.0/SH/2012/ESACCI-SEAICE-L3C-SITHICK-RA2_ENVISAT-SH50KMEASE2-201202-fv2.0.nc
```
* Check items against defined rules
* Format - `<what to check>=<rule type>:<function/check>[:<extras>[:<extras>...]]`
* Four options for `<rule type>`:
  * `rule-func` - check item against a defined function, 4 options:
    * `match-file-name` - item must be the same as the file name, allowing for formatting through `<extras>` - `lowercase`, `uppercase`, `no_extension` - example: `global_attributes:id=rule-func:match-file-name:lowercase:no-extension`
    * `match-one-of` - item must be the same as one of the `<extras>` given. Multiple options should be separated by a `|` and surrounded by double quotation marks - example: `global_attributes:project=rule-func:match-one-of:"ukcp18|ukcp09"`
    * `match-one-or-more-of` - item must be the same as one or more of the `<extras>` given. Multiple options should be separated by a `|` and surrounded by double quotation marks - example: `global_attributes:contact=rule-func:match-one-or-more-of:"ukcpproject@metoffice.gov.uk|UKCP Team|MOHC"`
    * `string-of-length` - item must be the same length as given `<extra>` or greater if `+` is given at end of `<extra>` - example: `global_attributes:project=rule-func:string-of-length:10,global_attributes:contact=rule-func:string-of-length:100+`
  * `type-rule` - check item is of type as defined in `<extra>` - example: `transverse_mercator:false_northing=type-rule:integer`
  * `regex` - check item for regular expression match - example: `global_attributes:project=regex:ukcp18`
  * `regex-rule` - check item matches pre-defined regex rule, name of which is given in `<extra>`
    * current options are `integer`,`valid-email`,`valid-url`,`valid-url-or-na`,`match:vN.M`,`datetime`,`datetime-or-na`,`number`


### Additional Options

#### specs
```
checksit check --specs=ceda-base /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc
```
* Checks file against a given specification. For more info, see [checksit show-specs](#checksit-show-specs)


#### auto-cache
```
checksit check --auto-cache --template=/badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/08/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_08_day_20671201-20681130.nc /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc
```
* Create a cache of the given template to add to add to checksit's template_cache


#### verbose
```
checksit check --verbose /group_workspaces/jasmin2/ukcp18/incoming-astephen/ukcordex-example/tasmax_rcp85_land-rcm_uk_12km_EC-EARTH_r12i1p1_HIRHAM5_day_19801201-19901130.nc
```
* Print additional information



## checksit describe

```
checksit describe
```
* Prints docstring of rules that can be used in `checksit check --rules`
* Individual rules can be printed out, e.g. `checksit describe match-one-of`



## checksit show-specs

```
checksit show-specs <spec-id>
```
* Prints out specs for a given spec-id, e.g. `ceda-base`
* sped-ids are saved in checksit/specs/groups



## checksit summary

* Summarises output from a number of log files created through `checksit check`
