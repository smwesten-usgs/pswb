from rasterstats import zonal_stats
import pandas as pd

shp = "/home/nobody/NATIONAL_GEODATA/PART_Baseflow_Separations/Reitz_BASEFLOW_stats.shp"
swb_rast = "/run/media/smwesten/SCRATCH/temp/concatenated_swb_recharge.vrt"
glass_rast = "/home/nobody/NATIONAL_GEODATA/GLASS_recharge/SWB_GLASS_Final_recharge__2000_2010_inches.asc"
reitz_rast = "/home/nobody/NATIONAL_GEODATA/GLASS_recharge/Meredith_FINAL_INCHES.tif"

swb_stats = zonal_stats( shp, swb_rast, stats="median mean", geojson_out=True)
glass_stats = zonal_stats( shp, glass_rast, stats="median mean", geojson_out=True)
reitz_stats = zonal_stats( shp, reitz_rast, stats="median mean", geojson_out=True)

swblist = []
huclist = []
reitzhuclist = []
glasshuclist = []
partlist = []
glasslist = []
reitzlist = []

# extract useful stuff from GeoJSON
for line in range(len(swb_stats)):
  swblist.append(swb_stats[line]['properties']['mean']);
  huclist.append(swb_stats[line]['properties']['GAGE_ID']);
  partlist.append(swb_stats[line]['properties']['BF_MEAN_IN']);

for line in range(len(reitz_stats)):
  reitzlist.append(reitz_stats[line]['properties']['mean']);
  reitzhuclist.append(reitz_stats[line]['properties']['GAGE_ID']);

for line in range(len(glass_stats)):
  glasslist.append(glass_stats[line]['properties']['mean']);
  glasshuclist.append(glass_stats[line]['properties']['GAGE_ID']);

swbdf = pd.DataFrame(data={'huc': huclist, 'mean_swb': swblist, 'mean_PART': partlist} )
reitzdf = pd.DataFrame(data={'huc': huclist, 'mean_glass': reitzlist} )
glassdf = pd.DataFrame(data={'huc': huclist, 'mean_reitz': glasslist} )
