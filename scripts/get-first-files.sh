#!/bin/bash

template_cache=template-cache
mkdir -p $template_cache

basedir=$1
#/badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day

if [[ "$basedir" =~ (land-cpm|land-rcm|land-gcm) ]]; then
    dirs=$(find -L $basedir -type d -name latest | grep "/01/")
else
    dirs=$(find -L $basedir -type d -name latest | grep rcp85)
fi


echo "[INFO] Directory count: $(wc -l $dirs)"

for latest_dir in $dirs ; do
    first_file=$(ls $latest_dir/*.nc | head -1)
 
    if [ ! "$first_file" ]; then
        echo "[WARNING] Found nothing at: $latest_dir/"
        continue
    fi

    fbase=$(basename $first_file | sed 's/\.nc//g')
    facets=$(echo $fbase | cut -d_ -f1-7 | sed 's/_/ /g')
    #rss_rcp85_land-cpm_uk_2.2km_01_day_19801201-19811130.nc
    #echo $facets

    dumpfile=$template_cache/${fbase}.cdl

    if [ ! -f "$dumpfile" ]; then
        ncdump -h $first_file > $dumpfile
        echo "[INFO] Wrote: $dumpfile"
    fi

done
