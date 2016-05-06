#!/bin/sh

PATH=/home/nobody/NATIONAL_GEODATA/NLCD
IMGFILE=$PATH/nlcd_2011_landcover_2011_edition_2014_03_31.img
RES=$1
SHPFILE=$2
POLYNAME=$3

gdalwarp -r mode -overwrite -tr $RES $RES -cutline $SHPFILE -csql "SELECT * from $SHPFILE WHERE Name LIKE '$POLYNAME'" -crop_to_cutline $IMGFILE tempfile.img
gdal_translate -ot Float32 -of AAIGrid tempfile.img $OUTPUT_FNAME 

