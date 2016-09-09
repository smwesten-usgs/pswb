#!/bin/bash

die() {
  echo >&2 "$@"
  exit 1
}

[ "$#" -eq 3 ] || die "usage: $BASH_SOURCE [ directory name ] [ fragment name ] [ output file prefix ]"

if [ ! -d $1 ]; then
    echo "Directory $1 not found while attempting to create virtual raster."
fi


DIRNAME=$1
FRAGMENT=$2
OUTFILE=$3

ORIGINAL_DIR=`pwd`
cd $DIRNAME

ls *"$FRAGMENT"*.asc > filelist.txt

LENGTH=`wc -l < filelist.txt`

[ "$LENGTH" -gt 0 ] || die "No files containing the search term $FRAGMENT could be found."

gdalbuildvrt -input_file_list filelist.txt "$OUTFILE".vrt

cd $ORIGINAL_DIR
