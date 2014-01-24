#-----------------------------------------------------------
# coding: utf-8
# Mxd2Qgs ver 1.0
# Copyright (C) 2011 Allan Maungu 
# EMAIL: lumtegis (at) gmail.com
# WEB  : http://geoscripting.blogspot.com
# Usage : Exporting ArcMap document layers to Quantum GIS file
# The resulting file can be opened in Quantum GIS
#
# Add command line mode / Author: François Prunayre, Mauro Michielon
#
# Tested on ArcMap 10, Python 2.7 and Quantum GIS 2.0.1
#
# Supported format:
#  * Vector file (eg. shapefile, GDB)
#  * RASTER file (eg. tif, AIG)
#-----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------

# Import system modules
import sys
import getopt
import os
import os.path
import hashlib
import xml.dom.minidom
from xml.dom.minidom import Document
import string
import arcpy


def usage():
    print "mxd2qgs usage:"
    print " --mxd -m   MXD file to process"
    print " --qgs -q   QGS file to produce"
    print " -v         Verbose mode"
    print " -h         Usage"


#Read command line arguments
try:
    optlist, args = getopt.getopt(sys.argv[1:], 'm:q:hv', ["qgs=", "mxd=", "help="])
except getopt.GetoptError as err:
    # print help information and exit:
    print str(err)
    usage()
    sys.exit(2)
    
mxdFile = None
qgsFile = None
verbose = False
for o, a in optlist:
    if o == "-v":
        verbose = True
    elif o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-m", "--mxd"):
        mxdFile = a
    elif o in ("-q", "--qgs"):
        qgsFile = a
    else:
        assert False, "Unhandled option."

print "Converting MXD to QGS file"
print "=========================="
print " MXD: %s" % mxdFile
print " QGS: %s" % qgsFile
mxdExists = os.path.isfile(mxdFile)
if mxdExists == False:
    print "MXD file %s not found." % mxdFile    
    sys.exit()

mapFolder = os.path.dirname(os.path.realpath(mxdFile))
print " Map folder: %s" % mapFolder


qgisVersion = "2.0.1-Dufour"


def hash(str):
  m = hashlib.md5()
  m.update(str)
  return m.hexdigest()




 
# Open the MXD
# Assign current document
#mxd = arcpy.mapping.MapDocument("CURRENT")
# http://help.arcgis.com/en%20/arcgisdesktop/10.0/help/index.html#//00s30000000r000000
mxd = arcpy.mapping.MapDocument(r"%s" % mxdFile)
# TODO: IOError 


print 'Converting mxd ...'


# Dataframe elements
# Retrieve first dataframe of the MXD project
# Is there any way to know which one is the main frame
df = arcpy.mapping.ListDataFrames(mxd)[0]
dfName = df.name
dfDescription = df.description
dfCredits = df.credits
# TODO: Should we handle more than one ?
# for df in arcpy.mapping.ListDataFrames(mxd):
# mxd.activeView = df.name
#   mxd.title = df.name
#    mxd.saveACopy(r"C:\Project\Output\\" + df.name + ".mxd")
#del mxd


# Create the minidom
doc = Document()

# Create the <qgis> base element
qgis = doc.createElement("qgis")
qgis.setAttribute("projectname", dfName)
qgis.setAttribute("version", qgisVersion)

# Add a ref to the mxa in an attribute of the root element
# This will be deleted by QGS if the file is saved.
qgis.setAttribute("mxd", mxdFile)
doc.appendChild(qgis)

# Create the <title> element
title = doc.createElement("title")
title.appendChild(doc.createTextNode(dfName))
qgis.appendChild(title)





unit = doc.createTextNode(df.mapUnits)

xmin1 = doc.createTextNode(str(df.extent.XMin))
ymin1 = doc.createTextNode(str(df.extent.YMin))
xmax1 = doc.createTextNode(str(df.extent.XMax))
ymax1 = doc.createTextNode(str(df.extent.YMax))


# Default EPSG code of the map if none found
defaultCode = "3035"
epsgCode = df.spatialReference.factoryCode

print " EPSG code: %s" % epsgCode
if epsgCode == 0:
    print "   using default EPSG code (ie. %s)" % defaultCode
    epsgCode = defaultCode

srid1 = doc.createTextNode(str(epsgCode))
srid2 = doc.createTextNode(str(epsgCode))
epsg1 = doc.createTextNode(str(epsgCode))
epsg2 = doc.createTextNode(str(epsgCode))

description1 = doc.createTextNode(str(df.spatialReference.name))
description2 = doc.createTextNode(str(df.spatialReference.name))

