# checksit

[![Documentation Status](https://readthedocs.org/projects/checksit/badge/?version=latest)](https://checksit.readthedocs.io/en/latest)

File-checking made simple


## Documentation

See the [Read The Docs page](https://checksit.readthedocs.io/en/latest) for more
details on how to install and run checksit.

Visit the [JASMIN help page](https://help.jasmin.ac.uk/docs/software-on-jasmin/community-software-checksit/)
for guidance on how to use checksit on JASMIN.


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

A brief description of how to use checksit is given here. For more detail, visit the
[documentation site](https://checksit.readthedocs.io/en/latest).

### checksit check

To check a file:

```
checksit check /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc
```
* Attempts to find best checks to use for this file, and then runs checks.
* A specific template can be defined using the `-t/--template` flag, or specific specs
can be defined using the `-s/--specs` flag.
