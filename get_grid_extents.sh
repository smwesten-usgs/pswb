#!/bin/bash

if [ ! -f $1 ]; then
    echo "File $1 not found while attempting to determine grid extents."
fi  

EXTENT=$(/usr/bin/gdalinfo $1 | /usr/bin/grep "Lower Left\|Upper Right" | /usr/bin/sed "s/Lower Left  //g;s/Upper Right //g;s/).*//g" | /usr/bin/tr -d "[(,])" )

echo -n $EXTENT
