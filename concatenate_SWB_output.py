from __future__ import print_function

import tarfile
import run_cmd as rc
import os
import glob
import sys
import gdal
import rasterio
from rasterstats import zonal_stats
import pandas as pd
from gdalconst import *
import numpy as np
import numpy.ma as ma
mydir = '/run/media/smwesten/SCRATCH/SWB_RUN__08AUG2016/results'
#mydir = '/home/smwesten/Project_Data/NAWQA_GLASS/results'
#myworkdir = '/home/smwesten/Project_Data/NAWQA_GLASS/analyses'
myworkdir = '/run/media/smwesten/SCRATCH/temp'

GLASS_SWB = '/home/nobody/NATIONAL_GEODATA/GLASS_recharge/GLASS_RECHARGE_MEAN_ANNUAL_RECHARGE_SUM_2000_2010.tif'
NLCD = '/home/nobody/NATIONAL_GEODATA/NLCD/nlcd_2011_landcover_2011_edition_2014_03_31.img'
reitz_recharge = '/home/nobody/NATIONAL_GEODATA/GLASS_recharge/Meredith_FINAL_INCHES.tif'

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
  cmap = { 1: 'Clayey, A soil', 2: 'Clayey, B soil', 3: 'Clayey, C soil', 4: 'Clayey, D soil',   \
           5: 'Loamy and Clayey, A soil', 6: 'Loamy and Clayey, B soil', 7: 'Loamy and Clayey, C soil', 8: 'Loamy and Clayey, D soil',  \
           9: 'Loamy, A soil', 10: 'Loamy, B soil', 11: 'Loamy, C soil', 12: 'Loamy, D soil',   \
           13: 'Sandy silty, A soil', 14: 'Sandy silty, B soil', 15: 'Sandy silty, C soil', 16: 'Sandy silty, D soil',   \
           17: 'Sandy, A soil', 18: 'Sandy, B soil', 19: 'Sandy, C soil', 20: 'Sandy, D soil',   \
           21: 'Other, A soil', 22: 'Other, B soil', 23: 'Other, C soil', 24: 'Other, D soil',   \
           25: 'Water' }

  zs = zonal_stats( shapefile, gridfile, categorical=True, category_map=cmap )
  return zs

def write_raster(ncol, nrow, xll, yll, cellsize, nodata, data, filename ):
  rasterfile = open(filename, "w")
  rasterfile.write("ncols " + str(ncol) + "\n")
  rasterfile.write("nrows " + str(nrow) + "\n")
  rasterfile.write("xllcorner " + str(xll) + "\n")
  rasterfile.write("yllcorner " + str(yll) + "\n")
  rasterfile.write("cellsize " + str(cellsize) + "\n")
  rasterfile.write("NODATA_value " + str(nodata) + "\n")

  print("ncol: " + str(ncol))
  print("nrow: " + str(nrow))
  print("shape: " + str(data.shape))

  for row in range(nrow):
    for col in range(ncol):
      dataval = float( data[row,col] )
      if dataval is not np.nan:
        rasterfile.write('{:.3f} '.format( dataval ) )
      else:
        rasterfile.write('{:.3f} '.format( -9999. ) )
    rasterfile.write("\n")
  rasterfile.close()

def read_raster(rasterfile):
  '''
  reads a GDAL raster into numpy array for plotting
  also returns meshgrid of x and y coordinates of each cell for plotting
  based on code stolen from:
  http://stackoverflow.com/questions/20488765/plot-gdal-raster-using-matplotlib-basemap
  '''
  try:
    import gdal
  except:
    print('This function requires gdal.')
  try:
    ds = gdal.Open(rasterfile)
  except:
    raise IOError("problem reading raster file {}".format(rasterfile))

  print('\nreading in {} into numpy array...'.format(rasterfile))
  data = ds.ReadAsArray()
  gt = ds.GetGeoTransform()
  proj = ds.GetProjection()

  xres = gt[1]
  yres = gt[5]

  # get the edge coordinates and add half the resolution
  # to go to center coordinates
  xmin = gt[0] + xres * 0.5
  xmax = gt[0] + (xres * ds.RasterXSize) - xres * 0.5
  ymin = gt[3] + (yres * ds.RasterYSize) + yres * 0.5
  ymax = gt[3] + yres * 0.5

  del ds

  print('creating a grid of xy coordinates in the original projection...')
  xy = np.mgrid[xmin:xmax+xres:xres, ymax+yres:ymin:yres]

  # create a mask for no-data values
  data[data<-1.0e+20] = 0

  return data, gt, proj, xy

def extract_huc_id( namelist=[] ):
  """
    Very brittle function...looks for the QUATERNARY_SOILS_GRP file and extracts the huc_id.
  """
  gage_id = 99999999
  filename = 'NA'
  for name in namelist:
    if 'QUATERNARY' in name:
      s = name.split('_')
      huc_id = s[-1].split('.')[0]
      filename = name.split('.')[0] + '.asc'
  return huc_id, filename


mytarfiles = []
myrechargefiles = []
myprecipfiles = []

huclist = []
reitzmeanlist = []
reitzminlist = []
reitzmaxlist = []
glassmeanlist = []
glassminlist = []
glassmaxlist = []
swbmeanlist = []
swbminlist = []
swbmaxlist = []

