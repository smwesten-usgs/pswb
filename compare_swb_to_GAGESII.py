import tarfile
import os
import glob
import gdal
import shutil
import sys
from gdalconst import *
import numpy as np
import pandas as pd

mydir = '/home/smwesten/Project_Data/NAWQA_GLASS/results'
myworkdir = '/home/smwesten/Project_Data/NAWQA_GLASS/analyses'
mycsv = '/home/nobody/NATIONAL_GEODATA/PART_Baseflow_Separations/Reitz_BASEFLOW_stats.csv'
THRESHOLD = 2./3.

part = pd.read_csv( mycsv )
part.Gage_STR = [s.strip("u") for s in part.Gage_STR] 

first_col = 37
last_col  = 67

good_gages = []
good_count = []
bad_gages = []
bad_count = []

def calc_part_stats( gage_id ):
  myrow = part[part.Gage_STR==gage_id]
  mydata = myrow.iloc[ :, first_col:last_col] 
  if myrow is not None:
    mymean = np.nanmean( mydata[ mydata >= 0.0 ] ) * 39.37
    mymin = np.nanmin( mydata[ mydata >= 0.0 ] ) * 39.37
    mymax = np.nanmax( mydata[ mydata >= 0.0 ] ) * 39.37
  return mymean, mymin, mymax

def extract_gage_id( namelist=[] ):
  """
    Very brittle function...looks for the QUATERNARY_SOILS_GRP file and extracts the gage_id.
  """
  gage_id = 99999999
  for name in namelist:
    if 'QUATERNARY' in name:
      s = name.split('_')
      gage_id = s[-1].split('.')[0]
  return gage_id


part = part[ part.GLASS.notnull() ]
nrows = part.ix[:,0].count()

for row in range(0, nrows):
    valid_vector = part.ix[row,first_col:last_col] > 0.
    valid_cols = sum( valid_vector )
    valid_frac = valid_cols / ( last_col - first_col + 1 )
    
    if valid_frac > THRESHOLD:
        good_gages.append( part.ix[ row, 'Gage_STR' ])
        good_count.append( valid_cols )
    else:
        bad_gages.append( part.ix[ row, 'Gage_STR'])
        bad_count.append( valid_cols )

# Pandas indexing is weird...
#part.ix[:,first_col:last_col]

mytarfiles = []
partmeanlist = []
partmaxlist = []
partminlist = []
swbmeanlist = []
finalgagelist = []

for file in glob.glob(mydir + '/*.tar'):
    mytarfiles.append(file)
    tfile = tarfile.open( file )
    namelist = tfile.getnames()
    gage_id = extract_gage_id( namelist )
    print ( 'Examining tarfile {0}. Gage ID={1}.'.format( file, gage_id ) )
    if gage_id in good_gages:
      newdirname = myworkdir +'/gage_' + gage_id 
      os.makedirs( newdirname, exist_ok=True )  
      print ( 'Creating directory {0}'.format( newdirname ) )
      found_files = False
      for filename in namelist:  
        if 'NLCD' in filename or 'SOILS' in filename or 'AWC' in filename or 'D8' in filename:
          tfile.extract( member=tfile.getmember( filename), path=newdirname )
        if 'MEAN_RECHARGE' in filename:
          tfile.extract( member=tfile.getmember( filename ), path=newdirname )
          found_files = True
          ds = gdal.Open( newdirname + '/' + filename, GA_ReadOnly )
          if ds is None:
            print( 'Could not open ' + filename )
            sys.exit(1)
          band = ds.GetRasterBand(1)
          cols = ds.RasterXSize
          rows = ds.RasterYSize
          data = band.ReadAsArray( 0, 0, cols, rows )
          mymean = np.nanmean( data[ data >= 0.0 ] )
          partmean, partmin, partmax = calc_part_stats( gage_id )
          print( 'PART and SWB mean for gage {0}: {1}, {2}'.format(gage_id, mymean, partmean ) )
          partmeanlist.append( partmean )
          partminlist.append( partmin )
          partmaxlist.append( partmax )
          swbmeanlist.append( mymean )
          finalgagelist.append( gage_id )
      if not found_files:
        shutil.rmtree( newdirname )
df = pd.DataFrame( { 'gage_id': finalgagelist, 'swb_mean': swbmeanlist, 'part_mean': partmeanlist, 'part_min': partminlist, \
     'part_max': partmaxlist } )
