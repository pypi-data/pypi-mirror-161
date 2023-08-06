#%%
"""
Here we find tools to process georeferenced rasters.
Thoses tools formed two categories :
    - there is functions to work directly on osgeo.gdal.Dataset
      more friendly and with a more intuitive syntax than the
      osgeo.gdal functions and osgeo.gdal.Dataset methods.

    - and a class called GeoIm. The main interest of this class
      is to place in the same place an array, and a osgeo.gdal.
      Dataset. You don't have to call osgeo.gdal.Dataset.ReadAs
      Array() because the array is computed only when it's man-
      datory, after a gdal.Warp resampling or reprojection for
      example.
"""

# Standard librairies
import os
import re
import json

# Third-Party libraries
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageEnhance

import shapely
import richdem as rd
import geopandas as gpd
from osgeo import gdal, gdalconst, osr, ogr

class GeoIm:

    """
    Describe a georeferenced image. A pixel represent a part of the space.
    Each pixel represent same size space-unit.

    attributes
    ----------

        name        | type       | short description
            --------------------------------------------------------------------------------------------
        array       | np.ndarray |  each pixel is charachterized by one or many values. 
                    |            |  Here, they're stored in an object called array or matrix. 
                    |            |                                
                    |            |  This array have 2 dimensions (x,y) if the image 
                    |            |  represented is monospectral (only one channel),
                    |            |  and in this case, each pixel is just one numerical value.
                    |            |  
                    |            |  But the array can have 3 dimensions (channel, x, y) 
                    |            |  if the image is multispectral. 
                    |            |  
                    |            |  This mean the image was acquired with many shortwaves 
                    |            |  length, and this is how we build some color images 
                    |            |  with a red, a blue and a green channel, for example.
            --------------------------------------------------------------------------------------------
        ds          |gdal.Dataset|  Contain all the geo-attributes of the image : the dimensions 
                    |            |  of the space unit represented by his pixels (wrongly commonly 
                    |            |  called "spatial resolution"), the coordinates of his origin
                    |            |  point, the name of the Coordinates System Reference in which
                    |            |  are wrote this coordinates 

    methods
    -------
        The methods of GeoIm objects can be split in 3 parts. 

        Part 1 : the getters
            This kind of methods will help you to get all the lovely geo-data, contained 
            in the osgeo.gdal.Dataset of each GeoIm instance, because use directly this 
            Dataset can sometimes be not very easy or natural. All this functions-names
            start by "get" like "getPixelSize()" or "getGeomExtent()". Except the function
            to get the number of bands, the height and the width of an image, because this
            one is called "shape" to looks like the .shape attribute of a numpy.ndarray.

             name               | arguments             | short description
            --------------------------------------------------------------------------------------------
             getOriginPoint     |                       | send a tuple : (originX, originY) 
                                |                       | this coordinates are wrote in the 
                                |                       | Coordinates Reference System 
                                |                       | of the image
            --------------------------------------------------------------------------------------------
             getPixelSize       |                       | send a tuple : (resX, resY)
                                |                       |  or (pixelSizeX, pixelSizeY)
            --------------------------------------------------------------------------------------------
             getCoordsExtent    |                       | send a tuple : 
                                |                       | (xMin, yMin, xMax, yMax)
            --------------------------------------------------------------------------------------------
             getGeomExtent      | mode : str            | send a geometry. If the mode is "ogr", 
                                | default="ogr"       | it's osgeo.ogr.geometry object. If 
                                |                       | the mode is "shapely", it send a 
                                |                       | shapely.geometry.Polygon. 
            --------------------------------------------------------------------------------------------
             shape              |                       | send a tuple : 
                                |                       | (numberOfBands, 
                                |                       |  numberOfRows, 
                                |                       |  numberOfCols)
            --------------------------------------------------------------------------------------------
             copy               |                       | send a new GeoIm instance, 
                                |                       | which is a copy of this from where 
                                |                       | the method is called
            --------------------------------------------------------------------------------------------

        Part 2 : the setters
            This kind of methods will help you to manipulate your GeoIm instances: You can
            change the size-space unit of the pixels of an image, the SCR, the origin point

             name               | arguments             | short description
            --------------------------------------------------------------------------------------------
             shiftOriginPoint   |                       | offsetX is added to the origin X of the GeoIm.    
                                | offsetX : float       | offsetY is added to the origin Y of the GeoIm.
                                | offsetY : float       | if inplace, change the originPoint of the instance.
                                | inplace : bool        | It can be used to literally move the image in space.
                                |   default=True      | if not inplace, send a new geoim
                                |                       | with the new origin.
            --------------------------------------------------------------------------------------------
             cropFromVector     | vector : str          | vector can be a path to a shapefile.
                                |   or shapely.geometry | In this case, the argument polygon
                                | polygon : int         | is used to extract only one polygon
                                |   default=0         | of this shapefile. This polygon is
                                |                       | next converted in shapely.geometry.
                                |                       | Polygon. Or, vector can be directly
                                |                       | a shapely geometry Polygon.
            --------------------------------------------------------------------------------------------
            cropFromRaster      |master_ds : str        | master_ds mean the dataset on which
                                |  or osgeo.gdal.Dataset| the input GeoIm is cropped. It 
                                |                       | either a path to raster, or dir
                                |                       | an osgeo.gdal.Dataset object. 
            --------------------------------------------------------------------------------------------
            cropFromIndex       |index : tuple          | index indicate the part of the array
                                |(col1,row1,col2,row2)  | the user want to select.
            --------------------------------------------------------------------------------------------
            resize              | xRes : float or int   | modify the size of the space-unit
                                |   the new pixel size  | represented by each pixel of the 
                                |   along the X axe     | GeoIm instance's. 
                                | yRes : float or int   | 
                                | method : str          |
                                |   the resampling algo |
                                |       "near"          |
                                |       "bilinear"      |
                                |       "cubic"         |
                                |       "cubicspline"   |
                                |       "lanczos"       |
                                |       "average"       |
                                |       "rms"           |
                                |       "max"           |
                                |       "min"           |
                                |       "med"           |
                                |       "q1"            |
                                |       "q3"            |
                                |       "sum"           |
            --------------------------------------------------------------------------------------------
            stack               | ls_geoim : list       | make a geoim with multiple channels.
                                |                       | each geoim in the ls_geoim must have
                                |                       | precisely the same number of rows and
                                |                       | columns. 
            --------------------------------------------------------------------------------------------
            save                | outpath : str         | write the geoim into a raster file.
                                | driverName:file format|
                                |   default="GTiff"   |
            --------------------------------------------------------------------------------------------            
            merge               | ls_geoim : list       | send a geoim containing the instance 
                                |                       |  + all the geoims contained in ls_geoim
            --------------------------------------------------------------------------------------------
            makeMosaic          | nbSquaresByAx : int   | send a list containing others geoims,
                                |                       | which are a part of the instance.
                                |                       | For example, if nbSquaresByAx=2,
                                |                       | you get a list with 4 geoims.
                                |                       | The first is the top left part of the current geoim,
                                |                       | the second is his bottom left part,
                                |                       | the third is his top right part,
                                |                       | and the last is his bottom left part.
    """

    def __init__(self, ds, array=None):

        if type(ds) == str:
            self.ds=gdal.Open(ds)

        elif type(ds) == gdal.Dataset:
            self.ds=ds

        if type(array) == np.ndarray or type(array) == rd.rdarray:
                self.array=array
        else:
            # print("Read as array from GeoIm.__init__ function")
            self.array=self.ds.ReadAsArray()

    def __add__(self, n):
        if type(n) == GeoIm:
            n=n.array
        result=self.array + n
        new=GeoIm(self.ds, result)
        new._updateDs()
        return new

    def __sub__(self, n):
        if type(n) == GeoIm:
            n=n.array
        result=self.array - n
        new=GeoIm(self.ds, result)
        new._updateDs()
        return new
    
    def __mul__(self, n):
        if type(n) == GeoIm:
            n=n.array
        result=self.array * n
        new=GeoIm(self.ds, result)
        new._updateDs()
        return new
    
    def __truediv__(self, n):
        if type(n) == GeoIm:
            n=n.array
        result=self.array / n
        new=GeoIm(self.ds, result)
        new._updateDs()
        return new

    def __pow__(self, power):
        if type(power) == GeoIm:
            power=power.array
        result=self.array ** power
        new=GeoIm(self.ds, result)
        new._updateDs()
        return new        

    def _updateArray(self):
        """
        Update instance's array from his dataset
        """
        print("read as array from GeoIm._updateArray function")
        self.array=self.ds.ReadAsArray()

    def _updateDs(self, geodata=None):
        """
        Update instance's dataset from his array
        """

        # Get geographic informations
        if geodata == None:
            xRes, yRes=self.getPixelSize()
            orX, orY=self.getOriginPoint()
            crs=self.ds.GetProjection()

        else:
            orX, xRes, orY, yRes, crs=geodata

        # Make a new memory dataset
        newds=makeDs(
            "",
            self.array,
            orX,
            xRes,
            orY,
            yRes,
            crs,
            "MEM")

        # Update instance dataset
        self.ds=newds

    def __repr__(self):
        print(
f"""pixel size : {self.getPixelSize()}
origin     : {self.getOriginPoint()}
bands      : {self.shape()[0]}
rows       : {self.shape()[1]}
columns    : {self.shape()[2]}
SCR epsg   : {self.getEpsg()}
SCR name   : {self.getProjName()}
array type : {self.array.dtype}
""")
        return ""

    def __getitem__(self, index):
        return self.array[index]

    def copy(self):
        """
        send a copy of the current instance
        """
        return GeoIm(self.ds, array=self.array)

    def shape(self):
        """
        send a tuple (numBands, numRows, numCols)
        """
        return getBandsRowsColsFromArray(self.array)

    def getWestEastLength(self):
        xMin, _, xMax, _=self.getCoordsExtent()
        return xMax - xMin
    
    def getNorthSouthLength(self):
        _, yMin, _, yMax=self.getCoordsExtent()
        return yMax - yMin
        
    def getArea(self):
        return round(self.getWestEastLength() * self.getNorthSouthLength())

    def getEpsg(self):
        """
        send the spatial coordinates reference system epsg id
        """
        try :
            return getDsEpsg(self.ds)
        except KeyError:
            return "unknown"

    def getProjName(self):
        """
        send the spatial coordinates reference system name
        """
        try :
            return getDsProjName(self.ds)
        except KeyError:
            return "unknown"

    def getOriginPoint(self):
        """
        send a tuple (originX, originY)
        """
        return getDsOriginPoint(self.ds)

    def getPixelSize(self):
        """
        send a tuple (pixelSizeX, pixelSizeY)
        """
        return getDsPixelSize(self.ds)

    def getGeomExtent(self, mode="OGR"):
        """
        :descr:
            compute the geographic extent of the current instance

        :params:
            mode : str - describe the type of the geometry.
                   default='OGR'
                   alternative='SHAPELY'

        :return:
            geom : osgeo.ogr.geometry or shapely.geometry.polygon
                a geometry representing the extent
        """
        return getGeomExtent(self.ds, mode=mode)

    def getCoordsExtent(self):
        """
        send a tuple(xMin, yMin, xMax, yMax)
        """
        return getDsCoordsExtent(self.ds)

    def shiftOriginPoint(self, offsetX, offsetY, inplace=False):
        """
        :descr:
            offsetX is added to the origin X of the GeoIm.    
            offsetY is added to the origin Y of the GeoIm.

        :params:
            offsetX : float - 
                The distance to shift the image origin point
                (in general, north-west corner) along the X axe. 
                Exprimate in a coordinates system reference 
                space unit ( meters or degrees, according to 
                the SCR).

            offsetY : float -
                same as offsetX but for the Y axe.

            inplace : boolean

        :return:
            if inplace, send a new geoim shifted.
            else, modify the current instance itself and return None.
            """

        shiftedDs=shiftDsOriginPoint(self.ds, offsetX, offsetY)
        if inplace:
            self.ds=shiftedDs
            return self

        # On connaît l'array, elle ne change pas. Donc, inutile de la re-déduire du dataset
        # dans la fonction d'initialisation du nouveau GeoIm.
        else:
            return GeoIm(shiftedDs, array=self.array)

    def cropFromVector(self, vector, polygon=0, inplace=False):
        """
        :descr:
            cut the image according to a vector geometry

        :params:
            vector : str or shapely.geometry.polygon -
                describe the spatial extent on which the image 
                will be cropped. If it's a string, it must be
                a path to a shapefile. 

            polygon (facultative) : int
                if the vector argument is a path to shapefile,
                this argument specify the id of the polygon
                inside this shapefile to use

            inplace : boolean

        :return:
            if inplace, send a new geoim cropped.
            else, modify the current instance itself and return None.
        
        """

        crop_ds=cropDsFromVector(self.ds, vector, polygon=polygon)

        if inplace:
            self.ds=crop_ds
            self.array=self.ds.ReadAsArray()
            return self
        else:
            return GeoIm(crop_ds)
        
    def cropFromRaster(self, master_ds, inplace=False):
        """
        :descr:
            cut the image according to another raster extent

        :params:
            master_ds : str or osgeo.gdal.Dataset -
                describe the spatial extent on which the image 
                will be cropped. If it's a string, it must be
                a path to a raster file. 

            inplace : boolean

        :return:
            if inplace, send a new geoim cropped.
            else, modify the current instance itself and return None.
        
        """
        if type(master_ds) == GeoIm:
            master_ds=master_ds.ds

        crop_ds=cropDsFromRaster(self.ds, master_ds)
        if inplace:
            self.ds=crop_ds
            self.array=self.ds.ReadAsArray()
            return self
        else:
            return GeoIm(crop_ds)

    def cropFromIndex(self, col1, row1, col2, row2, inplace=False):

        """
        :descr:
            cut the image according to an matrixian area

        :params:
            index : tuple -
                (firstColumn, firstRow, lastColumn, lastRow)
                describe the matrixian extent on which the image 
                will be cropped.

            inplace : boolean

        :return:
            if inplace, send a new geoim cropped.
            else, modify the current instance itself and return None.
        
        """
        if inplace: 
            target=self
        else:
            target=self.copy()

        # Crop the array
        nBands=target.shape()[0]
        if nBands == 1:
            target.array=target.array[row1:row2, col1:col2]
        else:
            target.array=target.array[0:nBands, row1:row2, col1:col2]

        # Get Metadata
        xRes, yRes=target.getPixelSize()
        old_orX, old_orY=target.getOriginPoint()

        # Compute new origin point
        new_orX=old_orX + (col1 * xRes)
        new_orY=old_orY + (row1 * yRes)

        # Update the dataset's instance
        target._updateDs((new_orX, xRes, new_orY, yRes, target.ds.GetProjection()))

        return target

    def resize(self, xSize, ySize, method="near", inplace=False):
        """
        :descr:
            change the spatial size of the pixels, sometimes
            (wrongly) called "spatial resolution"

        :params:
            xSize : float - the X pixel size
            ySize : float - the Y pixel size
            method : str - the resampling algorithm
                default="near"
                type help(telenvi.raster_tools.resizeDs) to see
                all the alternative methods
            inplace : boolean

        :return:
            if inplace, send a new geoim resampled.
            else, modify the current instance itself and return None.
        
        """

        res_ds=resizeDs(self.ds, xSize, ySize, method)
        if inplace:
            self.ds=res_ds
            self._updateArray()
            return self
        else:
            return GeoIm(res_ds)

    def stack(self, ls_geoim, inplace=False):
        """
        :descr:
            stack geoim's arrays

                -------------    -------------    -------------    
              /             /  /             /  /             /    
             /      A      /  /      B      /  /      C      /     
            /             /  /             /  /             /      
            -------------    -------------    -------------     

                                   \/

                              ------------- 
                            /             / 
                           /      A      /-  
                          /             / /
                          -------------  /-
                          /      B      / /
                          -------------  /
                          /      C      /
                          -------------

        :params:
            ls_geoim : list
                a list containing telenvi.raster_tools.GeoIm objects
            inplace: boolean

        :return:
            if inplace, send a new geoim stacked.
            else, modify the current instance itself and return None.
        """
        if inplace:
            target=self.copy()
        else:
            target=self

        ls_ar=[self.array] + [geoim.array for geoim in ls_geoim]
        stack_ar=np.array(ls_ar)
        target.array=stack_ar
        target._updateDs()

        return target

    def merge(self, ls_geoim, inplace=False):
        """
        :descr:
            merge geoim's arrays : 

                -------------    -------------    -------------    
              /             /  /             /  /             /    
             /      A      /  /      B      /  /      C      /     
            /             /  /             /  /             /      
            -------------    -------------    -------------     

                                   \/

                  ---------------------------------------
                /                                       /  
               /                  ABC                  / 
              /                                       /  
              ---------------------------------------
  
        :params:
            ls_geoim : list
                a list containing telenvi.raster_tools.GeoIm objects
            inplace: boolean

        :return:
            if inplace, send a new geoim merged.
            else, modify the current instance itself and return None.
        """
        ls_ds=[self.ds] + [geoim.ds for geoim in ls_geoim]
        merged_ds=mergeDs(ls_ds)
        if inplace:
            self.ds=merged_ds
            self._updateArray()
            return self
        else:
            return GeoIm(merged_ds)

    def makeMosaic(self, thumbsY=2, thumbsX=2):
        
        """
        :descr:
            display one band of the GeoIm

                    ---------------------------------------
                  /                                       /  
                 /                                       / 
                /                 ABCD                  /  
               /                                       /
              /                                       / 
             /                                       /                
             ----------------------------------------  
                                  \/
    
                  -------------            -------------   
                /             /          /             /   
               /      A      /          /      B      /    
              /             /          /             /     
              -------------            -------------    
                                 
             -------------            -------------   
           /             /          /             /   
          /      C      /          /      D      /    
         /             /          /             /     
         -------------            -------------    

        :params:
            nbSquaresByAx : int
                default : 2
                the number of cells to cells along the X size and the Y size
                from the current instance. 2 means you will have 4 GeoIms in
                return. The current instance will be split in 2 lines and 2 cols.

        :returns:
            mosaic : list
                a list of GeoIms
        """

        cells_nRows=int(self.shape()[1]/thumbsY)
        cells_nCols=int(self.shape()[2]/thumbsX)

        mosaic=[]
        for row in range(thumbsY):
            for col in range(thumbsX):
                row1=cells_nRows * row
                col1=cells_nCols * col
                row2=row1 + cells_nRows
                col2=col1 + cells_nCols
                mosaic.append(self.cropFromIndex(col1, row1, col2, row2))

        return mosaic

    def splitBands(self):
        nBands=self.shape()[0]

        if nBands == 1:
            return self.copy()

        elif nBands > 1:
            bands=[]
            for band in self.array:
                new=GeoIm(self.ds, band)
                new._updateDs()
                bands.append(new)

            return bands

    def save(self, outpath, driverName="GTiff"):
        """
        :descr:
            Create a raster file from the instance
        
        :params:
            outpath : str
                the path of the output file
            driverName : str
                default="GTiff"
                the outputfile format

        :returns:
            None
        """

        save(self, outpath, self.array, driverName)

    def quickVisual(self, index=None, band=0, colors="viridis"):

        """
        :descr:
            display one band of the GeoIm
        
        :params:
            index : tuple
                default : None - all the image is displayed.
                alternative : (firstColumn, firstRow, lastColumn, lastRow)
                described a matrixian area to display

            band : int
                default=0
                the index of the band to display if the geoim is multispectral

        :returns:
            None
        """

        # Compute nCols and nRows
        nBands, nRows, nCols=self.shape()
        if index == None:
            col1, row1, col2, row2=0, 0, nCols-1, nRows-1
        else:
            col1, row1, col2, row2=index

        # Plot
        if nBands > 1:
            plt.imshow(self.array[band][row1:row2, col1:col2], cmap=colors)

        else:
            plt.imshow(self.array[row1:row2, col1:col2], cmap=colors)

        plt.show()
        plt.close()
        return None

    def rgbVisual(self, colorMode=[0,1,2], resize_factor=1, brightness=1, show=False, path=None):

        """
        :descr:
            display 3 bands of the GeoIm in RGB mode
        
        :params:
            colorMode : list or tuple
                the order of the 3 bands to display

            resize_factor : int
                default : 1
                allow to "zoom" on the image if the area is to 
                small to be correctly visualized

            brightness : int
                default : 1
                allow to improve the RGB composition brightness. 

            show : boolean
                default : False
                if True,the image is displayed in the os system image reader.
                when this method is called from a Jupyter Notebook, 
                there's no need to set it on True
            
            path : str
                default : None
                if not None, the image is not displayed but saved to this path

        :returns:
            rgb : PIL.Image
                a RGB image        
        """

        _, nRows, nCols=self.shape()

        if len(self.array.shape) != 3:
            raise AttributeError("You need a GeoIm in 3 dimensions to display a GeoIm in RGB")

        if self.array.shape[0] < 3:
            raise AttributeError("The GeoIm have only {} channel and we need 3 channels to display it in RGB")

        # Convert array into RGB array

        # Unpack the RGB components is separates arrays
        r=self.array[colorMode[0]]
        g=self.array[colorMode[1]]
        b=self.array[colorMode[2]]

        # data normalization between [0-1]
        r_norm=(r - r[r!=0].min()) / (r.max() - r[r!=0].min()) * 255
        g_norm=(g - g[g!=0].min()) / (g.max() - g[g!=0].min()) * 255
        b_norm=(b - b[b!=0].min()) / (b.max() - b[b!=0].min()) * 255

        # RGB conversion
        # --------------

        # Create a target array
        rgb_ar=np.zeros((nRows, nCols, 3))

        # For each cell of the "board"
        for row in range(nRows):
            for col in range(nCols):

                # We get the separate RGB values in each band
                r=r_norm[row][col]
                g=g_norm[row][col]
                b=b_norm[row][col]

                # We get them together in little array
                rgb_pixel=np.array([r,g,b])

                # And we store this little array on the board position
                rgb_ar[row][col]=rgb_pixel

        rgb=Image.fromarray(np.uint8(rgb_ar))

        # Adjust size
        rgb=rgb.resize((nCols * resize_factor, nRows * resize_factor))

        # Adjust brightness
        enhancer=ImageEnhance.Brightness(rgb)
        rgb=enhancer.enhance(brightness)

        # Display
        if show:
            rgb.show()

        # Save
        if path != None:
            rgb.save(path)

        # Return PIL.Image instance
        return rgb

