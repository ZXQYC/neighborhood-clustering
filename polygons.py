
import json

import numpy as np

import progress

def seg_to_tuple(seg):
    return ((seg[0,0],seg[0,1]),(seg[1,0],seg[1,1]))

def signedArea(poly):
    poly = poly - poly.mean(0)
    matrices = np.stack((poly[:-1],poly[1:]),1)
    dets = np.linalg.det(matrices)
    return np.sum(dets)/2

def signedAreaWithSegs(segs):
    dets = np.linalg.det(segs)
    return np.sum(dets)/2

def segLength(seg):
    return np.linalg.norm(seg[0,:]-seg[1,:])

def segLengthSum(segs):
    return np.linalg.norm(segs[:,0,:]-segs[:,1,:],axis=1).sum()

class MultiPolygon:
    def __init__(self, segs, merge=True):
        # segs: bag of directed segments - Nx2x2
        self.segs = segs
        if merge: self.removeOpposingSegs()
        self.regions = broken_to_regions(self.segs)
        self.polys = [np.concatenate((reg[0:1,0,:],reg[:,1,:]),0) for reg in self.regions]
        self.polys.sort(key=signedArea,reverse=True)
        self.signedAreas = [signedArea(p) for p in self.polys]
        self.totalArea = sum(self.signedAreas)
    def removeOpposingSegs(self):
        N,_,_ = self.segs.shape
        seg_set = set()
        keep = np.ones(N, dtype=bool)
        for i in range(N):
            seg_set.add(seg_to_tuple(self.segs[i,:,:]))
        for i in range(N):
            s_rev = np.flip(self.segs[i,:,:],0)
            keep[i] = seg_to_tuple(s_rev) not in seg_set
        self.segs = self.segs[keep,:,:]
    def polySplit(self):
        """returns a list of MultiPolygons, each with only 1 polygon"""
        return [MultiPolygon(reg) for reg in self.regions]
    def perimeter(self):
        try:
            return self.perim
        except:
            perims = [segLengthSum(p) for p in self.regions]
            self.perim = sum(perims)
            return self.perim
    def centroid(self):
        ans = np.zeros(2)
        for poly_i,poly in enumerate(self.polys):
            polymean = poly.mean(0)
            pts = poly - polymean
            n = pts.shape[0]-1
            area2 = 0
            x = 0
            y = 0
            for i in range(n):
                shoelace = pts[i][0]*pts[i+1][1] - pts[i][1]*pts[i+1][0]
                area2 += shoelace
                x += (pts[i][0]+pts[i+1][0]) * shoelace
                y += (pts[i][1]+pts[i+1][1]) * shoelace
            area6 = area2*3
            x = x/area6
            y = y/area6
            cent = np.array([x,y])+polymean
            ans += cent * self.signedAreas[poly_i] / self.totalArea
        return ans
    @staticmethod
    def merge(poly0, poly1):
        return MultiPolygon(np.concatenate((poly0.segs,poly1.segs),0))
    @staticmethod
    def shared_perimeters(poly0, poly1):
        slist = set()
        for seg in poly0.segs:
            slist.add(seg_to_tuple(seg))
        ans = 0
        for seg in poly1.segs:
            if seg_to_tuple(seg) in slist or seg_to_tuple(np.flip(seg,0)) in slist:
                ans += segLength(seg)
        return ans

class PolyList:
    @staticmethod
    def to_vertex_lists(polylist):
        return [[p.tolist() for p in pp.polys] for pp in polylist]
    @staticmethod
    def from_vertex_lists(vlists):
        ans = []
        for vl in vlists:
            segs = np.concatenate([np.stack((vs[:-1],vs[1:]),1) for vs in vl])
            ans.append(MultiPolygon(segs,merge=False))
        return ans
    @staticmethod
    def export_json(polylist, fp):
        json.dump(PolyList.to_vertex_lists(polylist), fp, indent=2)
    @staticmethod
    def import_json(fp):
        res = json.load(fp)
        return PolyList.from_vertex_lists(res)

# algo for creating regions (with adjacency graph) from a collection of segments

def segment_break(segs, update_every=None):
    # segs: N x 2 x 2
    N,_,_ = segs.shape
    prog = progress.Progress(N-1,update_every)
    breakvals = [[(0,segs[i,0,:]), (1,segs[i,1,:])] for i in range(N)]
    for i in range(1,N):
        prog.update()
        segsI = np.tile(segs[i:i+1,:,:],(i,1,1))
        segsJ = segs[:i,:,:]
        main_m = np.stack((segsI[:,0,:],segsJ[:,0,:]),1)
        denom_m= np.stack((segsI[:,1,:],segsJ[:,1,:]),1)
        denom = np.linalg.det(main_m-denom_m)
        num_t = np.linalg.det(main_m-segsJ)
        num_u = np.linalg.det(main_m-np.flip(segsI,1))
        val_t = num_t / denom
        val_u = num_u / denom
        coincide_inorder = np.any(np.all(segsI==segsJ,2),1)
        coincide_outorder= np.any(np.all(segsI==np.flip(segsJ,1),2),1)
        coincide_any = coincide_inorder | coincide_outorder
        has_intersect = (0 < val_t) & (val_t < 1) & (0 < val_u) & (val_u < 1) & (1-coincide_any)
        intersect_list = np.where(has_intersect)[0]
        for j in intersect_list:
            bpoint = segs[i,0,:]*(1-val_t[j]) + segs[i,1,:]*val_t[j]
            breakvals[i].append((val_t[j], bpoint))
            breakvals[j].append((val_u[j], bpoint))
    # generate new broken segments
    newsegs = []
    for i,bvals in enumerate(breakvals):
        bvals.sort()
        bpoints = np.stack([bv[1] for bv in bvals])
        bpoints = np.expand_dims(bpoints,1)
        bsegs = np.stack((bpoints[:-1,0,:], bpoints[1:,0,:]), 1)
        newsegs.append(bsegs)
    ans = np.concatenate(newsegs, 0)
    return ans

