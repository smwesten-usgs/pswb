#!/bin/sh

die() {
  echo >&2 "$@"
  exit 1
}

[ "$#" -eq 2 ] || die "usage: $BASH_SOURCE [ shapefile name ] [ layer name ]"
if [ ! -f $1 ]; then
    echo "File $1 not found while attempting to determine shapefile extents."
fi  

BASENAME=$2

EXTENT=$( /usr/bin/ogrinfo $1 $BASENAME | /usr/bin/grep "Extent" | /usr/bin/sed "s/Extent: //g" | /usr/bin/tr -d "[(,])\-" )

echo -n $EXTENT
