
import numpy as np
import osmium

# any 'highways' with these tags will be ignored
# (see https://wiki.openstreetmap.org/wiki/Key:highway for the list of possible tags)
ignored_road_tags = [
    'pedestrian',
    'track', 'raceway',
    'footway',
    'bridleway',
    'steps',
    'corridor',
    'path',
    'cycleway',
    'service'
]

class RoadHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.num_roads = 0
        self.segs = []
        self.alltags = {}

    def way(self, n):
        if 'highway' in n.tags and n.tags['highway'] not in ignored_road_tags:
            self.handle_road(n)
        if 'waterway' in n.tags or 'natural' in n.tags and n.tags['natural'] == 'water':
            self.handle_water(n)
    
    def handle_road(self, n):
        htag = self.gen_tag_str(n, ['highway'])
        self.update_tag(htag)
        self.handle_way(n)
    
    def handle_water(self, n):
        htag = self.gen_tag_str(n, ['waterway', 'natural', 'water'])
        self.update_tag(htag)
        self.handle_way(n)
    
    def update_tag(self, htag):
        self.alltags[htag] = self.alltags.get(htag,0)+1
        self.num_roads += 1

    def gen_tag_str(self, n, tags):
        x = [t+'='+n.tags.get(t,'') for t in tags]
        return ','.join(x)
    
    def handle_way(self, n):
        num = len(n.nodes)
        for i in range(num-1):
            dat = np.array([[n.nodes[i].lon,n.nodes[i].lat],[n.nodes[i+1].lon,n.nodes[i+1].lat]])
            self.segs.append(dat)

def get_road_segs(osm_file):
    """
    Input: a string that is a path to a .osm file.
    Output: A numpy array 'arr' of shape (N,2,2), when there are a total of N road segments. 
    Segment i starts at (longitude,latitude) of (arr[i,0,0],arr[i,0,1]) and ends at (arr[i,1,0],arr[i,1,1]). 
    """
    osm_streets = RoadHandler()
    osm_streets.apply_file(osm_file, locations=True)
    print("Roads/Water found: %d" % osm_streets.num_roads)
    print("Total segments:", len(osm_streets.segs))
    print(osm_streets.alltags)
    return np.stack(osm_streets.segs)