class PointVertex:
    def __init__(self, loc):
        # loc: np array of size 2
        self.loc = loc
        self.adjacent = []
    def add_adjacent(self, adj):
        self.adjacent.append(adj)
    def sort_adjacent(self):
        self.adjacent.sort(key=self.adj_key)
    def adj_key(self, adj):
        diff = adj-self.loc
        return np.arctan2(diff[1],diff[0])
    def next_adj(self, adj):
        idx = -1
        for i,v in enumerate(self.adjacent):
            if np.all(v==adj):
                idx = i
                break
        #idx = self.adjacent.index(adj)
        idx = (idx-1) % len(self.adjacent)
        return self.adjacent[idx]

def double_reverse_segs(segs):
    return np.concatenate((segs, np.flip(segs, 1)), 0)

def broken_to_regions(segs):
    # segs: N x 2 x 2
    N,_,_ = segs.shape
    # step 1: create the segment graph and add all segments to the destruction set
    graph = {}
    
    def add_to_graph(v,w):
        tv = tuple(v)
        if tv not in graph:
            graph[tv] = PointVertex(v)
        graph[tv].add_adjacent(w)
    for i in range(N):
        add_to_graph(segs[i,0,:],segs[i,1,:])
        #add_to_graph(segs[i,1,:],segs[i,0,:])
    for key in graph:
        graph[key].sort_adjacent()
    # step 2 : generate regions
    regions = []
    used_segs = set()
    def visited(s):
        ts = seg_to_tuple(s)
        if ts in used_segs:
            return True
        else:
            used_segs.add(ts)
            return False
    for si in range(N):
        if visited(segs[si,:,:]):
            continue
        regsegs = [segs[si,:,:]]
        while True:
            nextvert = graph[tuple(regsegs[-1][1,:])].next_adj(regsegs[-1][0,:])
            
            nextseg = np.stack((regsegs[-1][1,:],nextvert))
            if not visited(nextseg):
                regsegs.append(nextseg)
            else:
                break
        reg = np.stack(regsegs)
        regions.append(reg)
    return regions

def full_region_finder_pipeline(segs):
    print('Breaking segments...')
    broken = segment_break(segs, update_every=2000)
    doubled = double_reverse_segs(broken)
    print('Creating polygons...')
    poly = MultiPolygon(doubled, merge=False)
    polys = poly.polySplit()
    ans = [p for p in polys if p.totalArea > 0]
    print('Done!')
    return ans

def set_toggle(s,x):
    if x in s:
        s.remove(x)
    else:
        s.add(x)

def put_points_into_polys(points,polylist,updateEvery=None):
    # points is a N x 2 numpy array
    # polylist is a list of MultiPolygon objects
    # returns: list of integers with size N
    segsort = [] # (endpoint_x, poly_i, seg_i)
    for poly_i, poly in enumerate(polylist):
        nsegs = poly.segs.shape[0]
        for seg_i in range(nsegs):
            for end_i in range(2):
                segsort.append((poly.segs[seg_i,end_i,0],poly_i,seg_i))
    segsort.sort()
    pointsort = [] # (x, index)
    for pt_i in range(points.shape[0]):
        pointsort.append((points[pt_i,0], pt_i))
    pointsort.sort()
    
    ans = [-1]*points.shape[0]
    
    seg_set = set() # entries are (poly_i, seg_i)
    segsort_i = 0
    prog = progress.Progress(len(pointsort),updateEvery)
    for pt_x,pt_i in pointsort:
        prog.update()
        pt = points[pt_i,:]
        while segsort_i<len(segsort) and segsort[segsort_i][0] <= pt_x:
            set_toggle(seg_set, (segsort[segsort_i][1], segsort[segsort_i][2]))
            segsort_i += 1
        which_poly = set() # entries are poly_i
        for poly_i,seg_i in seg_set:
            seg = polylist[poly_i].segs[seg_i,:,:]
            # check for intersection of pt--(x,inf) and seg
            # just need to check intersection is above the point itself
            y_int = (seg[0,1]*(seg[1,0]-pt_x)+seg[1,1]*(pt_x-seg[0,0])) / (seg[1,0]-seg[0,0])
            if y_int > pt[1]:
                set_toggle(which_poly,poly_i)
        if len(which_poly)>0:
            ans[pt_i] = min(which_poly, key=lambda poly_i: np.linalg.norm(polylist[poly_i].centroid()-pt))
    return ans























