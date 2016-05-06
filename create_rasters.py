import os

myfile = ""

def run_command( command_str):

    result = os.system( command_str )

    return result

def squote( string ):
    return "'" + string + "'"

def dquote( string ):
    return '"' + string + '"'

def rasterize_int( fieldname, llx, lly, urx, ury, resolution, shapefile, modifier=''):
    """ Rasterize a field from a shapefile and create a tif file as output."""
    command_str = exe_location + 'gdal_rasterize -a ' + fieldname + '-a_nodata -9999'
    + ' -te ' + str(llx) + '. ' + str(lly) + '. ' + str(urx) + '. ' + str(ury) + '. '
    + '-tr ' + str( resolution) + ' ' + str(resolution) + ' -ot Int32 ' + shapefile 
    + ' ' + fieldname + ' ' + modifier + '__' + str(resolution) +'m.tif'
    print( 'command text: ' + command_str )
    result = run_command( command_str )
    command_str = exe_location + 'gdal_translate ' + ' -ot Float32 -a_nodata -9999. -of AAIGrid '
    + '-co DECIMAL_PRECISION=3'
    + ' ' + fprefix + '.tif' + ' ' + fprefix + '.asc'
    print( 'command text: ' + command_str )
    result = run_command( command_str )

def rasterize_float( fieldname, llx, lly, urx, ury, resolution, shapefile, file_prefix, file_modifier=''):
    """ Rasterize a field from a shapefile and create a tif file as output."""
    fprefix =  file_prefix + ' ' + modifier + '__' + str(resolution) +'m'
    command_str = exe_location + 'gdal_rasterize -a ' + fieldname + '-a_nodata -9999.'
    + ' -te ' + str(llx) + '. ' + str(lly) + '. ' + str(urx) + '. ' + str(ury) + '. '
    + '-tr ' + str( resolution) + ' ' + str(resolution) + ' -ot Float32 ' + shapefile 
    + ' ' + fprefix + '.tif'
    print( 'command text: ' + command_str )
    result = run_command( command_str )
    command_str = exe_location + 'gdal_translate ' + ' -ot Int32 -a_nodata -9999 -of AAIGrid '
    + ' ' + fprefix + '.tif' + ' ' + fprefix + '.asc'
    print( 'command text: ' + command_str )
    result = run_command( command_str )
    

def subset_shapefile( path_name, shape_name, attr_name, attr_value, output_shape_name='local_shape.shp' ):
    print ( 'Creating local basin shapefile. File= ' + output_shape_name )
    basename = shape_name.split('.')[0]
    command_str = exe_location + 'ogr2ogr -sql ' + dquote('SELECT * from ' + basename + ' WHERE ' + attr_name + '=' 
    + squote(attr_value) ) + ' ' + output_shape_name + ' ' + path_name + shape_name
    print( 'command text: ' + command_str )
    result = run_command( command_str )

if __name__ == '__main__':

    exe_location = '/usr/bin/'
    huc10_path ='/home/nobody/NATIONAL_GEODATA/WBD_National/'
    huc10_shp = 'WBDHU10_AEA_NAD83.shp'
    output_shape_name = 'crap.shp'
    huc10_id = '1028010209'    
    
    result = subset_shapefile( huc10_path, huc10_shp, 'HUC10', huc10_id, output_shape_name )
        