def openGeoRaster(
    rasterPath,
    crop=None,
    pol=0,
    clip=None,
    numBands= None,
    epsg=None,
    res=None,
    resMethod="near",
    ds_mode=False,
    verbose=False,
    ):

    """
    :descr:
        create a GeoIm object from a raster file.
        you can specify a lot of settings to this function to setup the future GeoIm.
    
    :params:

        mandatory : 
            rasterPath : str
                the path to the raster file to open

        facultative :
            crop : str or tuple
                if str, this argument is a path to a shapefile or to a rasterfile
                if tuple, it should be structured as follow : (firstCol, firstRow, lastCol, lastRow). 
                Each value is exprimated in matrixian coordinates.

            pol : int
                if crop is a path to a shapefile, pol specify the id of the polygon to use as work
                extent. 
            
            clip : str or GeoIm
                A path to an other raster file or a GeoIm object.
                This case is different than just "crop" according to another
                raster file because here, the resolution, the xOrigin and yOrigin and the spatial 
                projection are setup according to this other raster file.
                In output, you got a geoim containing the data of the raster file given as rasterPath,
                with exactly the same number of rows / cols, the same CRS, the same extent and the same
                spatial origint than the clip raster.
            
            numBands: int or list
                the indexes of the bands to load if the rasterPath is multispectral
            
            epsg: int
                the epsg of a Coordinates System Reference. The GeoIm is reproject in this CRS.

            res : float
                the spatial size of the pixels, sometimes (wrongly) called "spatial resolution"

            resMethod : str
                default : near
                the algorithm to use for change the pixel's spatial size
            
            verbose: boolean
                default : False
                write informations about the geoim preparation
            
            ds_mode : boolean
                default : True
                load or not the raster array

    :returns:
        ds : an osgeo.gdal.Dataset instance if ds_mode == True
        geoim : a telenvi.raster_tools.GeoIm instance
    """

    if verbose: print("\n")

    # check target path validity
    if not os.path.exists(rasterPath):
        raise ValueError("error 1 : the path doesn't exist")
    
    # Input dataset
    inDs=gdal.Open(rasterPath)
    if inDs == None:
        raise ValueError("error 2 : the file is not a valid raster")

    if clip != None:

        if type(clip) == str:
            master_ds=gdal.Open(clip)

        elif type(clip) == gdal.Dataset:
            master_ds=clip

        elif type(clip) == GeoIm:
            master_ds=clip.ds
    
        # Get input and clip resolutions
        master_resX,_=getDsPixelSize(master_ds)
        input_resX,_=getDsPixelSize(inDs)

        # If the input pixel size is higher than the master pixel size,
        # we order a resample by setting res argument
        if master_resX < input_resX:
            res=master_resX

        # SCR check
        try:
            if getDsEpsg(master_ds) != getDsEpsg(inDs):
                epsg=master_ds

        # In case of ungeoreferenced file
        except KeyError:
            # print("warning : the input file or the clip file is ungeoreferenced")
            pass

    # Reprojection
    if epsg != None:
        if verbose: print(f"reprojection\n---\nin  : {getDsEpsg(inDs)}\nout : {epsg}\n---\n")
        inDs=reprojDs(inDs, epsg)

    # Resample
    if res != None:
        if verbose: print(f"resample\n---\nin     : {getDsPixelSize(inDs)[0]}\nout    : {res}\nmethod : {resMethod}\n---\n")
        inDs=resizeDs(inDs, xRes=res, yRes=res, resMethod=resMethod)

    # Crop
    if type(crop) == str:
        if crop[-4:].lower() == ".shp":
            inDs=cropDsFromVector(inDs, crop, polygon=pol, verbose=verbose)
        elif gdal.Open(crop) != None:
            inDs=cropDsFromRaster(inDs, crop, verbose=verbose)
    
    elif type(crop) in [list, tuple]:
        # xMin, yMin, xMax, yMax
        if verbose: print(f"crop\n---\nxMin : {crop[0]}\nyMin : {crop[1]}\nxMax : {crop[2]}\nyMax : {crop[3]}\n---\n")
        inDs=cropDsFromIndex(inDs, crop)

    if clip != None:
        # Here we make a special crop, by changing the origin coordinates
        inDs=cropDsFromRaster(inDs, master_ds, verbose=verbose)

    # Extract interest band
    if numBands!= None:
        if verbose: print(f"extract bands\n---\n{numBands}\n---\n")
        inDs=chooseBandFromDs(inDs, numBands)

    # Send ds and not geoim, to avoid read as array step
    if ds_mode :
        print(f"\nosgeo.gdal.Dataset from file {os.path.basename(rasterPath)} ready\n")
        return inDs

    else :
        geoim=GeoIm(inDs)
        print(f"\ngeoim from file {os.path.basename(rasterPath)} ready\n")
        return geoim

