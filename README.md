# checksit

File-checking made simple

## Installation

Create a venv, then install dependencies:

```
pip install -r requirements.txt
pip install -e .
```

## Usage

```
checksit check /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc

checksit check /group_workspaces/jasmin2/ukcp18/UKcordex/UKCP18_UI_test/tas_rcp85_land-rcm_uk_12km_AD_mon_198012-208011.nc

# Verbose
checksit check --verbose /group_workspaces/jasmin2/ukcp18/UKcordex/UKCP18_UI_test/tas_rcp85_land-rcm_uk_12km_AD_mon_198012-208011.nc

checksit check --verbose /group_workspaces/jasmin2/ukcp18/UKcordex-laura/tasmax_rcp85_land-rcm_uk_12km_EC-EARTH_r12i1p1_HIRHAM5_day_19801201-19901130.nc
```

## Features

### Mapping the names of attributes or sub-dictionaries (such as variables)

Say you want to compare the contents of a data file with a template file, but you know that
a variable has been given a different NetCDF variable ID in the data file, you can tell the 
checker to map the name as follows:

```
$ checksit check  -m cltAnom=cloud_area_fraction  /gws/nopw/j04/cmip6_prep_vol1/ukcp18/data/land-prob/v20211110/uk/25km/rcp85/sample/b8110/30y/cltAnom/mon/v20211110/cltAnom_rcp85_land-prob_uk_25km_sample_b8110_30y_mon_20091201-20991130.nc
```

This will find the "cloud_area_fraction" variable ID in the data file and match it to the 
"cltAnom" variable dictionary in the template.

### Connecting to controlled vocabularies

```
$ checksit check  -m cltAnom=cloud_area_fraction  /gws/nopw/j04/cmip6_prep_vol1/ukcp18/data/land-prob/v20211110/uk/25km/rcp85/sample/b8110/30y/cltAnom/mon/v20211110/cltAnom_rcp85_land-prob_uk_25km_sample_b8110_30y_mon_20091201-20991130.nc

Running with:
        Template: template-cache/cltAnom_rcp85_land-prob_uk_25km_sample_b8110_30y_mon_20091201-20991130.cdl
        Datafile: /gws/nopw/j04/cmip6_prep_vol1/ukcp18/data/land-prob/v20211110/uk/25km/rcp85/sample/b8110/30y/cltAnom/mon/v20211110/cltAnom_rcp85_land-prob_uk_25km_sample_b8110_30y_mon_20091201-20991130.nc


---------------- Running checks ------------------

[FAILED] with 2 errors:

        01. [variables] sample:units: 'UNDEFINED' does not match expected: '1'
        02. [global_attributes] 'CF-1.7' not in vocab options: ['CF-1.5', 'CF-1.6']
```


## Ideas

```
template_cache=my-template-cache
basedir=/badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day

for latest_dir in $(find -L $basedir -type d -name latest); do
    first_file=$(ls $latest_dir/*.nc | head -1)
    facets=$(basename $first_file | cut -d_ -f1-7 | sed 's/_/ /g')
#rss_rcp85_land-cpm_uk_2.2km_01_day_19801201-19811130.nc
    echo $facets
    ncdump -h $first_file
done

```
