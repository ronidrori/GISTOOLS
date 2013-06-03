#-------------------------------------------------------------------------------
# Name:        samples
# Purpose:
#
# Author:      Ron Drori
#
# Created:     29/05/2013
# Copyright:   (c) hamaarag 2013
# Licence:     CC
#-------------------------------------------------------------------------------

"""
Script to create sample points,polygons and plots
for hamaarag monitoring program.

"""


from gistools import *
import time

print time.strftime('%X %x %Z')

# layer files
site_file = "G:\\Data\\diary\\4_13\\14\\harhanegev_stlmnt.shp"
road_file = "G:\\Data\\GIS\\infrastructure\\roads_infl99.shp"

#first read sites file
site_name, sites = read_shplyr(site_file)

#read roads file
road_name,roads = read_shplyr(road_file)

#Create memory data source to save result (mem_ds)
mem_ds = create_memds("Results")

#Create layer in memory data source to store buffer results (buf_lyr)
nearbuf_lyr = creat_memlyr(mem_ds, sites, site_name, 'near buffer')
farbuf_lyr = creat_memlyr(mem_ds, sites, site_name, 'far buffer')
road_lyr = creat_memlyr(mem_ds, roads, road_name, 'roads')
road_buf = creat_memlyr(mem_ds, roads, road_name, 'roadsbuf', geom=6) #wkbMultiPolygon
site_erase = creat_memlyr(mem_ds, sites, site_name, 'erase buffer')
#road_buf_dis =

#do buffer
near_buf=500.
far_buf = 2500.
nearbuf = create_buffer(sites,mem_ds,site_name,nearbuf_lyr, near_buf)
farbuf = create_buffer(sites,mem_ds,site_name,farbuf_lyr, far_buf)


#create road buffer
#first clip
roadclip = clip(roads, road_name, mem_ds, nearbuf, mem_ds, road_lyr)
road_buf = create_buffer(mem_ds,mem_ds, roadclip, road_buf, buf,by_field='WIDTH1', scale=2.)
#road_buf_dis = UnionCascaded(mem_ds, road_buf,'union')
#erase(mem_ds,nearbuf_lyr,mem_ds,road_buf,mem_ds,site_erase)

#write result layer out
#res = create_shplyr(mem_ds,road_buf_dis,'g:\\data\\test\\uc7.shp')
res1 = create_shplyr(mem_ds,road_buf,'g:\\data\\test\\rdbf1.shp')
#res.Destroy()
res1.Destroy()
mem_ds.Destroy()
print time.strftime('%X %x %Z')

#======
mem_ds = create_memds("Results")
in_layer = 'g:/data/test/rdbf1.shp'
out_layer = 'g:/data/test/bufsamp10.shp'
grts(in_layer,out_layer,cellsize=100.,npoints=10)
#res1 = create_shplyr(mem_ds,'ranked','g:\\data\\test\\pranke.shp')

# TODO
# ====

#2. connect to R (for GRTS)


