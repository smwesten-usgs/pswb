#!/bin/sh
INPUT_PATH=$1
INPUT_IMG=$2
OUTPUT_FNAME=$3
SHPFILE=$4
RES=$5
BASE=$(basename $SHPFILE .shp)
# EXTENT=$(ogrinfo -so $SHPFILE $BASE | grep Extent \
# | sed 's/Extent: //g' | sed 's/(//g' | sed 's/)//g' \
# | sed 's/ - /, /g')

# echo $EXTENT

gdalwarp -r mode -overwrite -tr $RES $RES -cutline $SHPFILE -csql "SELECT * from GenMod_Unconfined WHERE Name LIKE 'WeldonRiver'" -crop_to_cutline $INPUT_IMG tempfile.img
gdal_translate -ot Float32 -of AAIGrid tempfile.img $OUTPUT_FNAME 

