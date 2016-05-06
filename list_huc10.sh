#!/bin/sh

result=$(ogrinfo -geom=no -WHERE HUC8=\'"$1"\' /home/nobody/NATIONAL_GEODATA/WBD_National/WBDHU10.shp WBDHU10 | /usr/bin/grep 'HUC10 (String)' | /usr/bin/gawk -F "=" '{print $2}')

rm -f "temp_$1.txt"

for item in $result
do

  echo $item >> "temp_$1.txt"

done

sort "temp_$1.txt" > "huc10_list__huc8_$1.txt"

rm -f "temp_$1.txt"