from rasterstats import zonal_stats
import pandas as pd
import numpy as np

baseflow_shp = "/home/nobody/NATIONAL_GEODATA/PART_Baseflow_Separations/Reitz_BASEFLOW_stats__GLASS_only.shp"
runoff_shp = "/home/nobody/NATIONAL_GEODATA/PART_Baseflow_Separations/Reitz_RUNOFF_stats__GLASS_only.shp"
totalflow_shp = "/home/nobody/NATIONAL_GEODATA/PART_Baseflow_Separations/Reitz_STREAMFLOW_stats__GLASS_only.shp"

swb_precip = "/run/media/smwesten/SCRATCH/temp__13OCT2016/concatenated_gross_precip.vrt"
swb_interception = "/run/media/smwesten/SCRATCH/temp__13OCT2016/concatenated_swb_interception.vrt"
swb_rech = "/run/media/smwesten/SCRATCH/temp__13OCT2016/concatenated_recharge.vrt"
glass_rech = "/home/nobody/NATIONAL_GEODATA/GLASS_recharge/SWB_GLASS_Final_recharge__2000_2010_inches.asc"
reitz_rech = "/home/nobody/NATIONAL_GEODATA/GLASS_recharge/Meredith_FINAL_INCHES.tif"

swb_et = "/run/media/smwesten/SCRATCH/temp__13OCT2016/concatenated_actual_et.vrt"
reitz_et = "/home/nobody/NATIONAL_GEODATA/ET_Grid_fm_Meredith/ET_0013_in_yr.tif"
ssebop_et = "/home/nobody/NATIONAL_GEODATA/SSEbopETa/SSEbopETa_2000_2013.tif"

swb_runoff = "/run/media/smwesten/SCRATCH/temp__13OCT2016/concatenated_runoff.vrt"
reitz_runoff = "/home/nobody/NATIONAL_GEODATA/Runoff_Grid_fm_Meredith/RO_0013_in_yr.tif"

swb_list = []
swb_huc_list = []
swb_et_huc_list = []
swb_intcp_huc_list = []
swb_intcp_list = []
reitz_huc_list = []
glass_huc_list = []
reitz_et_huc_list = []
part_list = []
glass_list = []
reitz_list = []
swb_precip_list = []
swb_et_list = []
reitz_et_list = []
ssebop_et_list = []
ssebop_et_huc_list = []
swb_ro_list = []
reitz_ro_list = []
part_ro_list = []
part_totalflow_list = []

swb_ro_huc_list = []
reitz_ro_huc_list = []

def mymean(x):
  mask = ( ~np.isnan(x) ) & ( x >= 0. )
  return x[mask].mean()

swb_rech_stats = zonal_stats( baseflow_shp, swb_rech, stats="count median", add_stats={'mean':mymean}, geojson_out=True)
glass_rech_stats = zonal_stats( baseflow_shp, glass_rech, stats="count median", add_stats={'mean':mymean}, geojson_out=True)
reitz_rech_stats = zonal_stats( baseflow_shp, reitz_rech, stats="count median", add_stats={'mean':mymean}, geojson_out=True)

# extract useful stuff from GeoJSON
for line in range(len(swb_rech_stats)):
  swb_list.append(swb_rech_stats[line]['properties']['mean']);
  swb_huc_list.append(swb_rech_stats[line]['properties']['GAGE_ID']);
  part_list.append(swb_rech_stats[line]['properties']['BF_MEAN_IN']);

for line in range(len(reitz_rech_stats)):
  reitz_list.append(reitz_rech_stats[line]['properties']['mean']);
  reitz_huc_list.append(reitz_rech_stats[line]['properties']['GAGE_ID']);

for line in range(len(glass_rech_stats)):
  glass_list.append(glass_rech_stats[line]['properties']['mean']);
  glass_huc_list.append(glass_rech_stats[line]['properties']['GAGE_ID']);

swb_rech_stats = None
reitz_rech_stats = None
glass_rech_stats = None

