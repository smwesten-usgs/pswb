from __future__ import print_function

import tarfile
import os
import glob
import gdal
import shutil
import sys
import matplotlib.pyplot as plt
from rasterstats import zonal_stats
from gdalconst import *
import numpy as np
import cartopy.crs as ccrs
import rasterio
import pandas as pd

mydir = '/home/smwesten/Project_Data/NAWQA_GLASS/results'
myworkdir = '/home/smwesten/Project_Data/NAWQA_GLASS/analyses'
mycsv = '/home/nobody/NATIONAL_GEODATA/PART_Baseflow_Separations/Reitz_BASEFLOW_stats.csv'
GLASS_SWB = '/home/nobody/NATIONAL_GEODATA/GLASS_recharge/GLASS_RECHARGE_MEAN_ANNUAL_RECHARGE_SUM_2000_2010.tif'
NLCD = '/home/nobody/NATIONAL_GEODATA/NLCD/nlcd_2011_landcover_2011_edition_2014_03_31.img'
reitz_recharge = '/home/nobody/NATIONAL_GEODATA/GLASS_recharge/Meredith_FINAL_INCHES.tif'
THRESHOLD = -1.

part = pd.read_csv( mycsv )
part.Gage_STR = [s.strip("u") for s in part.Gage_STR] 

first_col = 37
last_col  = 67

good_gages = []
good_count = []
bad_gages = []
bad_count = []

def plot_NLCD( shapefile, gridfile ):
  shp = gdal.Open( shapefile , GA_ReadOnly )
  if shp is None:
    print( 'Could not open ' + shapefile )
    sys.exit(1)
    shp.
  with rasterio.drivers():
    with rasterio.open( gridfile, 'r') as src:
      im = src.read()

def read_swb_array( filename ):
  ds = gdal.Open( filename , GA_ReadOnly )
  if ds is None:
    print( 'Could not open ' + filename )
    sys.exit(1)
  band = ds.GetRasterBand(1)
  cols = ds.RasterXSize
  rows = ds.RasterYSize
  data = band.ReadAsArray( 0, 0, cols, rows )
  return cols, rows, data

def calc_NLCD_stats( shapefile ):
  cmap = { 11: 'Open water', 12: 'Perennial ice/snow', 21: 'Developed, open space', \
           22: 'Developed, low-intensity', 23: 'Developed, medium-intensity',       \
           24: 'Developed, high-intensity', 31: 'Barren land )rock/sand/clay)',     \
           41: 'Deciduous forest', 42: 'Evergreen forest', 43: 'Mixed forest',      \
           51: 'Dwarf scrub', 52: 'Shrub/scrub', 71: 'Grassland/herbaceous',        \
           72: 'Sedge/herbaceous', 81: 'Pasture/hay', 82: 'Cultivated crops',       \
           90: 'Woody wetlands', 95: 'Emergent herbaceous wetlands' }
  
  zs = zonal_stats( shapefile, NLCD, categorical=True, category_map=cmap)
  return zs

def calc_quaternary_stats( shapefile, gridfile ):
  cmap = { 1: 'Bedrock', 2: 'Clayey, stratified, continuous', 3: 'Clayey, unstratified, continuous',        \
           4: 'Fill', 5: 'Island', 6: 'Peat', 7: 'Sandy, stratified, continuous',                           \
           8: 'Sandy, unstratified, continuous', 9: 'Sandy, stratified, continuous, ice-contact',           \
           10: 'Sandy, unstratified, patchy', 11: 'Silty, stratified, continuous',                          \
           12: 'Silty, unstratified, continuous', 13: 'Silty, unstratified, patchy',                        \
           14: 'Variable, unstratified, continuous', 15: 'Water', 16: 'Driftless Area ridgetop colluviuum'}
  
  zs = zonal_stats( shapefile, gridfile, categorical=True, category_map=cmap )
  return zs
  
def calc_reitz_stats( shapefile ):
  zs = zonal_stats( shapefile, reitz_recharge)
  return zs

def calc_glass_stats( shapefile ):
  zs = zonal_stats( shapefile, GLASS_SWB )
  return zs

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
  filename = 'NA'
  for name in namelist:
    if 'QUATERNARY' in name:
      s = name.split('_')
      gage_id = s[-1].split('.')[0]
      filename = name.split('.')[0] + '.asc'
  return gage_id, filename

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
reitzmeanlist = []
reitzminlist = []
reitzmaxlist = []
glassmeanlist = []
glassminlist = []
glassmaxlist = []
nlcdlist = []
quaternarylist = []