def openManyGeoRaster(
    directory,
    pattern,
    endKeyPos=-4,
    crop=None,
    pol=0,
    clip=None,
    numBands= None,
    epsg=None,
    res=None,
    resMethod="near",
    verbose=False
    ):

    # Compile pattern with regular expression
    rpattern=re.compile(pattern.upper())

    x={}
    for fileName in sorted(os.listdir(directory)):

        try : # Get pattern start position in fileName
            startKeyPos=re.search(rpattern, fileName.upper()).span()[0]

        except AttributeError: # Pattern not find in fileName
            continue
        
        fileBandName=os.path.join(directory, fileName)
        
        # Get the key corresponding to the pattern in the fileName
        bandId=fileName[startKeyPos:endKeyPos]

        # Extract and pack all the data in a lovely dictionnary with bandId as key
        x[bandId]=openGeoRaster(
            rasterPath=fileBandName,
            crop=crop,
            pol=pol,
            clip=clip,
            epsg=epsg,
            res=res,
            numBands= numBands,
            resMethod=resMethod,
            verbose=verbose)

    return x

def getDsOriginPoint(ds):
    """
    ds : osgeo.gdal.Dataset or str
        if str, convert into osgeo.gdal.Dataset with gdal.Open()

    send a tuple (xMin,)
    """
    if type(ds) == str:
        ds=gdal.Open(ds)
    return (ds.GetGeoTransform()[0], ds.GetGeoTransform()[3])

