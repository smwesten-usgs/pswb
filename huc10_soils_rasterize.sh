#!/bin/sh

PATH=/home/nobody/NATIONAL_GEODATA/PSU_CONUS_SOILS
FQ_SHPFILE="$PATH/CONUS_SOILS_NAD83.shp"
FQ_SHPFILE2=/home/nobody/NATIONAL_GEODATA/Quaternary_Atlas/Quaternary_intersected_w_STATSGO_HSG.shp
FQ_VRTFILE=/home/nobody/NATIONAL_GEODATA/HydroSheds/hydroshed_D8.vrt
VRT_PROJ4="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
PROJ4="+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

MASK_SHPFILE='/home/nobody/NATIONAL_GEODATA/WBD_National/WBDHU10.shp'

SHPFILE=WBDHU10.shp
BASENAME=WBDHU10
POLYNAME=$1

OUTPUT_NLCD_NAME=NLCD_2011_landcover_$RESm__huc10_$POLYNAME.asc
OUTPUT_AWC_NAME=AWC_IN_FT_$RESm__huc10_$POLYNAME.asc
OUTPUT_SOILS_NAME=QUATERNARY_SOILS_GRP_$RESm__huc10_$POLYNAME.asc
OUTPUT_D8_FLOWDIR_NAME=D8_FLOW_DIRECTION_$RESm__huc10_$POLYNAME.asc

echo \'$OUTPUT_NLCD_NAME\'

EXTENTS=$( ./get_grid_extents.sh $OUTPUT_NLCD_NAME )
#RES=$(/usr/bin/gdalinfo $OUTPUT_NLCD_NAME | grep 'Pixel Size' | sed "s/Pixel Size = //g;s/,.*//g" | tr -d '[(,])' )
RES=$( ./get_grid_resolution.sh $OUTPUT_NLCD_NAME )

#PROJ4=$( ./get_proj4.sh $OUTPUT_NLCD_NAME | /usr/bin/sed -e 's/[ ]*$//' | /usr/bin/tr "'" '"' )

#echo /usr/bin/gdal_rasterize -a 'AWC100INFT' -te $EXTENTS -tr $RES $RES FQ_SHAPEFILE tempfile.tif
/usr/bin/gdal_rasterize -a 'AWC100INFT' -te $EXTENTS -tr $RES $RES $FQ_SHPFILE tempfile.tif
/usr/bin/gdalwarp -r mode -overwrite -dstnodata -9999. -tr $RES $RES -cutline $MASK_SHPFILE -csql "SELECT * from $BASENAME WHERE HUC10="\'"$POLYNAME"\' -crop_to_cutline  tempfile.tif tempfile2.tif
/usr/bin/gdal_translate -ot Float32 -a_nodata -9999. -of AAIGrid tempfile2.tif $OUTPUT_AWC_NAME

/usr/bin/gdal_rasterize -a 'sim_unit' -te $EXTENTS -tr $RES $RES $FQ_SHPFILE2 tempfile.tif
/usr/bin/gdalwarp -r mode -overwrite -dstnodata -9999. -tr $RES $RES -cutline $MASK_SHPFILE -csql "SELECT * from $BASENAME WHERE HUC10="\'"$POLYNAME"\' -crop_to_cutline  tempfile.tif tempfile2.tif
/usr/bin/gdal_translate -ot Int32 -a_nodata -9999 -of AAIGrid tempfile2.tif $OUTPUT_SOILS_NAME

/usr/bin/gdalwarp -ot Int32 -r mode -co "FORCE_CELLSIZE=TRUE" -s_srs "$VRT_PROJ4" -t_srs "$PROJ4" -te_srs "$PROJ4" -te $EXTENTS -overwrite -cutline $MASK_SHPFILE -csql "SELECT * from $BASENAME WHERE HUC10="\'"$POLYNAME"\' -crop_to_cutline $FQ_VRTFILE tempfile.tif
/usr/bin/gdal_translate -ot Int32 -a_nodata -9999 -co "FORCE_CELLSIZE=TRUE" -of AAIGrid tempfile.tif $OUTPUT_D8_FLOWDIR_NAME

echo $EXTENTS
echo $RES
