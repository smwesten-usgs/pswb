#!/bin/sh

if [ ! -f $1 ]; then
    echo "File $1 not found while attempting to determine grid extents."
fi  

RES=$( /usr/bin/gdalinfo $1 | /usr/bin/grep "Pixel Size" | /usr/bin/sed "s/Pixel Size = //g;s/,.*//g" | /usr/bin/tr -d "[(,])" )

echo -n $RES