def getDsPixelSize(ds):
    """
    ds : osgeo.gdal.Dataset or str
        if str, convert into osgeo.gdal.Dataset with gdal.Open()

    send a tuple (pixelSizeX, pixelSizeY)
    """

    if type(ds) == str:
        ds=gdal.Open(ds)
    return (ds.GetGeoTransform()[1], ds.GetGeoTransform()[5])

def getDsCoordsExtent(ds):
    """
    ds : osgeo.gdal.Dataset or str
        if str, convert into osgeo.gdal.Dataset with gdal.Open()

    send a tuple (xMin, yMin, xMax, yMax)
    """

    if type(ds) == str:
        ds=gdal.Open(ds)
    nRows, nCols=ds.RasterYSize, ds.RasterXSize
    xMin, yMax=getDsOriginPoint(ds)
    xRes, yRes=getDsPixelSize(ds)
    xMax=xMin + xRes * nCols
    yMin=yMax + yRes * nRows
    return xMin, yMin, xMax, yMax

def getGeomExtent(ds=None, coords=None, mode="OGR"):
    """
    :descr:
        compute the geographic extent of a raster

    :params:
        mode : str - describe the type of the geometry.
                default='OGR'
                alternative='SHAPELY'

    :return:
        geom : osgeo.ogr.geometry or shapely.geometry.polygon
            a geometry representing the raster extent
    """

    # Extract instance extent coordinates
    if ds != None:
        if type(ds) == str:
            ds=gdal.Open(ds)
        xMin, yMin, xMax, yMax=getDsCoordsExtent(ds)
    
    if coords != None:
        xMin, yMin, xMax, yMax=coords

    # Compute OGR geometry
    if mode.upper() == "OGR":

        # Create a ring
        ring=ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(xMin, yMax)
        ring.AddPoint(xMin, yMin)
        ring.AddPoint(xMax, yMin)
        ring.AddPoint(xMax, yMax)
        ring.AddPoint(xMin, yMax)

        # Assign this ring to a polygon
        polygon_env=ogr.Geometry(ogr.wkbPolygon)
        polygon_env.AddGeometry(ring)

    # Compute Shapely geometry
    elif mode.upper() == "SHAPELY":
        polygon_env=shapely.geometry.Polygon(
            [(xMin, yMax),
             (xMin, yMin),
             (xMax, yMin),
             (xMax, yMax),
             (xMin, yMax)])

    return polygon_env