ellipsoidacronym1 = doc.createTextNode(str(df.spatialReference.name))
ellipsoidacronym2 = doc.createTextNode(str(df.spatialReference.name))

geographicflag1 = doc.createTextNode("true")
geographicflag2 = doc.createTextNode("true")

authid2 = doc.createTextNode("EPSG:"+str(epsgCode))
authid3 = doc.createTextNode("EPSG:"+str(epsgCode))


# Layerlist elements
lyrlist = arcpy.mapping.ListLayers(df)
count1 = str(len(lyrlist))

# mapcanvas
def map_canvas():
    print " > Analyzing map ..."
    # Create the <mapcanvas> element
    mapcanvas = doc.createElement("mapcanvas")
    qgis.appendChild(mapcanvas)
    
    # Create the <units> element
    units = doc.createElement("units")
    units.appendChild(unit)
    mapcanvas.appendChild(units)

    # Create the <extent> element
    extent = doc.createElement("extent")
    mapcanvas.appendChild(extent)

    # Create the <xmin> element
    xmin = doc.createElement("xmin")
    xmin.appendChild(xmin1)
    extent.appendChild(xmin)

    # Create the <ymin> element
    ymin = doc.createElement("ymin")
    ymin.appendChild(ymin1)
    extent.appendChild(ymin)

    # Create the <xmax> element
    xmax = doc.createElement("xmax")
    xmax.appendChild(xmax1)
    extent.appendChild(xmax)

    # Create the <ymax> element
    ymax = doc.createElement("ymax")
    ymax.appendChild(ymax1)
    extent.appendChild(ymax)

    # Create the <projections> element
    projections = doc.createElement("projections")
    mapcanvas.appendChild(projections)

    # Create the <destinationsrs> element
    destinationsrs = doc.createElement("destinationsrs")
    mapcanvas.appendChild(destinationsrs)

    # Create the <spatialrefsys> element
    spatialrefsys = doc.createElement("spatialrefsys")
    destinationsrs.appendChild(spatialrefsys)

    # Create the <proj4> element
    proj4 = doc.createElement("proj4")
    spatialrefsys.appendChild(proj4)

    # Create the <srsid> element
    srsid = doc.createElement("srsid")
    spatialrefsys.appendChild(srsid)

    # Create the <srid> element
    srid = doc.createElement("srid")
    srid.appendChild(srid1)
    spatialrefsys.appendChild(srid)

    # Create the <authid> element
    authid = doc.createElement("authid")
    authid.appendChild(authid2)
    spatialrefsys.appendChild(authid)

    # Create the <description> element
    description = doc.createElement("description")
    description.appendChild(description1)
    spatialrefsys.appendChild(description)

    # Create the <projectionacronym> element
    projectionacronym = doc.createElement("projectionacronym")
    spatialrefsys.appendChild(projectionacronym)

    # Create the <ellipsoidacronym element
    ellipsoidacronym = doc.createElement("ellipsoidacronym")
    ellipsoidacronym.appendChild(ellipsoidacronym1)
    spatialrefsys.appendChild(ellipsoidacronym)

    # Create the <geographicflag> element
    geographicflag = doc.createElement("geographicflag")
    geographicflag.appendChild(geographicflag1)
    spatialrefsys.appendChild(geographicflag)
    



# Legend
def legend_func():
    print " > Analyzing legend ..."
    # Create the <legend> element
    legend = doc.createElement("legend")
    qgis.appendChild(legend)

    for lyr in lyrlist:
        if(lyr.isGroupLayer == False):
            
            # Create the <legendlayer> element
            legendlayer = doc.createElement("legendlayer")
            legendlayer.setAttribute("open", "true")
            legendlayer.setAttribute("checked", "Qt::Checked")
            layerName = lyr.name.encode('utf8')  
            legendlayer.setAttribute("name",str(layerName))
            
            legend.appendChild(legendlayer)

            # Create the <filegroup> element
            filegroup = doc.createElement("filegroup")
            filegroup.setAttribute("open", "true")
            filegroup.setAttribute("hidden", "false")
            legendlayer.appendChild(filegroup)

            # Create the <legendlayerfile> element
            legendlayerfile = doc.createElement("legendlayerfile")
            legendlayerfile.setAttribute("isInOverview", "0")
            legendlayerfile.setAttribute("layerid", hash(layerName))
            legendlayerfile.setAttribute("visible", "1") #TODO visible
            filegroup.appendChild(legendlayerfile)
        