for file in glob.glob(mydir + '/*GAGES*.tar'):
    mytarfiles.append(file)
    
    try:
      tfile = tarfile.open( file )
      tfile_open=True
    except:
      tfile_open=False

    if tfile_open:
      namelist = tfile.getnames()
      gage_id, quaternary_file = extract_gage_id( namelist )
      print ( 'Examining tarfile {0}. Gage ID={1}.'.format( file, gage_id ) )
      if gage_id in good_gages:
        newdirname = myworkdir +'/gage_' + gage_id 
        quaternary_gridfile = newdirname + '/' + quaternary_file
        os.makedirs( newdirname )  
        print ( 'Creating directory {0}'.format( newdirname ) )
        found_files = False
        for filename in namelist:  
          file_extension = filename.split('.')[1]
          if 'MEAN_RECHARGE' in filename:

            tfile.extract( member=tfile.getmember( filename ), path=newdirname )
            found_files = True
            cols, rows, data = read_swb_array( newdirname + '/' + filename )
            mymean = np.nanmean( data[ data >= 0.0 ] )
            
            partmean, partmin, partmax = calc_part_stats( gage_id )
            print( 'PART and SWB mean for gage {0}: {1}, {2}'.format(gage_id, mymean, partmean ) )
            partmeanlist.append( partmean )
            partminlist.append( partmin )
            partmaxlist.append( partmax )
            swbmeanlist.append( mymean )
            
            finalgagelist.append( gage_id )

          elif file_extension in ['asc','shx','dbf','prj','qpj']:
            tfile.extract( member=tfile.getmember( filename ), path=newdirname )

          elif file_extension == 'shp':  
            tfile.extract( member=tfile.getmember( filename ), path=newdirname )
            myshapefile = newdirname + '/' + filename  

        if not found_files:
          shutil.rmtree( newdirname )
        else:

          try:
            zs = calc_reitz_stats( myshapefile )
            reitzminlist.append( zs[0]['min'] )
            reitzmeanlist.append( zs[0]['mean'] )
            reitzmaxlist.append( zs[0]['max'] )            
          except:
            reitzminlist.append(-99999.)
            reitzmeanlist.append(-99999.)
            reitzmaxlist.append(-99999.)            
          
          try:
            zs = calc_glass_stats( myshapefile )
            glassminlist.append( zs[0]['min'] )
            glassmeanlist.append( zs[0]['mean'] )
            glassmaxlist.append( zs[0]['max'] )            
          except:
            glassminlist.append(-99999.)
            glassmeanlist.append(-99999.)
            glassmaxlist.append(-99999.)            

          try:
            zs = calc_NLCD_stats( myshapefile )
            nlcdlist.append( zs[0] )
          except:
            nlcdlist.append({ 'NA': -99999 } )

          try:
            zs = calc_quaternary_stats( myshapefile, quaternary_gridfile )
            quaternarylist.append( zs[0] )
          except:
            quaternarylist.append({ 'NA': -99999 } )

df = pd.DataFrame( { 'gage_id': finalgagelist, 'swb_mean': swbmeanlist, 'reitz_mean': reitzmeanlist, \
                     'reitz_min': reitzminlist, 'reitz_max': reitzmaxlist,                           \
                     'glass_mean': glassmeanlist,                                                    \
                     'glass_min': glassminlist, 'glass_max': glassmaxlist,                           \
                     'part_mean': partmeanlist, 'part_min': partminlist, 'part_max': partmaxlist,    \
                     'nlcd_counts': nlcdlist, 'quaternary_counts': quaternarylist  } )

df['diff'] = df.swb_mean - df.part_mean
df['gage_id_str'] = 'u' + df.gage_id

df.to_csv('SWB_vs_GAGESII.csv')

# SNIPPETS
# extract dictionary from larger dataframe...
#   mydict=df.loc[0, 'quaternary_counts']
# convert dictionary to pandas dataframe
#   qa = pd.DataFrame.from_dict(mydict, orient='index')
# sort pandas dataframe by column name
#   qa.sort_values('cat')
#
# Seaborn scatterplot of PART vs another recharge estimation method:
# with sns.axes_style('ticks'):sns.jointplot(x='part_mean', y='reitz_mean', data=df)
