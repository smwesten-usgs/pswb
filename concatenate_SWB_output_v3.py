from __future__ import print_function

import tarfile
import run_cmd as rc
import os
import glob
import sys
import gdal
import rasterio
from gdalconst import *
import numpy as np
import numpy.ma as ma
from shutil import copyfile

mydir = '/run/media/smwesten/SCRATCH/SWB_RUN__09SEP2016/results'
myworkdir = '/run/media/smwesten/SCRATCH/temp__09SEP2016_run'

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
myinterceptionfiles = []

huclist = []

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
    try:
      os.makedirs( newdirname )
      print ( 'Creating directory {0}'.format( newdirname ) )
    except:
      pass
    found_files = False

    firstpass_precip = True
    precip_count = 0
    firstpass_interception = True
    interception_count = 0

    for filename in namelist:
      file_extension = filename.split('.')[1]
      file_basename = filename.split('.')[0]
      fname = newdirname + '/' + filename

      if 'MEAN_RECHARGE' in filename:

        tfile.extract( member=tfile.getmember( filename ), path=newdirname )
        myrechargefiles.append( fname )
        found_files = True
        huclist.append( huc_id )
        copyfile( fname, myworkdir + '/' + file_basename + '_huc8_' + huc_id + '.asc' )

      elif 'GROSS_PRECIP' in filename and 'SUM' in filename:

        precip_count += 1
        fname = newdirname + '/' + filename
        tfile.extract( member=tfile.getmember( filename ), path=newdirname )
        data, gt, proj, xy = read_raster( fname )

        if firstpass_precip:
          precip_data = ma.masked_where( data < 0.0, data )
          firstpass_precip = False
          gt_precip = gt
          proj_precip = proj
        else:
          precip_data += ma.masked_where( data < 0.0, data )

      elif 'INTERCEPTION' in filename and 'SUM' in filename:

        interception_count += 1
        tfile.extract( member=tfile.getmember( filename ), path=newdirname )
        data, gt, proj, xy = read_raster( fname )

        if firstpass_interception:
          interception_data = ma.masked_where( data < 0.0, data )
          firstpass_interception = False
          gt_interception = gt
          proj_interception = proj
        else:
          interception_data += ma.masked_where( data < 0.0, data )

      elif file_extension in ['asc','shx','dbf','prj','qpj','ctl']:
        tfile.extract( member=tfile.getmember( filename ), path=newdirname )

      elif 'LOGFILE' in filename:
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

    if interception_count > 0:
      interception_data /= interception_count
      #os.chdir( myworkdir )
      interception_filename=myworkdir + '/swb_mean_interception_'+ str(huc_id) + '.asc'
      nrow = interception_data.shape[0]
      ncol = interception_data.shape[1]
      cellsize = gt_interception[1]
      write_raster(ncol=ncol,
                  nrow=nrow,
                  xll=gt_interception[0],
                  yll=gt_interception[3] - nrow * cellsize,
                  cellsize=cellsize,
                  nodata=-9999.,
                  data=interception_data,
                  filename=interception_filename )
      myinterceptionfiles.append( interception_filename )


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


filelist = open( 'huc_list_interception_vrt.txt', 'w')
[filelist.write( filename + '\n' ) for filename in myinterceptionfiles]
filelist.close()

command_args = ['-input_file_list','huc_list_interception_vrt.txt','concatenated_swb_interception.vrt']
rc.run_cmd( command_text='gdalbuildvrt', command_arguments=command_args )