def getBandsRowsColsFromDs(ds):
    """
    ds : osgeo.gdal.Dataset or str
        if str, convert into osgeo.gdal.Dataset with gdal.Open()

    send a tuple (numBands, numRows, numCols)
    """
    if type(ds) == str:
        ds=gdal.Open(ds)
    nBands=ds.RasterCount
    nRows=ds.RasterYSize
    nCols=ds.RasterXSize
    return nBands, nRows, nCols

def getBandsRowsColsFromArray(array):
    """
    array : numpy.ndarray - 2D or 3D

    send a tuple (numBands, numRows, numCols)
    """
    ar_dims=len(array.shape)
    if ar_dims == 2:
        nBands, nRows, nCols=(1,) + array.shape
    elif ar_dims == 3:
        nBands, nRows, nCols=array.shape
    else:
        print("Array have more than 3 dimensions")
        return None
    return nBands, nRows, nCols

def getDsArrayIndexesFromSpatialExtent(ds, BxMin, ByMin, BxMax, ByMax):
    """
    :descr:
        compute the matrixian coordinates of an area described by his bounds inside a dataset's array 

    :params:
        ds : osgeo.gdal.Dataset or str
            if str, convert into osgeo.gdal.Dataset with gdal.Open()

        BxMin : float - the xMin coordinates of the area
        ByMin : idem
        BxMax : idem
        ByMax : idem

    :returns:
        a tuple (row1, col1, row2, col2)

    """
    if type(ds) == str:
        ds=gdal.Open(ds)

    # Get initial image resolution
    xRes, yRes=getDsPixelSize(ds)

    # Get initial image extent
    A=getGeomExtent(ds=ds, mode="SHAPELY")
    AxMin=A.bounds[0]
    AyMax=A.bounds[3]

    # Get argument extent
    B=getGeomExtent(coords=(BxMin, ByMin, BxMax, ByMax), mode="SHAPELY")

    # Get intersection extent
    C=A.intersection(B)
    CxMin, CyMin, CxMax, CyMax=C.bounds

    # Transform geographic to matrixian coordinates
    # distance between the top edge of A and the top edge of C=CyMax - AyMax
    # to find the row of the input image integrating the C line
    # number_of_pixels_between_A_top_edge_and_C_top_edge=dist_between_A_top_edge_and_C_top_edge / yRes

    row1=int((CyMax - AyMax) / yRes)
    col1=int((CxMin - AxMin) / xRes)
    row2=int((CyMin - AyMax) / yRes)
    col2=int((CxMax - AxMin) / xRes)

    return row1, col1, row2, col2

