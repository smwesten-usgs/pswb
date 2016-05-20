#!/bin/sh

RESOLUTION=300
START_DATE=1980
END_DATE=2013

die() {
  echo >&2 "$@"
  exit 1
}

[ "$#" -eq 1 ] || die "usage: $BASH_SOURCE [ huc8 sort number ]"

sim_num=$(expr $1 + 1)
proc_num="$1"
#linenumber=$sim_num
linenumber=$[$RANDOM % 229]

echo proc_num, sim_num, line_number: $proc_num, $sim_num, $linenumber

export HDF5_DISABLE_VERSION_CHECK=1

# the following are here simply to spit out the values so they
# will be included in the logfile.
date
ls -l

echo "Machine name: $(uname -n)"

tar xvf swbfiles.tar
filename="GAGE_ID_list__GAGES_II.txt"
numlines=$(wc -l $filename | cut -d ' ' -f1)

if [ ! -e "$filename" ]
then
  die "FILE NOT FOUND: could not find $filename."
elif [ $linenumber -gt $numlines ]
then
  die "FILE $filename has $numlines lines; you tried to access line $linenumber."
else
  huc8=$(sed -n "${linenumber}p" "$filename")	
fi

huc8=$(sed -n "${linenumber}p" "$filename")

OUTPUT_SWB_CTL_NAME="recharge_""$RESOLUTION""m_huc8_""$huc8.ctl"

#args: [ huc10 # ] [ desired resolution ] [ start date ] [ end date ] { desired output pathname }
swb_file=$(./create_rasters_GAGESII.sh $huc8 $RESOLUTION $START_DATE $END_DATE )
wait

cat $swb_file


./swb "$OUTPUT_SWB_CTL_NAME"

# need to reference the 'tar' files by PROCESS number (0-based index) not
# by SIMULATION number (1-based index) so that Condor can *find* the  output files.
tar --ignore-failed-read -cvf swb_logfiles_$proc_num.tar SWB_LOG*
tar --ignore-failed-read -cvf swb_output_files_$proc_num.tar $(ls *.asc) $(ls *.csv) $(ls *.png)

ls -l
