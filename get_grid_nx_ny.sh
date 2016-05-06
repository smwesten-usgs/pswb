#!/bin/bash

if [ ! -f $1 ]; then
    echo "File $1 not found while attempting to determine grid extents."
fi  

NXNY=$(/usr/bin/gdalinfo $1 | /usr/bin/grep "Size is" | /usr/bin/sed "s/Size is //g" | /usr/bin/tr -d "[(,])" )

echo -n $NXNY
