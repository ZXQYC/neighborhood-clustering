import numpy as np

from pykml import parser

import polygons

f_footprints = open('champaign-Building_Footprints.kml', 'rt')
s_footprints = f_footprints.read()
b_footprints = bytes(s_footprints, 'utf-8')

root = parser.fromstring(b_footprints)

placemarks = root.Document.Folder.Placemark

def extract():
    polys = []
    for pm in placemarks:
        try:
            txt = pm.Polygon.outerBoundaryIs.LinearRing.coordinates.text
            pts = np.array([tuple(map(float, p.split(','))) for p in txt.split(' ')])
            segs = np.stack((pts[:-1],pts[1:]),1)
            polys.append(polygons.MultiPolygon(segs))
        except AttributeError:
            continue
    return polys
