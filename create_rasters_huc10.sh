#!/bin/sh

die() {
  echo >&2 "$@"
  exit 1
}

[ "$#" -ge 4 ] || die "usage: $BASH_SOURCE [ huc10 # ] [ desired resolution ] [ start date ] [ end date ] { desired output pathname }"

#PATH=/home/nobody/NATIONAL_GEODATA/PSU_CONUS_SOILS
IMGFILE=/home/nobody/NATIONAL_GEODATA/NLCD/nlcd_2011_landcover_2011_edition_2014_03_31.img
FQ_SHPFILE=/home/nobody/NATIONAL_GEODATA/PSU_CONUS_SOILS/CONUS_SOILS_NAD83.shp
FQ_SHPFILE2=/home/nobody/NATIONAL_GEODATA/Quaternary_Atlas/Quaternary_intersected_w_STATSGO_HSG.shp
FQ_VRTFILE=/home/nobody/NATIONAL_GEODATA/HydroSheds/hydroshed_D8.vrt
VRT_PROJ4="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
PROJ4="+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

MASK_SHPFILE='/home/nobody/NATIONAL_GEODATA/WBD_National/WBDHU10_AEA_NAD83.shp'

SHPFILE=WBDHU10_AEA_NAD83.shp
BASENAME=WBDHU10_AEA_NAD83
POLYNAME=$1
RES=$2
START_DATE=$3
END_DATE=$4
OUTPATH=$5

OUTPUT_NLCD_NAME="NLCD_2011_landcover_""$RES""m_huc10_""$POLYNAME.asc"
OUTPUT_AWC_NAME="AWC_IN_FT_""$RES""m_huc10_""$POLYNAME.asc"
OUTPUT_SOILS_NAME="QUATERNARY_SOILS_GRP_""$RES""m_huc10_""$POLYNAME.asc"
OUTPUT_D8_FLOWDIR_NAME="D8_FLOW_DIRECTION_""$RES""m_huc10_""$POLYNAME.asc"
OUTPUT_SWB_CTL_NAME="recharge_""$RES""m_huc10_""$POLYNAME.ctl"

echo NLCD NAME: $OUTPUT_NLCD_NAME

TEMPTIF1="$OUTPATH"tempfile.tif
TEMPIMG="$OUTPATH"tempfile.img
TEMPTIF2="$OUTPATH"tempfile2.tif
LOCAL_SHP="$OUTPATH"local_shape.shp
LOCAL_BASENAME='local_shape'



echo "Creating local basin shapefile. File= $LOCAL_SHP"
/usr/bin/ogr2ogr -sql "SELECT * from $BASENAME WHERE HUC10="\'"$POLYNAME"\' $LOCAL_SHP $MASK_SHPFILE
wait


EXTENTS=$( ./get_shapefile_extent.sh "$LOCAL_SHP" "$LOCAL_BASENAME" )

echo "Rasterizing available water capacity shapefile."
/usr/bin/gdal_rasterize -a 'AWC100INFT' -te $EXTENTS -tr $RES $RES $FQ_SHPFILE $TEMPTIF1
#/usr/bin/gdalwarp -r near -overwrite -dstnodata -9999. -te $EXTENTS -tr $RES $RES -cutline $MASK_SHPFILE -csql "SELECT * from $BASENAME WHERE HUC10="\'"$POLYNAME"\' -crop_to_cutline  tempfile.tif tempfile2.tif
/usr/bin/gdalwarp -r near -overwrite -dstnodata -9999. -te $EXTENTS -tr $RES $RES -csql "SELECT * from $BASENAME WHERE HUC10="\'"$POLYNAME"\' "$TEMPTIF1" "$TEMPTIF2"
/usr/bin/gdal_translate -ot Float32 -co "DECIMAL_PRECISION=2" -a_nodata -9999. -of AAIGrid $TEMPTIF2 "$OUTPATH"$OUTPUT_AWC_NAME

echo "Rasterizing simple glacial units shapefile."
/usr/bin/gdal_rasterize -a 'sim_unit' -te $EXTENTS -tr $RES $RES $FQ_SHPFILE2 $TEMPTIF1
/usr/bin/gdalwarp -r near -overwrite -dstnodata -9999. -tr $RES $RES -csql "SELECT * from $BASENAME WHERE HUC10="\'"$POLYNAME"\' $TEMPTIF1 $TEMPTIF2
/usr/bin/gdal_translate -ot Int32 -a_nodata -9999 -of AAIGrid $TEMPTIF2 "$OUTPATH"$OUTPUT_SOILS_NAME

echo "Creating landcover subset."
#/usr/bin/gdalwarp -r mode -overwrite -dstnodata -9999 -te $EXTENTS -tr $RES $RES -t_srs "$PROJ4" -te_srs "$PROJ4" -cutline $MASK_SHPFILE -csql "SELECT * from $BASENAME WHERE HUC10="\'"$POLYNAME"\' -crop_to_cutline  "$IMGFILE" tempfile.tif
/usr/bin/gdalwarp -r mode -overwrite -ot Int32 -of HFA -srcnodata 0 -dstnodata -9999 -te $EXTENTS -tr $RES $RES  -cutline $MASK_SHPFILE -csql "SELECT * from $BASENAME WHERE HUC10="\'"$POLYNAME"\' -crop_to_cutline  "$IMGFILE" $TEMPIMG
/usr/bin/gdal_translate -ot Int32 -a_nodata -9999 -of AAIGrid $TEMPIMG "$OUTPATH""$OUTPUT_NLCD_NAME" 

echo "Extracting D8 flow direction grid."
/usr/bin/gdalwarp -ot Int32 -r near -s_srs "$VRT_PROJ4" -t_srs "$PROJ4" -te $EXTENTS -overwrite -csql "SELECT * from $BASENAME WHERE HUC10="\'"$POLYNAME"\' $FQ_VRTFILE $TEMPTIF1
/usr/bin/gdal_translate -ot Int32 -a_nodata -9 -tr $RES $RES -co "FORCE_CELLSIZE=TRUE" -of AAIGrid $TEMPTIF1 "$OUTPATH"$OUTPUT_D8_FLOWDIR_NAME


LLX=$( echo $EXTENTS | awk '{print $1}')
LLY=$( echo $EXTENTS | awk '{print $2}')
NXNY=$( ./get_grid_nx_ny.sh "$OUTPATH"$OUTPUT_NLCD_NAME )
echo LLCOORD: $LLX  $LLY
echo NXNY: $NXNY

echo "GRID $NXNY $LLX $LLY $RES" > "$OUTPATH"$OUTPUT_SWB_CTL_NAME

./write_swbfile.sh $OUTPUT_NLCD_NAME $OUTPUT_AWC_NAME $OUTPUT_SOILS_NAME $OUTPUT_D8_FLOWDIR_NAME "$OUTPATH"$OUTPUT_SWB_CTL_NAME

echo "START_DATE $START_DATE" >> "$OUTPATH"$OUTPUT_SWB_CTL_NAME
echo "END_DATE $END_DATE" >> "$OUTPATH"$OUTPUT_SWB_CTL_NAME

echo "$OUTPATH"$OUTPUT_SWB_CTL_NAME