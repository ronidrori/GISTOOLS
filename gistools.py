#-------------------------------------------------------------------------------
# Name:        gistools
# Purpose:
#
# Author:      roni
#
# Created:     28/05/2013
# Copyright:   (c) roni 2013
# Licence:     CC
#-------------------------------------------------------------------------------

from osgeo import ogr
from os.path import basename, splitext
from pyper import *

def create_memds(ds_name):
    #create memory data source to store results
    #and speed up execution
    mem_drv = ogr.GetDriverByName( 'Memory' )
    mem_ds  = mem_drv.CreateDataSource( ds_name )
    return mem_ds

def creat_memlyr(mem_ds, ds, ds_lyr, lyr_name, geom=0):
    """
    mem_ds: the memory datasource
    ds: reference layer data source
    ds_lyr: reference layer
    lyt_name: created memory layer name
    """
    # use ref_lyr to as template to memlyr
    ref_lyr = ds.GetLayerByName( ds_lyr )
    proj      = ref_lyr.GetSpatialRef()
    if geom ==0:
        geom      = ref_lyr.GetGeomType()
    lyr_def   = ref_lyr.GetLayerDefn ()
    mem_layer = mem_ds.CreateLayer( lyr_name, proj, geom )

    # create attribute table
    for i in range(lyr_def.GetFieldCount()):
        mem_layer.CreateField ( lyr_def.GetFieldDefn(i) )
    return lyr_name


def read_shplyr(ds_name):
    # read layer from shapefile
    ds = ogr.Open(ds_name)
    lyr_name = splitext(basename(ds_name))[0]
    lyr = ds.GetLayerByName( lyr_name )
    return lyr_name, ds

def create_shplyr(lyr_ds, lyr_name,out_name, driver_name="ESRI Shapefile"):
    ref_lyr = lyr_ds.GetLayerByName( lyr_name )
    proj      = ref_lyr.GetSpatialRef()
    geom      = ref_lyr.GetGeomType()
    lyr_def   = ref_lyr.GetLayerDefn ()

    drv = ogr.GetDriverByName( driver_name )
    ds = drv.CreateDataSource( out_name )
    out_layer = ds.CreateLayer( lyr_name, proj, geom )
    for i in range(lyr_def.GetFieldCount()):
        out_layer.CreateField ( lyr_def.GetFieldDefn(i) )
    for feat in ref_lyr:
        out_layer.CreateFeature(feat)

    return ds


def create_buffer(in_ds,out_ds,inlyr_name,outlyr_name, buf,by_field='none', scale=0):
    #general perpuse buffer
    in_lyr = in_ds.GetLayerByName( inlyr_name )
    out_lyr = out_ds.GetLayerByName( outlyr_name )
    for feat in in_lyr:
        geom = feat.GetGeometryRef()
        feature = feat.Clone()
        if by_field == 'none':
            feature.SetGeometry(geom.Buffer(float(buf)))
        else:
            buf = feature.GetField(by_field)*scale
            feature.SetGeometry(geom.Buffer(float(buf)))
        out_lyr.CreateFeature(feature)
        del geom
    return outlyr_name

def clip(in_ds, inlyr_name, clip_ds, clip_name, out_ds, out_name):
    in_lyr = in_ds.GetLayerByName( inlyr_name )
    clip_lyr = clip_ds.GetLayerByName( clip_name )
    out_lyr = out_ds.GetLayerByName(out_name)
    in_lyr.Clip(clip_lyr,out_lyr)
    return out_name


def erase(in_ds, inlyr_name, erase_ds, erase_name, out_ds, out_name):
    in_lyr = in_ds.GetLayerByName( inlyr_name )
    erase_lyr = erase_ds.GetLayerByName( erase_name )
    out_lyr = out_ds.GetLayerByName(out_name)
    in_lyr.Erase(erase_lyr,out_lyr)

def UnionCascaded(in_ds,inlyr_name,out_layer):
    in_lyr = in_ds.GetLayerByName( inlyr_name )
    in_type=in_lyr.GetGeomType()
    pls = ogr.Geometry(type=in_type)
    dss = ogr.Geometry(type=in_type)
    for ftr in in_lyr:
        dss.AddGeometry(ftr.GetGeometryRef())
    pls = dss.UnionCascaded()

    # now create a layer to store the results
    # ASSUMING this is memory layer
    lyr = creat_memlyr(in_ds, in_ds, inlyr_name, out_layer, geom=3)
    lyr = in_ds.GetLayerByName( out_layer )
    featureDefn = lyr.GetLayerDefn()
    feature = ogr.Feature(featureDefn)
    feature.SetGeometry(pls)
    lyr.CreateFeature(feature)
    pls.Destroy()
    dss.Destroy()
    return out_layer

def grts(in_layer, out_layer, cellsize=10., npoints=10 ):
    """
    Wrapper to R GRTS package
    in_layer: shape file name
    """

    # create R object
    r = R()
    # spatially balanced sampling using GRTS
    r('library(rgdal)')
    r('library(GRTS)')
    # cell size in meters
    r.cellsize = cellsize
    # number of sampling points
    r.npoints = npoints
    r.in_layer = in_layer
    r.out_layer = out_layer
    r.layer_name = splitext(basename(in_layer))[0]

    #read the shapefile
    r('shape<-readOGR(in_layer,layer_name)')
    # generate sample points
    r('smp<-GRTS(shape, cellsize=cellsize, Subset=TRUE)')
    # subset sampling points
    r('pnts<-subset(smp, Ranking <= npoints)')
    r.out_name = splitext(basename(out_layer))[0]
    r.driver = """ESRI Shapefile"""
    r("writeOGR(pnts,out_layer,out_name,driver)")







