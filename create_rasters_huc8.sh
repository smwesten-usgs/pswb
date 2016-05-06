#!/bin/bash

die() {
  echo >&2 "$@"
  exit 1
}


[ "$#" -eq 2 ] || die "usage: $BASH_SOURCE [ huc8 # ] [ desired resolution ]"


huc8=$1
res=$2

for huc in $(exec ./list_huc10.sh "$huc8" )
do

  echo Creating $resmm rasters for huc10: $huc
  exitcode=$(exec ./create_rasters_huc10.sh $huc $res)

done