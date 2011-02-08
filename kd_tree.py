from __future__ import division
""" 
    KDTree implementation.
    Replacement for scipy.spatial import KDTree which loops forever with my data

    Based on 
        http://en.wikipedia.org/wiki/Kd-tree and 
         http://code.google.com/p/python-kdtree/downloads/detail?name=kdtree.py

    Peter Williams
    23/11/2010

"""

# Coding conventions
# ------------------
# indexed_point = (point, index)

__version__ = '1'
__all__ = ['KDTree']

import numpy as np

def get_distance2(a, b):
    return sum([(x[1]-x[0])**2 for x in zip(a,b)])

class KDTreeNode():
    def __init__(self, indexed_point, left, right):
        self.index = indexed_point[1]
        self.point = indexed_point[0]
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left == None and self.right == None

class KDTreeNeighbours():
    """ Internal structure used in nearest-neighbours search.
    """
    def __init__(self, query_point, k):
        self.query_point = query_point  # point for which knn are being found
        self.k = k                      # #neighbours wanted. 
        self.largest_distance2 = 0
        self.current_best = []          # list of nearest neighbours so far, sorted best to worst
                                        # each element is (point,index,distance)

    def _check_current_best(self):
        """ Consistency check """
        last_distance = 0.0
        for _,_,distance in self.current_best:
            assert(last_distance <= distance)
            last_distance = distance

    def calculate_largest(self):
        for point, index, distance2 in self.current_best:
            assert(isinstance(index, int))
            assert(isinstance(distance2, float))

        if self.k >= len(self.current_best):
            self.largest_distance2 = self.current_best[-1][2]
        else:
            self.largest_distance2 = self.current_best[self.k-1][2]
        self._check_current_best()

    def add(self, point, index):
        """ Add a point to the nearest neighbour list if it closest than k nearest neighbours """
        assert(isinstance(index, int))
        distance2 = get_distance2(point, self.query_point)
        #print 'add', point, index, distance2

        # run through current_best, try to find appropriate place
        # ~!@# replace with a binary search
        for i, e in enumerate(self.current_best):
            if i >= self.k:
                return # have enough neighbours, this one is further so forget it
            if e[2] > distance2:
                self.current_best.insert(i, [point, index, distance2])
                self.calculate_largest()
                return
        # append it to the end otherwise
        self.current_best.append([point, index, distance2])
        self.calculate_largest()
    
    def get_best(self):
        if False:
            print 'get_best:'
            print 'k =', self.k
            print 'current_best =', [(i,e) for i,e in enumerate(self.current_best[:3])]
            print 'best k =', self.current_best[:self.k]
        for point, index, distance2 in self.current_best:
            assert(isinstance(index, int))
            assert(isinstance(distance2, float))
        return self.current_best[:self.k]

class KDTree():
    """ KDTree implementation.
    
        Example usage:
        
            from kdtree import KDTree
            
            data = <load data> # iterable of points (which are also iterable, same length)
            point = <the point of which neighbours we're looking for>
            
            tree = KDTree.construct_from_data(data)
            nearest = tree.query(point, k=4) # find nearest 4 points
    """
    
    def __init__(self, training_data):
        # assume all points have the same dimension
        num_axes = len(training_data[0])

        def build_kdtree(indexed_point_list, depth):
            # code based on wikipedia article: http://en.wikipedia.org/wiki/Kd-tree
            if indexed_point_list is None:
                assert(indexed_point_list is not None)
                return None
            
            # Got to a terminal node
            if len(indexed_point_list) == 0:
                return None

            # select axis based on depth so that axis cycles through all valid values
            axis = depth % num_axes # assumes all points have the same dimension

            # sort point list and choose median as pivot point,
            # TODO: better selection method, linear-time selection, distribution
            indexed_point_list.sort(key=lambda indexed_point: indexed_point[0][axis])
            median = len(indexed_point_list)//2 # choose median

            # create node and recursively construct subtrees
            #print '@', depth, len(indexed_point_list), median
            node = KDTreeNode(indexed_point = indexed_point_list[median],
                              left = build_kdtree(indexed_point_list[0:median], depth+1),
                              right = build_kdtree(indexed_point_list[median+1:], depth+1))
            return node

        indexed_data = [(x,i) for i,x in enumerate(training_data)]
        self.root_node = build_kdtree(indexed_data, depth=0)

    @staticmethod
    def construct_from_data(data):
        tree = KDTree(data)
        return tree

    def query(self, a_query_point, k=1):
        """ a_query_point: point to find nearest neighbours of a NumPy array
            k: number of nearest neighbours to find
            return: distances, indices sorted by distance
        """
        query_point = list(a_query_point)
        #print 'query_point', len(query_point), query_point, a_query_point
        statistics = {'nodes_visited': 0, 'far_search': 0, 'leafs_reached': 0}

        def nn_search(node, query_point, k, depth, best_neighbours):
            if node == None:
                return
            
            #statistics['nodes_visited'] += 1
            
            # if we have reached a leaf, let's add to current best neighbours,
            # (if it's better than the worst one or if there is not enough neighbours)
            if node.is_leaf():
                #statistics['leafs_reached'] += 1
                best_neighbours.add(node.point, node.index)
                return
            
            # this node is no leaf
            
            # select dimension for comparison (based on current depth)
            axis = depth % len(query_point)
            
            # figure out which subtree to search
            near_subtree = None # near subtree
            far_subtree = None # far subtree (perhaps we'll have to traverse it as well)
            
            # compare query_point and point of current node in selected dimension
            # and figure out which subtree is farther than the other
            if query_point[axis] < node.point[axis]:
                near_subtree = node.left
                far_subtree = node.right
            else:
                near_subtree = node.right
                far_subtree = node.left

            # recursively search through the tree until a leaf is found
            nn_search(near_subtree, query_point, k, depth+1, best_neighbours)

            # while unwinding the recursion, check if the current node
            # is closer to query point than the current best,
            # also, until k points have been found, search radius is infinity
            best_neighbours.add(node.point, node.index)
            
            # check whether there could be any points on the other side of the
            # splitting plane that are closer to the query point than the current best
            if (node.point[axis] - query_point[axis])**2 < best_neighbours.largest_distance2:
                #statistics['far_search'] += 1
                nn_search(far_subtree, query_point, k, depth+1, best_neighbours)
            
            return
        
        # if there's no tree, there are no neighbours
        if self.root_node != None:
            neighbours = KDTreeNeighbours(query_point, k)
            nn_search(self.root_node, query_point, k, depth=0, best_neighbours=neighbours)
            #print 'neighbours.get_best()', neighbours.get_best()
            result = [[x[i] for x in neighbours.get_best()] for i in (2,1)]
            #print 'result =', result
            #exit()
        else:
            result = []*2
        
        #print statistics
        last_x = 0.0
        for x in result[0]:
            assert(x >= last_x)
            last_x = x
        return [np.array(x) for x in result]
