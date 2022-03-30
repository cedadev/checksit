checksit check /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc

# Specify your own template in the template cache
checksit check --template=template-cache/rls_rcp85_land-cpm_uk_2.2km_01_day_19801201-19811130.cdl /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc

# Specify your own archive file as template
checksit check --template=/badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/08/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_08_day_20671201-20681130.nc \
 /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc

# Switch on automatic-caching when checking a file
checksit check --auto-cache --template=/badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/08/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_08_day_20671201-20681130.nc \
 /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc

checksit check --verbose /group_workspaces/jasmin2/ukcp18/UKcordex-laura/tasmax_rcp85_land-rcm_uk_12km_EC-EARTH_r12i1p1_HIRHAM5_day_19801201-19901130.nc

checksit check /badc/ukcp09/data/gridded-land-obs/gridded-land-obs-monthly/grid/ascii/rainfall/2016/ukcp09_gridded-land-obs-monthly_5km_rainfall_201610.txt

checksit check /badc/ukmo-assim/data/standard/2022/ukmo-nwp-strat_gbl-std_2022020112_u-v-gph-t-w.pp

# With auto-cache (will write YAML representation to template-cache directory)
checksit check --auto-cache /badc/ukmo-assim/data/standard/2022/ukmo-nwp-strat_gbl-std_2022020112_u-v-gph-t-w.pp

checksit check -m cltAnom=cloud_area_fraction /gws/nopw/j04/cmip6_prep_vol1/ukcp18/data/land-prob/v20211110/uk/25km/rcp85/sample/b8110/30y/cltAnom/mon/v20211110/cltAnom_rcp85_land-prob_uk_25km_sample_b8110_30y_mon_20091201-20991130.nc

# Vocabs checked as well
checksit check -m cltAnom=cloud_area_fraction /gws/nopw/j04/cmip6_prep_vol1/ukcp18/data/land-prob/v20211110/uk/25km/rcp85/sample/b8110/30y/cltAnom/mon/v20211110/cltAnom_rcp85_land-prob_uk_25km_sample_b8110_30y_mon_20091201-20991130.nc

checksit check --ignore-attrs=global_attributes:time_coverage_start,global_attributes:time_coverage_end,global_attributes:tracking_id /neodc/esacci/sea_ice/data/sea_ice_thickness/L3C/envisat/v2.0/SH/2012/ESACCI-SEAICE-L3C-SITHICK-RA2_ENVISAT-SH50KMEASE2-201202-fv2.0.nc

# ESACCI fire
checksit check /gws/nopw/j04/esacci_portal/fire/SYN/FireCCIS310/Grid/20190101-ESACCI-L4_FIRE-BA-SYN-fv1.0.nc 

checksit check --rules=global_attributes:id=rule_func:match-file-name:lowercase:no-extension --ignore-attrs=global_attributes:time_coverage_start,global_attributes:time_coverage_end,global_attributes:tracking_id /neodc/esacci/sea_ice/data/sea_ice_thickness/L3C/envisat/v2.0/SH/2012/ESACCI-SEAICE-L3C-SITHICK-RA2_ENVISAT-SH50KMEASE2-201202-fv2.0.nc

# Match a global attribute to a regex
checksit check --rules=global_attributes:project=regex:ukcp18 /gws/nopw/j04/cmip6_prep_vol1/ukcp18/data/land-prob/v20211110/uk/25km/rcp85/sample/b8110/30y/cltAnom/mon/v20211110/cltAnom_rcp85_land-prob_uk_25km_sample_b8110_30y_mon_20091201-20991130.nc 

