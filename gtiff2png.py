#!/usr/bin/python2

#This script takes a GeoTIFF file as input and generates a PNG file of the
#heightmap contained and a text file which contains the latitude and longitude
#of the corners of the image. It probably only works on UNIX-like systems.
#The output files will have the same filename as the input with different extensions.

from osgeo import osr, gdal
import os, sys

#check for correct number of arguments
if (len(sys.argv) != 2):
    print "Usage: ./gtiff2png.py inputFilename"
    exit(0)

inputfilename = sys.argv[1]
basefilename = sys.argv[1].split(".")[0]
textoutput = open(basefilename+".latlng", "w")

ds = gdal.Open(inputfilename)

# get the existing coordinate system
old_cs = osr.SpatialReference()
old_cs.ImportFromWkt(ds.GetProjectionRef())

# create the new coordinate system,
# wgs84 AKA latitude/longitude which Google Maps requires
wgs84_wkt = """
GEOGCS["WGS 84",
    DATUM["WGS_1984",
        SPHEROID["WGS 84",6378137,298.257223563,
            AUTHORITY["EPSG","7030"]],
        AUTHORITY["EPSG","6326"]],
    PRIMEM["Greenwich",0,
        AUTHORITY["EPSG","8901"]],
    UNIT["degree",0.01745329251994328,
        AUTHORITY["EPSG","9122"]],
    AUTHORITY["EPSG","4326"]]"""
new_cs = osr.SpatialReference()
new_cs .ImportFromWkt(wgs84_wkt)

# create a transform object to convert between coordinate systems
transform = osr.CoordinateTransformation(old_cs,new_cs) 

#get the point to transform, pixel (0,0) in this case
width = ds.RasterXSize
height = ds.RasterYSize
gt = ds.GetGeoTransform()

minx = gt[0]
maxx = gt[0] + width*gt[1] + height*gt[2]
miny = gt[3] + width*gt[4] + height*gt[5]
maxy = gt[3]

#get the coordinates in lat long
latlong = transform.TransformPoint(minx,miny)
latlong2 = transform.TransformPoint(maxx,maxy)

#write coordinates to file
textoutput.write(str(latlong[1]))
textoutput.write("\n")
textoutput.write(str(latlong[0]))
textoutput.write("\n")
textoutput.write(str(latlong2[1]))
textoutput.write("\n")
textoutput.write(str(latlong2[0]))
textoutput.write("\n")

#creates color mapping file used by the gdaldem program
color = open("color", "w")
color.write("0% 0 0 0\n100% 255 255 255\n")
color.close()

#bash commands to call gdaldem, which generates the PNG file
os.system("gdaldem color-relief " + inputfilename + " color "+basefilename+".png -of png")

#delete temporary files created by gdaldem
os.system("rm " + basefilename + ".png.aux.xml")
os.system("rm color")