def cropDsFromRaster(slave_ds, master_ds, verbose=False):
    """
    :descr:
        cut the image according to another raster extent

    :params:
        slave_ds : osgeo.gdal.Dataset or str
            if str, convert into osgeo.gdal.Dataset with gdal.Open()

        master_ds : osgeo.gdal.Dataset or str 
            describe the spatial extent on which the image 
            will be cropped. If it's a string, it must be
            a path to a raster file. 

    :return:
        a new osgeo.gdal.Dataset
    """

    if type(slave_ds) == str:
        slave_ds=gdal.Open(slave_ds)
    if type(master_ds) == str:
        master_ds=gdal.Open(master_ds)

    # Extract geometries
    slave_extent=getGeomExtent(slave_ds, mode="shapely")
    master_extent=getGeomExtent(master_ds, mode="shapely")

    # Intersect themselves
    inter_extent=slave_extent.intersection(master_extent)

    # Get data on the intersection area
    return cropDsFromVector(slave_ds, inter_extent, verbose=verbose)

def cropDsFromVector(ds, vector, polygon=0, verbose=False):
    """
    :descr:
        cut the image according to a vector geometry

    :params:
        ds : osgeo.gdal.Dataset or str
            if str, convert into osgeo.gdal.Dataset with gdal.Open()

        vector : str or shapely.geometry.polygon -
            describe the spatial extent on which the image 
            will be cropped. If it's a string, it must be
            a path to a shapefile. 

        polygon (facultative) : int
            if the vector argument is a path to shapefile,
            this argument specify the id of the polygon
            inside this shapefile to use

    :return:
        a new osgeo.gdal.Dataset
    """
    if type(ds) == str:
        ds=gdal.Open(ds)

    # If vector argument is a path to a shapefile,
    # here we extract only one polygon of this shapefile
    if type(vector) == str:
        layer=gpd.read_file(vector)
        vector=layer["geometry"][polygon]
    
    # Extract Coordinates extent
    xMin, yMin, xMax, yMax=vector.bounds

    # inform user
    if verbose: print(f"crop\n---\nxMin : {xMin}\nyMin : {yMin}\nxMax : {xMax}\nyMax : {yMax}\n---\n")

    # crop the dataset
    new_ds=gdal.Warp(
        destNameOrDestDS="",
        srcDSOrSrcDSTab=ds,
        format="VRT",
        outputBounds=(xMin, yMin, xMax, yMax),
        resampleAlg="near"
    )

    if getDsPixelSize(new_ds) != getDsPixelSize(ds):
        pxSize, pySize = getDsPixelSize(ds)
        orX, orY = getDsOriginPoint(new_ds)
        new_ds.SetGeoTransform((orX, pxSize, 0.0, orY, 0.0, pySize))

    return new_ds