swb_et_stats = zonal_stats( baseflow_shp, swb_et, stats="count median", add_stats={'mean':mymean}, geojson_out=True)
#swb_intcp_stats = zonal_stats( baseflow_shp, swb_interception, stats="count median", add_stats={'mean':mymean}, geojson_out=True)
reitz_et_stats = zonal_stats( baseflow_shp, reitz_et, stats="count median", add_stats={'mean':mymean}, geojson_out=True)
ssebop_et_stats = zonal_stats( baseflow_shp, ssebop_et, stats="count median", add_stats={'mean':mymean}, geojson_out=True)


for line in range(len(swb_et_stats)):
  swb_et_list.append(swb_et_stats[line]['properties']['mean']);
  swb_et_huc_list.append(swb_et_stats[line]['properties']['GAGE_ID']);

# for line in range(len(swb_intcp_stats)):
#   swb_intcp_list.append(swb_intcp_stats[line]['properties']['mean']);
#   swb_intcp_huc_list.append(swb_intcp_stats[line]['properties']['GAGE_ID']);

for line in range(len(reitz_et_stats)):
  reitz_et_list.append(reitz_et_stats[line]['properties']['mean']);
  reitz_et_huc_list.append(reitz_et_stats[line]['properties']['GAGE_ID']);

for line in range(len(ssebop_et_stats)):
  ssebop_et_list.append(ssebop_et_stats[line]['properties']['mean']);
  ssebop_et_huc_list.append(ssebop_et_stats[line]['properties']['GAGE_ID']);

swb_et_stats = None
swb_intcp_stats = None
reitz_et_stats = None
ssebop_et_stats = None

swb_ro_stats = zonal_stats( runoff_shp, swb_runoff, stats="count median", add_stats={'mean':mymean}, geojson_out=True)
reitz_ro_stats = zonal_stats( runoff_shp, reitz_runoff, stats="count median", add_stats={'mean':mymean}, geojson_out=True)

for line in range(len(reitz_ro_stats)):
  reitz_ro_list.append(reitz_ro_stats[line]['properties']['mean']);
  reitz_ro_huc_list.append(reitz_ro_stats[line]['properties']['GAGE_ID']);

for line in range(len(swb_ro_stats)):
  swb_ro_list.append(swb_ro_stats[line]['properties']['mean']);
  swb_ro_huc_list.append(swb_ro_stats[line]['properties']['GAGE_ID']);
  part_ro_list.append(swb_ro_stats[line]['properties']['RO_MEAN_IN']);

swb_ro_stats = None
reitz_ro_stats = None

swb_precip_stats = zonal_stats( totalflow_shp, swb_precip, stats="count median", add_stats={'mean':mymean}, geojson_out=True)

for line in range(len(swb_precip_stats)):
  swb_precip_list.append(swb_precip_stats[line]['properties']['mean']);
  part_totalflow_list.append(swb_precip_stats[line]['properties']['SF_MEAN_IN']);

swb_precip_stats = None

swbdf = pd.DataFrame(data={'huc': swb_huc_list, 'mean_swb_precip': swb_precip_list,
                            'mean_swb_rech': swb_list, 'mean_PART_streamflow': part_totalflow_list,
                            #'mean_swb_intcp': swb_intcp_list,
                            'mean_PART_rech': part_list,
                            'mean_PART_ro': part_ro_list,
                            'mean_swb_et': swb_et_list, 'mean_swb_ro': swb_ro_list,
                            'mean_ssebop_et': ssebop_et_list })
glassdf = pd.DataFrame(data={'huc': glass_huc_list, 'mean_glass_rech': glass_list} )
reitzdf = pd.DataFrame(data={'huc': reitz_huc_list, 'mean_reitz_rech':reitz_list,
                            'mean_reitz_et': reitz_et_list, 'mean_reitz_ro': reitz_ro_list } )

df1 = swbdf.merge( glassdf, on="huc")
df2 = df1.merge( reitzdf, on="huc")

df2.to_csv("SWB_GLASS_Reitz_PART_13OCT2016.csv")