# Project Layers
def project_layers():
    print " > Analyzing layers ..."
    # Create the <projectlayers> element
    projectlayers = doc.createElement("projectlayers")
    projectlayers.setAttribute("layercount", count1)
    qgis.appendChild(projectlayers)

    for lyr in lyrlist:
        layerName = lyr.name.encode('utf8')
        print ""
        print "   > layer %s (group layer: %s)." % (layerName, lyr.isGroupLayer)
        if(lyr.isGroupLayer == False):
            exception = False
            print "     Datasource: %s." % lyr.dataSource
       
            try:
              geometry1 = arcpy.Describe(lyr.dataSource)
            except IOError:
              exception = True
              # Log to file TODO
              print "     IOError on datasource %s." % lyr.dataSource

            # Layer not found are not added to QGS file
            if (exception == False):
              print "     isRasterLayer: %s." % lyr.isRasterLayer
              if(lyr.isRasterLayer == False):
                  geometry2 = str(geometry1.shapeType)
              else:
                  geometry2 = str(geometry1.format)
              
              isGDB = False
              if(geometry1.dataType == "FeatureClass"):
                isGDB = True

              print "     Datatype: %s." % geometry1.dataType
              print "     Shapetype: %s." % geometry2
              print "     isGDB: %s." % isGDB
       
              # TODO: Postgis, Spatialite
              if isGDB:
                  gdbExt = ".gdb"
                  extIndex = lyr.dataSource.find(gdbExt)
                  dsFile = lyr.dataSource[0:extIndex] + gdbExt
                  ds = doc.createTextNode(str(dsFile + "|layername=" + lyr.name))
              else:
                  ds = doc.createTextNode(str(lyr.dataSource))


              name1 = doc.createTextNode(hash(layerName))
              name2 = doc.createTextNode(str(layerName))
                     
             # Create the <maplayer> element
              maplayer = doc.createElement("maplayer")
              maplayer.setAttribute("minimumScale", "0")
              maplayer.setAttribute("maximumScale", "1e+08")
              maplayer.setAttribute("minLabelScale", "0")
              maplayer.setAttribute("maxLabelScale", "1e+08")
              maplayer.setAttribute("geometry", geometry2)
              if(lyr.isRasterLayer == True):
                  maplayer.setAttribute("type", "raster")
              else:
                  maplayer.setAttribute("type", "vector")
              maplayer.setAttribute("hasScaleBasedVisibilityFlag", "0")
              maplayer.setAttribute("scaleBasedLabelVisibilityFlag", "0")
              projectlayers.appendChild(maplayer)
  
              # Create the <id> element
              id = doc.createElement("id")
              id.appendChild(name1)
              maplayer.appendChild(id)
  
              # Create the <datasource> element
              datasource = doc.createElement("datasource")
              datasource.appendChild(ds)
              maplayer.appendChild(datasource)
  
              # Create the <layername> element
              layername = doc.createElement("layername")
              layername.appendChild(name2)
              maplayer.appendChild(layername)
  
              # Create the <srs> element
              srs = doc.createElement("srs")
              maplayer.appendChild(srs)
  
              # Create the <spatialrefsys> element
              spatialrefsys = doc.createElement("spatialrefsys")
              srs.appendChild(spatialrefsys)
  
              # Create the <proj4> element
              proj4 = doc.createElement("proj4")
              spatialrefsys.appendChild(proj4)
  
              # Create the <srsid> element
              srsid = doc.createElement("srsid")
              spatialrefsys.appendChild(srsid)
  
              # Create the <srid> element
              srid = doc.createElement("srid")
              srid.appendChild(srid2)
              spatialrefsys.appendChild(srid)
         
  
              # Create the <authid> element
              authid = doc.createElement("authid")
              authid.appendChild(authid3)
              spatialrefsys.appendChild(authid)
  
              # Create the <description> element
              description = doc.createElement("description")
              description.appendChild(description2)
              spatialrefsys.appendChild(description)
  
              # Create the <projectionacronym> element
              projectionacronym = doc.createElement("projectionacronym")
              spatialrefsys.appendChild(projectionacronym)
  
              # Create the <ellipsoidacronym element
              ellipsoidacronym = doc.createElement("ellipsoidacronym")
              ellipsoidacronym.appendChild(ellipsoidacronym2)
              spatialrefsys.appendChild(ellipsoidacronym)
  
              # Create the <geographicflag> element
              geographicflag = doc.createElement("geographicflag")
              geographicflag.appendChild(geographicflag2)
              spatialrefsys.appendChild(geographicflag)
          
              # Create the <transparencyLevelInt> element
              transparencyLevelInt = doc.createElement("transparencyLevelInt")
              transparency2 = doc.createTextNode("255")
              transparencyLevelInt.appendChild(transparency2)
              maplayer.appendChild(transparencyLevelInt)
  
              # Create the <customproperties> element
              customproperties = doc.createElement("customproperties")
              maplayer.appendChild(customproperties)
  
              if(lyr.isRasterLayer == False):
                  # Create the <provider> element
                  provider = doc.createElement("provider")
                  provider.setAttribute("encoding", "System")
                  ogr = doc.createTextNode("ogr")
                  provider.appendChild(ogr)
                  maplayer.appendChild(provider)
  
              # Create the <singlesymbol> element
              singlesymbol = doc.createElement("singlesymbol")
              maplayer.appendChild(singlesymbol)
  
              # Create the <symbol> element
              symbol = doc.createElement("symbol")
              singlesymbol.appendChild(symbol)
  
              # Create the <lowervalue> element
              lowervalue = doc.createElement("lowervalue")
              symbol.appendChild(lowervalue)
  
              # Create the <uppervalue> element
              uppervalue = doc.createElement("uppervalue")
              symbol.appendChild(uppervalue)
  
              # Create the <label> element
              label = doc.createElement("label")
              symbol.appendChild(label)
  
              # Create the <rotationclassificationfieldname> element
              rotationclassificationfieldname = doc.createElement("rotationclassificationfieldname")
              symbol.appendChild(rotationclassificationfieldname)
  
              # Create the <scaleclassificationfieldname> element
              scaleclassificationfieldname = doc.createElement("scaleclassificationfieldname")
              symbol.appendChild(scaleclassificationfieldname)
  
              # Create the <symbolfieldname> element
              symbolfieldname = doc.createElement("symbolfieldname")
              symbol.appendChild(symbolfieldname)
  
              # Create the <outlinecolor> element
              # TODO improve getting style
              # TODO: what to do with styling http://resources.arcgis.com/fr/help/main/10.1/index.html#//00s30000006z000000
              outlinecolor = doc.createElement("outlinecolor")
              outlinecolor.setAttribute("red", "88")
              outlinecolor.setAttribute("blue", "99")
              outlinecolor.setAttribute("green", "37")
              symbol.appendChild(outlinecolor)
  
               # Create the <outlinestyle> element
              outlinestyle = doc.createElement("outlinestyle")
              outline = doc.createTextNode("SolidLine")
              outlinestyle.appendChild(outline)
              symbol.appendChild(outlinestyle)
  
               # Create the <outlinewidth> element
              outlinewidth = doc.createElement("outlinewidth")
              width = doc.createTextNode("0.26")
              outlinewidth.appendChild(width)
              symbol.appendChild(outlinewidth)
  
               # Create the <fillcolor> element
              fillcolor = doc.createElement("fillcolor")
              fillcolor.setAttribute("red", "90")
              fillcolor.setAttribute("blue", "210")
              fillcolor.setAttribute("green", "229")
              symbol.appendChild(fillcolor)
  
               # Create the <fillpattern> element
              fillpattern = doc.createElement("fillpattern")
              fill = doc.createTextNode("SolidPattern")
              fillpattern.appendChild(fill)
              symbol.appendChild(fillpattern)
  
               # Create the <texturepath> element
              texturepath = doc.createElement("texturepath")
              texturepath.setAttribute("null", "1")
              symbol.appendChild(texturepath)


