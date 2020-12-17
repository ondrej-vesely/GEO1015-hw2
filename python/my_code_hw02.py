#-- my_code_hw02.py
#-- Assignment 02 GEO1015.2020
#-- Ondrej Vesely 
#-- 5162130
#-- Guilherme Spinoza Andreo 
#-- 5383994 

import sys
import math
import numpy as np
import rasterio
from rasterio import features

def create_circle_exterior_mask(h, w, center, radius):
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    mask = dist_from_center > radius
    return mask

def create_circle_outline_mask(h, w, center, radius, thickness=math.sqrt(2)):
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    mask = np.logical_and( (radius-thickness) < dist_from_center, 
                            dist_from_center <= radius )
    return mask

def bresenham_line(h, w, x1, y1, x2, y2):
    l = {"type":"LineString", "coordinates":[(x1, y1), (x2, y2)]}
    mask = features.rasterize([(l, 1)], out_shape= (h, w))
    mask[x2, y2] = 1
    return mask



def output_viewshed(d, viewpoints, maxdistance, output_file):
    """
    !!! TO BE COMPLETED !!!
     
    Function that writes the output raster
     
    Input:
        d:            the input datasets (rasterio format)  
        viewpoints:   a list of the viewpoints (x, y, height)
        maxdistance:  max distance one can see
        output_file:  path of the file to write as output
        
    Output:
        none (but output GeoTIFF file written to 'output-file')
    """  
    
    # [this code can and should be removed/modified/reutilised]
    # [it's just there to help you]

    # numpy of the input
    terrain  = d.read(1)
    # numpy of the output
    output = np.zeros(d.shape, dtype=np.int8)

    # pixel size
    pixel_size = d.transform[0]


   
   
   
   
    # set pixels outside of radius to value 5
    radius_mask = False
    for v in viewpoints:
        vrow, vcol = d.index(v[0], v[1])
        mask = create_circle_outline_mask(d.shape[0], d.shape[1], 
                                          (vcol, vrow), maxdistance/pixel_size)
        radius_mask = np.logical_or(mask, radius_mask)      
    np.putmask(output, radius_mask, 5)


    # set pixels outside of radius to value 3
    exterior_mask = True
    for v in viewpoints:
        vrow, vcol = d.index(v[0], v[1])
        mask = create_circle_exterior_mask(d.shape[0], d.shape[1], 
                                          (vcol, vrow), maxdistance/pixel_size)
        exterior_mask = np.logical_and(mask, exterior_mask)      
    np.putmask(output, exterior_mask, 3)

    # set viewpoint pixels to value 2
    for v in viewpoints:  
        vrow, vcol = d.index(v[0], v[1])
        output[vrow, vcol] = 2

    # finally write numpy raster array as tif
    with rasterio.open(output_file, 'w', 
                       driver='GTiff', 
                       height=terrain.shape[0],
                       width=terrain.shape[1], 
                       count=1, 
                       dtype=rasterio.uint8,
                       crs=d.crs, 
                       transform=d.transform) as dst:
        dst.write(output.astype(rasterio.uint8), 1)

    print("Viewshed file written to '%s'" % output_file)



def Bresenham_with_rasterio():
    # d = rasterio dataset as above
    a = (10, 10)
    b = (100, 50)
    #-- create in-memory a simple GeoJSON LineString
    v = {}
    v["type"] = "LineString"
    v["coordinates"] = []
    v["coordinates"].append(d.xy(a[0], a[1]))
    v["coordinates"].append(d.xy(b[0], b[1]))
    shapes = [(v, 1)]
    re = features.rasterize(shapes, 
                            out_shape=d.shape, 
                            all_touched=True,
                            transform=d.transform)
    # re is a numpy with d.shape where the line is rasterised (values != 0)



