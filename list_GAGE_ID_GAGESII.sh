#!/bin/sh

result=$(ogrinfo -geom=no -WHERE "GLASS='yes' AND MEAN_81_13 > 0." /home/nobody/NATIONAL_GEODATA/Reitz_BF_Separations/Reitz_BASEFLOW_stats.shp Reitz_BASEFLOW_stats | /usr/bin/grep 'GAGE_ID (String)' | /usr/bin/gawk -F "=" '{print $2}')

rm -f "temp_GAGES_II.txt"

for item in $result
do

  echo $item >> "temp_GAGES_II.txt"

done

sort "temp_GAGES_II.txt" > "GAGE_ID_list__GAGES_II.txt"

rm -f "temp_GAGES_II.txt"