def cropDsFromIndex(ds, index):
    """
        :descr:
            cut the image according to an matrixian area

        :params:
        ds : osgeo.gdal.Dataset or str
            if str, convert into osgeo.gdal.Dataset with gdal.Open()
        
        index : tuple -
            (firstColumn, firstRow, lastColumn, lastRow)
            describe the matrixian extent on which the image 
            will be cropped.

        :return:
            a new osgeo.gdal.Dataset
    """
    if type(ds) == str:
        ds=gdal.Open(ds)

    col1, row1, col2, row2=index
    ls_stack=[]
    num_band=0
    while ds.GetRasterBand(num_band+1) != None:
        num_band += 1
    if num_band > 1:
        for band in range(0,num_band):
            ar_band=ds.GetRasterBand(num_band)
            print(f"Read as array for band {band} from rt.cropDsFromIndex function")
            ar_custom=ar_band.ReadAsArray(col1, row1, col2-col1, row2-row1)
            ls_stack.append(ar_custom)
        im_array=np.array(ls_stack)
    else:
        print("Read as array from rt.cropDsFromIndex function")
        im_array=ds.GetRasterBand(1).ReadAsArray(col1, row1, col2-col1, row2-row1)

    # Get input dataset metadata
    xRes, yRes=getDsPixelSize(ds)
    old_orX, old_orY=getDsOriginPoint(ds)

    # Compute new origin point
    new_orX=old_orX + (col1 * xRes)
    new_orY=old_orY + (row1 * yRes)

    # Update the dataset's instance
    newDs=makeDs(
        "",
        im_array,
        new_orX,
        xRes,
        new_orY,
        yRes,
        ds.GetProjection(),
        "MEM")

    return newDs

def resizeDs(ds, xRes, yRes, resMethod="near"):
    """
    :descr:
        change the spatial size of the pixels, sometimes
        (wrongly) called "spatial resolution"

    :params:
        ds : osgeo.gdal.Dataset or str
            if str, convert into osgeo.gdal.Dataset with gdal.Open()
        xRes : float - the X pixel size
        yRes : float - the Y pixel size
        method : str - the resampling algorithm
            default : "near"
            alternatives :
                "bilinear"   
                "cubic"      
                "cubicspline"
                "lanczos"    
                "average"    
                "rms"        
                "max"        
                "min"        
                "med"        
                "q1"         
                "q3"         
                "sum"

    :return:
        a new osgeo.gdal.Dataset
    """

    if type(ds) == str:
        ds=gdal.Open(ds)

    ds_resized=gdal.Warp(
        destNameOrDestDS="",
        srcDSOrSrcDSTab=ds,
        format="VRT",
        xRes=xRes,
        yRes=yRes,
        resampleAlg=resMethod)
    
    return ds_resized

def reprojDs(ds, epsg):
    """
    :descr:
        change the Coordinates Reference System of a raster
        and reproject it into the new CRS

    :params:
        ds : osgeo.gdal.Dataset or str
            if str, convert into osgeo.gdal.Dataset with gdal.Open()
        epsg : 
            the epsg of the new CRS

    :return:
        a new osgeo.gdal.Dataset
    
    """
    if type(ds) == str:
        ds=gdal.Open(ds)

    if type(epsg) == int:
        srs=osr.SpatialReference()
        srs.ImportFromEPSG(epsg)
        crs=srs.ExportToWkt()
    else:
        crs=epsg
    return gdal.Warp("", ds, format="VRT", dstSRS=crs)

def chooseBandFromDs(ds, numBands):
    """
    :descr:
        send a osgeo.gdal.Dataset with only one band

    :params:
        ds : osgeo.gdal.Dataset or str
            if str, convert into osgeo.gdal.Dataset with gdal.Open()
        index : int
            the index of the band to  extract

    :return:
        a new osgeo.gdal.Dataset
    
    """

    if type(ds) == str:
        ds=gdal.Open(ds)

    if type(numBands) == int:
        numBands=[numBands]

    new_ds=gdal.Translate(
        destName="",
        srcDS=ds,
        format="VRT",
        bandList=numBands,
        noData=0
    )

    return new_ds

def shiftDsOriginPoint(ds, offsetX, offsetY):
    """
    :descr:
        offsetX is added to the origin X of the dataset.    
        offsetY is added to the origin Y of the dataset.

    :params:
        offsetX : float - 
            The distance to shift the image origin point
            (in general, north-west corner) along the X axe. 
            Exprimate in a coordinates system reference 
            space unit ( meters or degrees, according to 
            the SCR).

        offsetY : float -
            same as offsetX but for the Y axe.

    :return:
        a new osgeo.gdal.Dataset
    """
    if type(ds) == str:
        ds=gdal.Open(ds)

    # Get metadata
    xRes, yRes=getDsPixelSize(ds)
    orX, orY=getDsOriginPoint(ds)

    # shift
    ds.SetGeoTransform((orX + offsetX, xRes, 0.0, orY + offsetY, 0.0, yRes))

    return ds