os.chdir( myworkdir )

for file in glob.glob(mydir + '/*output_files*.tar'):
  mytarfiles.append(file)

  try:
    tfile = tarfile.open( file )
    tfile_open=True
  except:
    tfile_open=False

  if tfile_open:
    namelist = tfile.getnames()
    huc_id, quaternary_file = extract_huc_id( namelist )
    print ( 'Examining tarfile {0}. HUC ID={1}.'.format( file, huc_id ) )
    newdirname = myworkdir +'/huc8_' + huc_id
    quaternary_gridfile = newdirname + '/' + quaternary_file
    os.makedirs( newdirname )
    print ( 'Creating directory {0}'.format( newdirname ) )
    found_files = False
    firstpass_precip = True
    precip_count = 0
    for filename in namelist:
      file_extension = filename.split('.')[1]
      if 'MEAN_RECHARGE' in filename:

        tfile.extract( member=tfile.getmember( filename ), path=newdirname )
        myrechargefiles.append( newdirname + '/' + filename)
        found_files = True
        huclist.append( huc_id )
        data, gt, proj, xy = read_raster( newdirname + '/' + filename )
        mymean = np.nanmean( data[ data >= 0.0 ] )
        mymin = np.nanmin( data[ data >= 0.0 ] )
        mymax = np.nanmax( data[ data >= 0.0 ] )
        swbmeanlist.append( mymean )
        swbminlist.append( mymin )
        swbmaxlist.append( mymax )

      elif 'GROSS_PRECIP' in filename and 'SUM' in filename:

        precip_count += 1
        tfile.extract( member=tfile.getmember( filename ), path=newdirname )
        data, gt, proj, xy = read_raster( newdirname + '/' + filename )

        if firstpass_precip:
          precip_data = ma.masked_where( data < 0.0, data )
          firstpass_precip = False
          gt_precip = gt
          proj_precip = proj
        else:
          precip_data += ma.masked_where( data < 0.0, data )

      elif file_extension in ['asc','shx','dbf','prj','qpj','ctl']:
        tfile.extract( member=tfile.getmember( filename ), path=newdirname )

      elif file_extension == 'shp':
        tfile.extract( member=tfile.getmember( filename ), path=newdirname )
        myshapefile = newdirname + '/' + filename

    if precip_count > 0:
      precip_data /= precip_count
      #os.chdir( myworkdir )
      precip_filename=myworkdir + '/swb_mean_gross_precip_'+ str(huc_id) + '.asc'
      nrow = precip_data.shape[0]
      ncol = precip_data.shape[1]
      cellsize = gt_precip[1]
      write_raster(ncol=ncol,
                  nrow=nrow,
                  xll=gt_precip[0],
                  yll=gt_precip[3] - nrow * cellsize,
                  cellsize=cellsize,
                  nodata=-9999.,
                  data=precip_data,
                  filename=precip_filename )
      myprecipfiles.append( precip_filename )

      if not found_files:
        pass
      else:
        try:
          zs = zonal_stats( myshapefile, reitz_recharge)
          reitzminlist.append( zs[0]['min'] )
          reitzmeanlist.append( zs[0]['mean'] )
          reitzmaxlist.append( zs[0]['max'] )
        except:
          reitzminlist.append(-99999.)
          reitzmeanlist.append(-99999.)
          reitzmaxlist.append(-99999.)

      if not found_files:
        pass
      else:
        try:
          zs = zonal_stats( myshapefile, GLASS_SWB)
          glassminlist.append( zs[0]['min'] )
          glassmeanlist.append( zs[0]['mean'] )
          glassmaxlist.append( zs[0]['max'] )
        except:
          glassminlist.append(-99999.)
          glassmeanlist.append(-99999.)
          glassmaxlist.append(-99999.)

df = pd.DataFrame( { 'huc_id': huclist, 'swb_mean': swbmeanlist, 'swb_min': swbminlist, 'swb_max': swbmaxlist, \
                     'reitz_mean': reitzmeanlist, 'reitz_min': reitzminlist, 'reitz_max': reitzmaxlist,        \
                     'glass_mean': glassmeanlist,                                                    \
                     'glass_min': glassminlist, 'glass_max': glassmaxlist } )

df['diff_reitz'] = df.swb_mean - df.reitz_mean
df['diff_glass'] = df.swb_mean - df.glass_mean
df['huc_id_str'] = 'huc_' + df.huc_id

df.to_csv('SWB_vs_REITZ_and_GWRP_GLASS.csv')

filelist = open( 'huc_list_recharge_vrt.txt', 'w')
[filelist.write( filename + '\n' ) for filename in myrechargefiles]
filelist.close()

command_args = ['-input_file_list','huc_list_recharge_vrt.txt','concatenated_swb_recharge.vrt']
rc.run_cmd( command_text='gdalbuildvrt', command_arguments=command_args )

filelist = open( 'huc_list_gross_precip_vrt.txt', 'w')
[filelist.write( filename + '\n' ) for filename in myprecipfiles]
filelist.close()

command_args = ['-input_file_list','huc_list_gross_precip_vrt.txt','concatenated_swb_gross_precip.vrt']
rc.run_cmd( command_text='gdalbuildvrt', command_arguments=command_args )

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
