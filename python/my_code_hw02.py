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

def distance_matrix(h, w, center):
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    return dist_from_center

def circle_exterior_mask(h, w, center, radius):
    dist_from_center = distance_matrix(h, w, center)
    mask = dist_from_center > radius
    return mask

def circle_outline_mask(h, w, center, radius, thickness=math.sqrt(2)):
    dist_from_center = distance_matrix(h, w, center)
    mask = np.logical_and( (radius-thickness) < dist_from_center, 
                            dist_from_center <= radius )
    return mask

def bresenham_line_mask(h, w, x1, y1, x2, y2):
    l = {"type":"LineString", "coordinates":[(x1, y1), (x2, y2)]}
    mask = features.rasterize([(l, 1)], out_shape= (h, w))
    mask[x2, y2] = 1
    return mask

def bresenham_circle_coords(x0, y0, radius):
    coords = set()
    f = 1 - radius
    ddf_x = 1
    ddf_y = -2 * radius
    x = 0
    y = radius
    coords.add(x0, y0 + radius)
    coords.add(x0, y0 - radius)
    coords.add(x0 + radius, y0)
    coords.add(x0 - radius, y0)
 
    while x < y:
        if f >= 0: 
            y -= 1
            ddf_y += 2
            f += ddf_y
        x += 1
        ddf_x += 2
        f += ddf_x    
        coords.add(x0 + x, y0 + y)
        coords.add(x0 - x, y0 + y)
        coords.add(x0 + x, y0 - y)
        coords.add(x0 - x, y0 - y)
        coords.add(x0 + y, y0 + x)
        coords.add(x0 - y, y0 + x)
        coords.add(x0 + y, y0 - x)
        coords.add(x0 - y, y0 - x)

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


    for v in viewpoints:
        # get raster coords and height
        vrow, vcol = d.index(v[0], v[1])
        vheight = terrain[vrow, vcol] + v[2]

        # get points on circle
        circle = circle_outline_mask  (d.shape[0], d.shape[1], 
                                      (vcol, vrow), maxdistance/pixel_size)
        
        crow, ccol = np.where(circle)
        cpoints = zip(ccol, crow)
        
        # try line drawing
        y1, x1 = vcol, vcol
        for x2, y2 in cpoints:
            line = bresenham_line_mask(*d.shape, x1, y1, x2, y2)
            np.putmask(output, line, 4)





   
   
   
    # set pixels outside of radius to value 5
    radius_mask = False
    for v in viewpoints:
        vrow, vcol = d.index(v[0], v[1])
        mask = circle_outline_mask  (d.shape[0], d.shape[1], 
                                    (vcol, vrow), maxdistance/pixel_size)
        radius_mask = np.logical_or(mask, radius_mask)      
    np.putmask(output, radius_mask, 5)


    # set pixels outside of radius to value 3
    exterior_mask = True
    for v in viewpoints:
        vrow, vcol = d.index(v[0], v[1])
        mask = circle_exterior_mask (d.shape[0], d.shape[1], 
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



