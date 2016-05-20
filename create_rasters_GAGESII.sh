#!/bin/sh

die() {
  echo >&2 "$@"
  exit 1
}

[ "$#" -eq 4 ] || die "usage: $BASH_SOURCE [ huc8 # ] [ desired resolution ] [ start date ] [ end date ]"

#PATH=/home/nobody/NATIONAL_GEODATA/PSU_CONUS_SOILS
IMGFILE=/home/nobody/NATIONAL_GEODATA/NLCD/nlcd_2011_landcover_2011_edition_2014_03_31.img
FQ_SHPFILE=/home/nobody/NATIONAL_GEODATA/PSU_CONUS_SOILS/CONUS_SOILS_NAD83.shp
FQ_SHPFILE2=/home/nobody/NATIONAL_GEODATA/Quaternary_Atlas/Merged_SM_and_QA.shp
FQ_VRTFILE=/home/nobody/NATIONAL_GEODATA/HydroSheds/hydroshed_D8.vrt
VRT_PROJ4="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
PROJ4="+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

#MASK_SHPFILE='/home/nobody/NATIONAL_GEODATA/WBD_National/WBDHU8_AEA_NAD83.shp'
MASK_SHPFILE='/home/nobody/NATIONAL_GEODATA/Reitz_BF_Separations/Reitz_BASEFLOW_stats.shp'

#SHPFILE=WBDHU8_AEA_NAD83.shp
#BASENAME=WBDHU8_AEA_NAD83

SHPFILE=Reitz_BASEFLOW_stats.shp
BASENAME=Reitz_BASEFLOW_stats

POLYNAME=$1
RES=$2
START_DATE=$3
END_DATE=$4

#FIELDNAME='HUC8'
FIELDNAME='GAGE_ID'

OUTPUT_NLCD_NAME="NLCD_2011_landcover_""$RES""m_huc8_""$POLYNAME.asc"
OUTPUT_AWC_NAME="AWC_IN_FT_""$RES""m_huc8_""$POLYNAME.asc"
OUTPUT_SOILS_NAME="QUATERNARY_SOILS_GRP_""$RES""m_huc8_""$POLYNAME.asc"
OUTPUT_D8_FLOWDIR_NAME="D8_FLOW_DIRECTION_""$RES""m_huc8_""$POLYNAME.asc"
OUTPUT_SWB_CTL_NAME="recharge_""$RES""m_huc8_""$POLYNAME.ctl"

echo NLCD NAME: $OUTPUT_NLCD_NAME

TEMPTIF1=tempfile.tif
TEMPIMG=tempfile.img
TEMPTIF2=tempfile2.tif
LOCAL_SHP=local_shape.shp
LOCAL_BASENAME='local_shape'


echo "Creating local basin shapefile. File= $LOCAL_SHP"
/usr/bin/ogr2ogr -sql "SELECT * from $BASENAME WHERE ""$FIELDNAME""="\'"$POLYNAME"\' $LOCAL_SHP $MASK_SHPFILE
wait


EXTENTS=$( ./get_shapefile_extent.sh "$LOCAL_SHP" "$LOCAL_BASENAME" )

/usr/bin/gdal_rasterize -a 'AWC100INFT' -te $EXTENTS -tr $RES $RES $FQ_SHPFILE $TEMPTIF1
#/usr/bin/gdalwarp -r near -overwrite -dstnodata -9999. -te $EXTENTS -tr $RES $RES -cutline $MASK_SHPFILE -csql "SELECT * from $BASENAME WHERE HUC8="\'"$POLYNAME"\' -crop_to_cutline  tempfile.tif tempfile2.tif
/usr/bin/gdalwarp -r near -overwrite -dstnodata -9999. -te $EXTENTS -tr $RES $RES -csql "SELECT * from $BASENAME WHERE ""$FIELDNAME""="\'"$POLYNAME"\' "$TEMPTIF1" "$TEMPTIF2"
/usr/bin/gdal_translate -ot Float32 -co "DECIMAL_PRECISION=2" -a_nodata -9999. -of AAIGrid $TEMPTIF2 $OUTPUT_AWC_NAME

/usr/bin/gdal_rasterize -a 'SMW_class' -te $EXTENTS -tr $RES $RES $FQ_SHPFILE2 $TEMPTIF1
/usr/bin/gdalwarp -r near -overwrite -dstnodata -9999. -tr $RES $RES -csql "SELECT * from $BASENAME WHERE ""$FIELDNAME""="\'"$POLYNAME"\' $TEMPTIF1 $TEMPTIF2
/usr/bin/gdal_translate -ot Int32 -a_nodata -9999 -of AAIGrid $TEMPTIF2 $OUTPUT_SOILS_NAME

#/usr/bin/gdalwarp -r mode -overwrite -dstnodata -9999 -te $EXTENTS -tr $RES $RES -t_srs "$PROJ4" -te_srs "$PROJ4" -cutline $MASK_SHPFILE -csql "SELECT * from $BASENAME WHERE HUC8="\'"$POLYNAME"\' -crop_to_cutline  "$IMGFILE" tempfile.tif
/usr/bin/gdalwarp -r mode -overwrite -ot Int32 -of HFA -srcnodata 0 -dstnodata -9999 -te $EXTENTS -tr $RES $RES  -cutline $MASK_SHPFILE -csql "SELECT * from $BASENAME WHERE ""$FIELDNAME""="\'"$POLYNAME"\' -crop_to_cutline  "$IMGFILE" $TEMPIMG
/usr/bin/gdal_translate -ot Int32 -a_nodata -9999 -of AAIGrid $TEMPIMG "$OUTPUT_NLCD_NAME" 

/usr/bin/gdalwarp -ot Int32 -r near -s_srs "$VRT_PROJ4" -t_srs "$PROJ4" -te $EXTENTS -overwrite -csql "SELECT * from $BASENAME WHERE ""$FIELDNAME""="\'"$POLYNAME"\' $FQ_VRTFILE $TEMPTIF1
/usr/bin/gdal_translate -ot Int32 -a_nodata -9 -tr $RES $RES -co "FORCE_CELLSIZE=TRUE" -of AAIGrid $TEMPTIF1 $OUTPUT_D8_FLOWDIR_NAME


LLX=$( echo $EXTENTS | awk '{print $1}')
LLY=$( echo $EXTENTS | awk '{print $2}')
NXNY=$( ./get_grid_nx_ny.sh $OUTPUT_NLCD_NAME )

NX=$(echo $NXNY | awk '{print $1}' )
NY=$(echo $NXNY | awk '{print $2}' )

GRID_SPEC="GRID $NXNY $LLX $LLY $RES"

./write_swbfile_1_0.sh $OUTPUT_NLCD_NAME $OUTPUT_AWC_NAME $OUTPUT_SOILS_NAME $OUTPUT_D8_FLOWDIR_NAME $OUTPUT_SWB_CTL_NAME $LLX $LLY $NX $NY $RES $START_DATE $END_DATE

echo "$OUTPUT_SWB_CTL_NAME"