#!/bin/sh

cd results 

FILES=$( ls *output*.tar )

for file in $FILES 
do
  tar -xvf $file
done

ncfiles=$( ls *potential_recharge_1980_1980_*.nc )

swb_merge $ncfiles
