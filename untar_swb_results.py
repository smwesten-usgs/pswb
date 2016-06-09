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

# Pandas indexing is weird...
#part.ix[:,first_col:last_col]

mytarfiles = []
mydescriptionlist = []
swbmeanlist = []
finalgagelist = []

for file in glob.glob(mydir + '/*output_files_CONFINED_*.tar'):
    mytarfiles.append(file)
    mydescriptionlist.append('CONFINED')

for file in glob.glob(mydir + '/*output_files_UNCONFINED_*.tar'):
    mytarfiles.append(file)
    mydescriptionlist.append('UNCONFINED')

for file in glob.glob(mydir + '/*output_files_IAMO_*.tar'):
    mytarfiles.append(file)
    mydescriptionlist.append('IAMO')    

for file in glob.glob(mydir + '/*output_files_INITIAL_*.tar'):
    mytarfiles.append(file)
    mydescriptionlist.append('INITIAL')    
    
for file, description in zip( mytarfiles, mydescriptionlist):    
    
    try:
      tfile = tarfile.open( file )
      tfile_open=True
    except:
      tfile_open=False

    if tfile_open:
      namelist = tfile.getnames()
      gage_id = extract_gage_id( namelist )
      print ( 'Examining tarfile {0}. Gage ID={1}.'.format( file, gage_id ) )
      newdirname = myworkdir + '/' + description + '_USGS_gage_' + str(gage_id )
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
          print( 'SWB mean for gage {0}: {1}'.format(gage_id, mymean ) )
          swbmeanlist.append( mymean )
          finalgagelist.append( gage_id )
        if not found_files:
          shutil.rmtree( newdirname )

df = pd.DataFrame( { 'gage_id': finalgagelist, 'swb_mean': swbmeanlist } )

df['gage_id_str'] = 'u' + df.gage_id

df.to_csv('SWB_vs_GAGESII.csv')