
import heapq

import numpy as np

import progress
import polygons

class PolygonNode:
    def __init__(self, poly, data):
        # poly is a polygon, data is a list of datapoints of whatever
        self.poly = poly
        self.data = data
    @staticmethod
    def merge(node0, node1):
        return PolygonNode(polygons.MultiPolygon.merge(node0.poly,node1.poly), node0.data+node1.data)

def list_union(a,b):
    return list(set(a+b))
    
class PolygonGraph:
    def __init__(self, polys, points, data):
        # first match polys with houses
        # discard all houses not in a poly, and all polys with no houses
        point_places = polygons.put_points_into_polys(points, polys)
        pointsIn = [[] for p in polys]
        for i in range(len(data)):
            if point_places[i] == -1:
                continue
            pointsIn[point_places[i]].append(data[i])
        self.nodes = [PolygonNode(poly, plist) for (poly,plist) in zip(polys,pointsIn) if len(plist)>0]
        self.N = len(self.nodes)
        # now create an adjacency list
        self.edges = [[] for i in range(self.N)]
        emap = {}
        for i in range(self.N):
            segs = self.nodes[i].poly.segs
            for seg in segs:
                s_tup = polygons.seg_to_tuple(seg)
                sr_tup = polygons.seg_to_tuple(np.flip(seg,0))
                emap[s_tup] = i
                if sr_tup in emap:
                    j = emap[sr_tup]
                    if j==i or j in self.edges[i]:
                        continue
                    self.edges[i].append(j)
                    self.edges[j].append(i)
    def agnes_cluster(self, dist_func, num_clusters=1):
        M = self.N*2-1
        
        dist_heap = [] # elements: (dist, node_i, node_j), where node_i<node_j
        
        for i in range(self.N):
            for j in self.edges[i]:
                if i>j: continue
                dist_heap.append((dist_func(self.nodes[i],self.nodes[j]), i, j))
        heapq.heapify(dist_heap)
        num_left = self.N
        active = [True]*M
        destroyed = [-1]*M
        mergeds = [None]*M
        merge_dists = [None]*M
        edges = [ecopy.copy() for ecopy in self.edges]
        nodes = [ncopy for ncopy in self.nodes]
        while len(dist_heap) and num_left > num_clusters:
            d,i,j = heapq.heappop(dist_heap)
            if not (active[i] and active[j]): continue
            active[i] = False
            active[j] = False
            
            k = len(nodes)
            destroyed[i] = k
            destroyed[j] = k
            mergeds[k] = (i,j)
            merge_dists[k] = d
            
            nodes.append(PolygonNode.merge(nodes[i],nodes[j]))
            newedges = list(set(edges[i]+edges[j]))
            newedges = [e for e in newedges if active[e]]
            edges.append(newedges)
            
            for e in edges[k]:
                edges[e].append(k)
                heapq.heappush(dist_heap, (dist_func(nodes[e],nodes[k]), e, k))
            num_left -= 1
            
        self.agnes_nodes = nodes
        self.agnes_edges = edges
        self.agnes_min_clusters = num_left
        self.agnes_final_M = self.N*2-num_left
        self.agnes_mergeds = mergeds
        self.agnes_merge_dists = merge_dists
        self.agnes_destroyed_time = destroyed
        self.agnes_dist_func = dist_func
        # self.agnes_active = active (DO NOT USE THIS)
    def agnes_set_num_clusters(self, num_clusters=None, max_dist=None):
        if num_clusters is None:
            last_delete = self.N
            while last_delete < self.agnes_final_M and self.agnes_merge_dists[last_delete]<=max_dist:
                last_delete += 1
            num_clusters = 2*self.N-last_delete
        if num_clusters < self.agnes_min_clusters:
            raise Exception('not enough clusters')
        num_deletes = self.N-num_clusters
        max_idx = self.N+num_deletes
        active = [True]*max_idx
        for i,j in self.agnes_mergeds[self.N:max_idx]:
            active[i] = False
            active[j] = False
        self.agnes_active = active
        self.agnes_max_idx = max_idx
        self.agnes_n_clusters = num_clusters
    def agnes_get_result_polygons(self):
        ans = [self.agnes_nodes[i].poly for i in range(self.agnes_max_idx) if self.agnes_active[i]]
        return ans
    def agnes_get_labelled_centroids(self):
        ans = []
        for i in range(self.agnes_max_idx):
            if self.agnes_active[i]:
                ans.append({
                    'point': self.agnes_nodes[i].poly.centroid().tolist(),
                    'label': str(i)
                })
        return ans
    def agnes_get_stats(self):
        return "Base polygons (%d): 0-%d\nMerged polygons (%d): %d-%d\nActive polygons (%d)" % (
            self.N,
            self.N-1,
            self.agnes_max_idx-self.N,
            self.N,
            self.agnes_max_idx-1,
            self.agnes_n_clusters
        )
    def agnes_explain(self, cid):
        ans = ""
        if cid >= self.agnes_max_idx:
            ans += "DOES NOT EXIST (valid id range is 0-%d)\n" % (cid, self.agnes_max_idx-1)
        else:
            if self.agnes_active[cid]:
                ans += "%d -> FINAL\n" % cid
            else:
                destr = self.agnes_destroyed_time[cid]
                ans += "(%d,%d) -> %d\n" % (cid, sum(self.agnes_mergeds[destr])-cid, destr)
            if cid >= self.N:
                ans += "%d <- (%d,%d)\n" % (cid, *self.agnes_mergeds[cid])
            else:
                ans += "%d <- BASE\n" % (cid)
        return ans
    def agnes_explain_pair(self, c0, c1):
        return self.agnes_dist_func(self.agnes_nodes[c0], self.agnes_nodes[c1], explain=True)
    def agnes_get_result_node_idx(self):
        return [i for i in range(self.agnes_max_idx) if self.agnes_active[i]]
    def agnes_edges_for_node(self, i):
        ans = []
        for j in self.agnes_edges[i]:
            if j >= self.agnes_max_idx or not self.agnes_active[j]: continue
            ans.append(j)
        return ans
    def agnes_get_result_edge_idx(self):
        ans = []
        for i in range(self.agnes_max_idx):
            if not self.agnes_active[i]: continue
            for j in self.agnes_edges[i]:
                if j>=self.agnes_max_idx: continue
                if not self.agnes_active[j]: continue
                if j>=i: continue
                ans.append([i,j])
        return ans