def stackDs(ls_ds):
    """
        :descr:
            stack first band of each osgeo.gdal.Datasets contained in ls_ds

        :params:
            ls_geoim : list
                a list containing osgeo.gdal.Datasets objects or a list of raster file paths

        :return:
            a new osgeo.gdal.Dataset
    """

    # potential path conversion into osgeo.gdal.Dataset objects
    i=0
    for ds in ls_ds:
        if type(ds) == str:
            ls_ds[i]=gdal.Open(ds)
        i+=1

    # Extract the first dataset
    stack_ds=ls_ds[0]

    # Add to those bands the first band of each others dataset
    i=0
    for ds in ls_ds[1:]:
        i+=1
        print(f"{i}/{len(ls_ds)}")
        print("Read first band as array from rt.StackDs function")
        stack_ds.GetRasterBand(1).WriteArray(ds.ReadAsArray())
    return stack_ds

def stackGeoIms(geoims):
    """
    stack different geoims into one
    return : a new geoim
    """
    return geoims[0].stack(geoims[1:])

def mergeDs(ls_ds, proj=None):
    """
        :descr:
            merge each osgeo.gdal.Datasets contained in ls_ds into one big dataset

        :params:
            ls_geoim : list
                a list containing osgeo.gdal.Datasets objects or a list of raster file paths

        :return:
            a new osgeo.gdal.Dataset
    """

    # potential path conversion into osgeo.gdal.Dataset objects
    i=0
    for ds in ls_ds:
        if type(ds) == str:
            ls_ds[i]=gdal.Open(ds)
        i+=1

    if proj == None:
        proj=ls_ds[0].GetProjection()

    merged_ds=gdal.Warp(
        destNameOrDestDS="",
        srcDSOrSrcDSTab=ls_ds,
        format="MEM")

    return merged_ds

def mergeGeoIms(geoims):
    """
    merge different GeoIm instancess
    """
    return geoims[0].merge(geoims[1:])

def getDsEpsg(ds):
    """
    send the spatial coordinates reference system epsg id
    """
    if type(ds) == str:
        ds=gdal.Open(ds)

    sp_ref=osr.SpatialReference(wkt=ds.GetProjection())
    json_proj=json.loads(sp_ref.ExportToPROJJSON())
    epsg=json_proj["base_crs"]["id"]["code"]
    return int(epsg)

def getDsProjName(ds):
    """
    send the spatial coordinates reference system name
    """
    if type(ds) == str:
        ds=gdal.Open(ds)

    sp_ref=osr.SpatialReference(wkt=ds.GetProjection())
    json_proj=json.loads(sp_ref.ExportToPROJJSON())
    projName=json_proj["name"]
    return projName

def isGeoRaster(target):
    try :
        ds = gdal.Open(target)
    except RuntimeError:
        return False

def makeDs(
    path,
    array,
    orX,
    xRes,
    orY,
    yRes,
    crs,
    driverName="MEM"):

    npdtype_gdalconst={
        'int8'     : gdalconst.GDT_Byte,
        'int16'    : gdalconst.GDT_Int16,
        'int32'    : gdalconst.GDT_Int32,
        'int64'    : gdalconst.GDT_Int64,
        'uint8'    : gdalconst.GDT_Byte,
        'uint16'   : gdalconst.GDT_UInt16,
        'uint32'   : gdalconst.GDT_UInt32,
        'uint64'   : gdalconst.GDT_UInt64,
        'float16'  : gdalconst.GDT_Float32,
        'float32'  : gdalconst.GDT_Float32,
        'float64'  : gdalconst.GDT_Float64,
    }

    # Get ds encoding type from the array dtype
    try:
        ds_enc = npdtype_gdalconst[array.dtype.name]

    # This ds encoding type will not delete data,
    # but, the ds weight is generally higher.
    except KeyError:
        print("no gdalconst encoding found for this array.\nDefault assignation : gdalconst.GDT_Float32")
        ds_enc = gdalconst.GDT_Float32

    # Compute ds Size from the array
    nBands, nRows, nCols=getBandsRowsColsFromArray(array)

    # Dataset metadata
    newds_driver=gdal.GetDriverByName(driverName)
    newds=newds_driver.Create(path, nCols, nRows, nBands, ds_enc)

    # Dataset geodata setup
    newds.SetGeoTransform((orX, xRes, 0.0, orY, 0.0, yRes))
    newds.SetProjection(crs)

    # Load data into the dataset
    if nBands > 1:
        for band in range(1, nBands+1):
            newds.GetRasterBand(band).WriteArray(array[band-1])
    else:
        newds.GetRasterBand(1).WriteArray(array)

    return newds

def save(target, outpath, array = None, driverName="GTiff"):
    """
    :descr:
        save a Dataset or a GeoIm in a raster file

    :params:
        target : osgeo.gdal.Dataset or telenvi.raster_tools.GeoIm
            the object you want to save in a raster file
        
        outpath : str
            the path of the raster file you want to create

        array : numpy.ndarray
            if None, the raster file array will be the target array
            
        driverName : str, default : "GTiff"
            a string describing the raster file extension
    """

    # Get array to write
    if type(target) == GeoIm:
        target._updateDs()
        if type(array) != np.ndarray:
            array = target.array
        ds = target.ds

    else:
        ds = target
        if type(array) != np.ndarray:
            array = ds.ReadAsArray()

    # Get geographic informations
    xRes, yRes = getDsPixelSize(ds)
    orX, orY = getDsOriginPoint(ds)
    crs = ds.GetProjection()

    # Build a dataset store on disk
    outds=makeDs(
        outpath,
        array,
        orX,
        xRes,
        orY,
        yRes,
        crs,
        driverName)

    # Write on the disk
    outds.FlushCache()

    print(f"{os.path.basename(outpath)} ok")

# def duration(func):
#     """
#     dev func - a decorator to compute the execution time of a function
#     """
#     import time
#     def wrapper(*args, **kwargs):
#         start=time.time()
#         func(*args, **kwargs)
#         dur=time.time() - start
#         print(dur)
#     return wrapper
# %%
