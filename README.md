# Hongyi's code for Community Mapping (Spring 2021)
LINK TO REPO

This repo contains all of the code I used for creating clustering algorithms for the Community Mapping project over the Spring 2021 semester.

This does NOT contain code for the website I made for evaluating clusters. See https://github.com/ZXQYC/neighborhood-evaluation for that code. 

Here's a list of things in this repo:

## Jupyter Notebooks
 - `neighborhoods_2.ipynb` contains my current AGNES-based clustering algorithm. See the comments in this notebook to see how it works.
 - `neighborhoods_old.ipynb` contains my old clustering algorithm. The code in it is not very well documented, partially because I have no idea what I was doing back then. I'm keeping this file in the git repo for legacy purposes, but it's not very useful. 
 - `road_region_creator.ipynb` contains code for generating `road_regions.js` and `road_regions.json`, which is a partition of Champaign into *natural regions* (aka a region bounded by natural boundaries). These 2 generated files are necessary for running `neighborhoods_2.ipynb`.
 - `tax_crawler.ipynb` contains code for crawling PropertyShark for tax data. This generates all of the files in the `PropertyShark` folder. This uses `tax_crawler.py`, which contains the main logic for crawling PropertyShark.

## Python Code Files

### `FloatColorMapper.py`
A module that generates heatmaps that can be displayed in `map.html`.
 - `FloatColorMapper.genJSON(points, floatScale)` gives an object which can be converted into a JSON string. 
### `footprint_kml_poly_extractor.py`
A simple module that reads `champaign-Building_Footprints.kml` and outputs a list of `polygons.MultiPolygon` objects containing all of the building footprints.
 - `footprint_kml_poly_extractor.extract()` gives the list of MultiPolygon objects.
### `jsdump.py`
A module for creating `.js` files that contain definitions for certain variables. Example usage:
```
import jsdump
dumper = jsdump.Dumper('things.js')
dumper.dump('oneplusone', 2)
dumper.dump('small_list', [5,6])
dumper.done()
```
This will create a file named `things.js` containing the following:
```
const oneplusone = 2;
const small_list = [
  5,
  6
];
```
### `latlon.py`
A module for calculating and approximating distances between geospatial points, given their latitude and longitude.
 - `exact_dist(pt0, pt1)` gives the exact distance (in km) between points `pt0` and `pt1`. Each point should be a list (or tuple, or numpy array, or whatever) of the form `[longitude, latitude]`.
 - `set_center(cx, cy)` will set variables that are used by `approx_dist(pt0, pt1)`. `approx_dist` will be most accurate when used on points close to `[cx,cy]`.
 - `approx_dist(pt0, pt1)` works similarly to `exact_dist(pt0, pt1)`, but is only accurate for points close to the `[cx,cy]` set by `set_center(cx,cy)`. This runs much faster than `exact_dist`, so use this when speed is an issue. You can do bulk calculation by passing in an *array* of points to either `pt0` or `pt1`, in which case the answer will be an array rather than a single number.
### `osm_roads.py`
A module that can read `.osm` files and gives a bunch of segments, each representing a natural boundary.
 - `osm_roads.get_road_segs(osm_file)` reads the `.osm` file with name `osm_file`, and outputs all the relevant natural boundaries found. The output is a 3d numpy array `arr` with shape `(N,2,2)`, where there are `N` natural boundary segments. Segment i starts at (longitude,latitude) of `(arr[i,0,0],arr[i,0,1])` and ends at `(arr[i,1,0],arr[i,1,1])`.

Note that the name of this file, and the variables/comments inside of it, are slightly outdated. Previously, this file only used roads as natural boundaries, but has since been expanded to include waterways as well. 

### `polygongraph.py`
A module that contains the main AGNES-based algorithm used in `neighborhoods_2.ipynb`. 
 - `PolygonGraph`: A class representing a graph where polygons are nodes, and two polygons are connected iff they share a side. This contains several functions for performing AGNES on the nodes.

### `polygons.py`
A big module for doing computational geometry used in `neighborhoods_2.ipynb`. 
 - `MultiPolygon`: A class representing a *MultiPolygon*, aka a set of polygons.
Honestly, this module is really inefficient, and I would recommend using some pre-existing computational geometry module instead. However, a significant portion of the code in this git repo relies on this module.

### `progess.py`
A simple module for keeping track of progress of a slow-running task.

### `tax_crawler.py`
A module for crawling PropertyShark for property data.
 - `get_all_tax_info(addrs)`: Gets a list of tax info for every address in `addrs`. `addrs` should be a list of strings, with each string being an address. 


## Map Frontend Code Files
These are the files for generating the map at `map.html`.
### `map.html`
The main page. Open this in a browser to view the map.
### `map.js`
This file contains most of the actual logic for the map. You can adjust the constants at the start of the file, to change what is displayed.

## Raw Data Files

### Downloaded from Champaign GIS
(Data files that were directly downloaded from websites)
 - `champaign-addresses.csv` was downloaded from `https://gis-cityofchampaign.opendata.arcgis.com/datasets/address-points` and contains address points in Champaign.
 - `champaign-Apartments.csv` was downloaded from `https://gis-cityofchampaign.opendata.arcgis.com/datasets/apartments` and contains apartments in Champaign.
 - `champaign-Building_Footprints.kml` was downloaded from `https://gis-cityofchampaign.opendata.arcgis.com/datasets/building-footprints` and contains building footprints in Champaign.

### Other Data Files
 - `map.osm` contains data for a region of Champaign, downloaded from OpenStreetMap. 
 - `PropertyShark/` contains property data found by crawling the PropertyShark website. `PropertyShark/tax_all.csv` contains all of the information. You can also view smaller chunks of it in the `tax0.csv`, `tax1.csv`, etc etc files. These files were generated by `tax_crawler.ipynb`.

## Generated Files

### Generated by `neighborhoods_2.ipynb`
 - `addresses_with_tax.csv` is a csv file that is the result of merging `PropertyShark/tax_all.csv` with the residential addresses in `champaign-addresses.csv`. 
 - `agnes_result.json` contains a representation for a set of regions generated by my AGNES-based clustering algorithm. Each region has a name, a set of addresses, and a set of adjacent regions. This file can be used by my website to generate pairs of houses for humans to evaluate. (Put it in the base directory in the git repo for the website, and rename it to `cluster_result.json`.)
 - `agnes_road_regions.js` contains another representation for a set of regions generated by my AGNES-based clustering algorithm. It contains the vertices of the polygonal regions created by my algorithm. It is used by `map.html` to display clusters.
 - `feature_color_map.js` contains information for displaying a heatmap for the 8 features used by my AGNES-based clustering algorithm. It is used by `map.html` to display the heatmap.

### Generated by `road_region_creator.ipynb`
 - `road_regions.json`: Contains a representation for a list of MultiPolygons, each representing a *natural region* of Champaign.
 - `road_regions.js`: Same as `road_regions.json`, but as a `js` file instead.

### Generated by `neighborhoods_old.ipynb` (OUTDATED)
 - `convex_hulls.js` contains information that `map.html` uses to display clusters formed by my old clustering algorithm.
