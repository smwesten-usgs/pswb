#!/bin/sh

if [ ! -f $1 ]; then
    echo "File $1 not found while attempting to determine PROJ4 string."
fi  

PROJ4=$(/usr/bin/gdalinfo -proj4 $1 | /usr/bin/grep "+proj=" )

echo -n $PROJ4