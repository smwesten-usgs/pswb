#!/bin/sh

result=$(ogrinfo -geom=no -WHERE GENERALMOD=\'"$1"\' /home/nobody/NATIONAL_GEODATA/WBD_National/WBDHU8.shp WBDHU8 | /usr/bin/grep 'HUC8 (String)' | /usr/bin/gawk -F "=" '{print $2}')

rm -f "temp_$1.txt"

for item in $result
do

  echo $item >> "temp_$1.txt"

done

sort "temp_$1.txt" > "huc8_list__general_model_type_$1.txt"

rm -f "temp_$1.txt"