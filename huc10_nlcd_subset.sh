#!/bin/sh

PATH=/home/nobody/NATIONAL_GEODATA/NLCD
IMGFILE=$PATH/nlcd_2011_landcover_2011_edition_2014_03_31.img
FQ_SHPFILE='/home/nobody/NATIONAL_GEODATA/WBD_National/WBDHU10.shp'

SHPFILE=WBDHU10.shp
BASENAME=WBDHU10
POLYNAME=$1
RES=$2
OUTPUT_FNAME=NLCD_2011_landcover_$RESm__huc10_$1.asc

/usr/bin/gdalwarp -r mode -overwrite -dstnodata -9999 -tr $RES $RES -cutline $FQ_SHPFILE -csql "SELECT * from $BASENAME WHERE HUC10="\'"$POLYNAME"\' -crop_to_cutline  "$IMGFILE" tempfile.tif
/usr/bin/gdal_translate -ot Int32 -a_nodata -9999 -of AAIGrid tempfile.tif "$OUTPUT_FNAME" 

