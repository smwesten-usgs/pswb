#!/bin/sh

RESOLUTION=75
START_DATE="01/01/1980"
END_DATE="12/30/1980"
HUC8="10280102"

die() {
  echo >&2 "$@"
  exit 1
}

[ "$#" -eq 1 ] || die "usage: $BASH_SOURCE [ huc10 sort number ]"

sim_num=$(expr $1 + 1)
proc_num="$1"
linenumber=$sim_num

echo proc_num, sim_num: $proc_num, $sim_num

export HDF5_DISABLE_VERSION_CHECK=1

# the following are here simply to spit out the values so they
# will be included in the logfile.
date
ls -l

echo "Machine name: $(uname -n)"

tar xvf swbfiles.tar

filename="huc10_list__huc8_$HUC8.txt"
numlines=$(wc -l $filename | cut -d ' ' -f1)

if [ ! -e "$filename" ]
then
  die "FILE NOT FOUND: could not find $filename."
elif [ $linenumber -gt $numlines ]
then
  die "FILE $filename has $numlines lines; you tried to access line $linenumber."
else
  huc10=$(sed -n "${linenumber}p" "$filename")	
fi

huc10=$(sed -n "${linenumber}p" "$filename")

OUTPUT_SWB_CTL_NAME="recharge_""$RESOLUTION""m_huc10_""$huc10.ctl"

#args: [ huc10 # ] [ desired resolution ] [ start date ] [ end date ] { desired output pathname }
swb_file=$(./create_rasters_huc10.sh $huc10 $RESOLUTION $START_DATE $END_DATE )
wait

./swb2 "$OUTPUT_SWB_CTL_NAME" "--output_prefix=huc$huc10"

./cdo yearsum $(ls *rainfall*.*) huc$huc10_rainfall_annual_$proc_num.nc
./cdo yearsum $(ls *fog*.*) huc$huc10_fog_annual_$proc_num.nc
./cdo yearsum $(ls *potential_recharge*.*) huc$huc10_potential_recharge_annual_$proc_num.nc
./cdo yearsum $(ls *interception*.*) huc$huc10_interception_annual_$proc_num.nc
./cdo yearsum $(ls *irrigation*.*) huc$huc10_irrigation_annual_$proc_num.nc
./cdo yearsum $(ls *runoff*.*) huc$huc10_runoff_annual_$proc_num.nc
./cdo yearsum $(ls *actual_et*.*) huc$huc10_actual_et_annual_$proc_num.nc

# need to reference the 'tar' files by PROCESS number (0-based index) not
# by SIMULATION number (1-based index) so that Condor can *find* the  output files.
tar --ignore-failed-read -cvf swb_logfiles_$proc_num.tar *LOGFILE*.md
tar --ignore-failed-read -cvf swb_output_files_$proc_num.tar $(ls *potential_recharge*.nc) $(ls *tmin*.nc) $(ls *tmax*.nc) $(ls *annual*.nc) *.asc *.csv

ls -l
