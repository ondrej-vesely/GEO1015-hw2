#-- my_code_hw02.py
# -- Assignment 02 GEO1015.2020
# -- Ondrej Vesely
#-- 5162130
# -- Guilherme Spinoza Andreo
#-- 5383994

import numpy as np
import rasterio
from rasterio import features

def circle_exterior_mask(h, w, center, radius):
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    mask = dist_from_center > radius
    return mask

def bresenham_line_mask(h, w, x1, y1, x2, y2):
    l = [({"type": "LineString", "coordinates": [(x1, y1), (x2, y2)]}, 1)]
    mask = features.rasterize(l, out_shape=(h, w), all_touched=True)
    return mask

def bresenham_circle_coords(x0, y0, radius):
    coords = set()
    radius = round(radius)
    f = 1 - radius
    ddf_x = 1
    ddf_y = -2 * radius
    x = 0
    y = radius
    coords.add((x0, y0 + radius))
    coords.add((x0, y0 - radius))
    coords.add((x0 + radius, y0))
    coords.add((x0 - radius, y0))
    while x < y:
        if f >= 0:
            y -= 1
            ddf_y += 2
            f += ddf_y
        x += 1
        ddf_x += 2
        f += ddf_x
        coords.add((x0 + x, y0 + y))
        coords.add((x0 - x, y0 + y))
        coords.add((x0 + x, y0 - y))
        coords.add((x0 - x, y0 - y))
        coords.add((x0 + y, y0 + x))
        coords.add((x0 - y, y0 + x))
        coords.add((x0 + y, y0 - x))
        coords.add((x0 - y, y0 - x))
    return coords


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
    # raster of the input
    terrain = d.read(1)
    # raster of the output
    output = np.zeros(d.shape, dtype=np.int8)
    # get dimensions in raster space
    pixel_size = d.transform[0]
    pixel_radius = maxdistance/pixel_size
    
    for v in viewpoints:
        # get viewpoint coords and height
        vrow, vcol = d.index(v[0], v[1])
        vheight = terrain[vrow, vcol] + v[2]

        # get points on circle circumference
        # and draw a bresenham lines towards them
        x1, y1 = vcol, vrow
        for x2, y2 in bresenham_circle_coords(x1, y1, pixel_radius+1):
            line = bresenham_line_mask(*d.shape, x1, y1, x2, y2)

            # get each lines points
            pts = np.argwhere(line)
            # and their projected distance 
            vect = np.array((y2-y1, x2-x1))
            vect_norm = vect / np.linalg.norm(vect)
            dist = np.dot(pts - (y1, x1), vect_norm)
            # sort them based on distance and remove starting point
            order = dist.argsort()[1:]
            pts, dist = pts[order], dist[order]
            # calculate each points tangent
            tang =  (terrain[pts.T[0], pts.T[1]] - vheight) / dist           
            # apply incremental tangent line of sight algo
            max_t = float('-inf')
            for i, t in enumerate(tang):
                if t >= max_t:
                    output[pts[i][0], pts[i][1]] = 1
                    max_t = t
        
    # set viewpoint pixels to value 2
    for v in viewpoints:
        vrow, vcol = d.index(v[0], v[1])
        output[vrow, vcol] = 2
    
    # set pixels outside of radius to value 3
    exterior_mask = True
    for v in viewpoints:
        vrow, vcol = d.index(v[0], v[1])
        mask = circle_exterior_mask(d.shape[0], d.shape[1],
                                    (vcol, vrow), pixel_radius)
        exterior_mask = np.logical_and(mask, exterior_mask)
    np.putmask(output, exterior_mask, 3)
 
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