# TODO: export to PNG http://help.arcgis.com/en%20/arcgisdesktop/10.0/help/index.html#/ExportToPNG/00s30000002s000000/
# to have a thumbnail of the map
# arcpy.mapping.ExportToPNG(mxd, r"C:\Project\Output\Project.png")
def create_map_thumbnail():
    thumbnailFile = "%s.png" % qgsFile

    print " > Creating thumbnail ..."
    print "   Thumbnail: %s" % thumbnailFile
    try:
        arcpy.mapping.ExportToPNG(mxd, r"%s" % thumbnailFile)
    except AttributeError:
        print "  Error generating thumbnail."


# Add map properties
def map_properties():
    props = doc.createElement("properties")
    
    title = doc.createElement("WMSServiceTitle")
    title.appendChild(doc.createTextNode(dfName))
    title.setAttribute("type", "QString")
    props.appendChild(title)
    
    desc = doc.createElement("WMSServiceAbstract")
    desc.appendChild(doc.createTextNode(dfDescription))
    desc.setAttribute("type", "QString")
    props.appendChild(desc)
    qgis.appendChild(props)


    
map_canvas()
legend_func()
project_layers()
map_properties()
create_map_thumbnail()

# Create an output qgs file
f = open(qgsFile, "w")
try:
    unistr = doc.toprettyxml(encoding="utf-8")
    f.write(unistr)
    # TODO set file date
    #xml.dom.ext.PrettyPrint(doc, f)
finally:
    f.close()

print 'Done.'



