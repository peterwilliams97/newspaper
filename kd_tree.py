from __future__ import division
"""
http://en.wikipedia.org/wiki/Kd-tree

Peter Williams
23/11/2010
"""

import re
import sys
import math
import operator
from bisect import insort
from bisect import bisect

def distance(a, b):
    #print 'distance', a, b, '=',
    dist = math.sqrt(sum([(x[1]-x[0])**2 for x in zip(a,b)]))
    #print dist
    return dist

def distanceAxis(a, b, axis):
    x = axis % len(a)
    #print 'distanceAxis', a, b, axis, '=',
    dist = abs(a[x]-b[x])
    #print dist
    return dist


class Node:
    def childNearAway(self, point, sign):
        #print '***', self.location
        #children = sorted([c for c in (self.left_child, self.right_child) if c], key = lambda c: sign*distance(c.location,point))
        children = [c for c in (self.left_child, self.right_child) if c]
        #print 'children', children
        #print 'children.location', [c.location for c in children]
        if False:
            def dist(child):
                print 'dist', child, 
                print child.location
                return sign*distance(child.location,point)
            children.sort(key = dist)
        children.sort(key = lambda c: sign*distance(c.location,point))
        if len(children) == 0:
            return None
        else:
            return children[0]
        
    def childNear(self, point):
        return self.childNearAway(point, +1)

    def childAway(self, point):
        return self.childNearAway(point, -1)

    def addToList(self, tree, leftmost, max_depth, depth, rightness):
        if self.location:
            if rightness < leftmost[0]:
                leftmost[0] = rightness
            if not depth in tree.keys():
                tree[depth] = {}
            tree[depth][rightness] = self.location 
            if self.left_child:
                self.left_child.addToList(tree, leftmost, max_depth, depth + 1, rightness - (max_depth - depth)**2)
            if self.right_child:
                self.right_child.addToList(tree, leftmost, max_depth, depth + 1, rightness + (max_depth - depth)**2)
            print 'tree[%d]' % depth, tree[depth]

    def show(self):
        tree = {}
        leftmost = [0]
        self.addToList(tree, leftmost, 0, 0, 0)
        max_depth = max(tree.keys()) + 0
        tree = {}
        leftmost = [0]
        self.addToList(tree, leftmost, max_depth, 0, 0)
        for depth in sorted(tree.keys()):
            x = 0
            print '%2d:' % depth,
            for r in sorted(tree[depth].keys()):
                while x < (r - leftmost[0]) * len(tree[0][0]):
                    print '',
                    x += 1
                s = str(tree[depth][r])
                print s,
                x += len(s) + 1
            print
        for depth in sorted(tree.keys()):
            print 'tree[%d]' % depth, tree[depth]

     
def kdTree(point_list, depth = 0):
    if not point_list:
        return
 
    # Select axis based on depth so that axis cycles through all valid values
    k = len(point_list[0]) # assumes all points have the same dimension
    axis = depth % k
 
    # Sort point list and choose median as pivot element
    point_list.sort(key=lambda point: point[axis])
    median = len(point_list) // 2 # choose median
 
    # Create node and construct subtrees
    location = point_list[median]
    if not location:
        return None
    node = Node()
    node.location = location
    node.left_child = kdTree(point_list[0:median], depth+1)
    node.right_child = kdTree(point_list[median+1:], depth+1)
    return node

def test1():
    point_list = [[i] for i in range(1,32)]
    point_list = [(i, i*2) for i in range(1,8)]
    point_list = [(i, i*2, i*3) for i in range(1,16)]
    point_list = [(i, 8-i) for i in range(1,8)]
    point_list = [(i, 16-i) for i in range(1,16)]
    node = kdTree(point_list)
    node.show()

def kdSearchNN(here, point, best, depth):
    if not here:
        return best
 
    if not best:
        best = here

    # consider the current node
    if distance(here.location, point) < distance(best.location,point):
        best = here

    # search the near branch
    child = here.childNear(point)
    best = kdSearchNN(child, point, best, depth+1)

    # search the away branch - maybe
    if distanceAxis(here.location,point, depth) < distance(best.location,point):
        child = here.childAway(point)
        best = kdSearchNN(child, point, best, depth+1)

    return best

def test2():
    point_list = [[i] for i in range(1,32)]
    node = kdTree(point_list)
    node.show()


    print 'point_list', point_list
    for point in point_list:
        best = kdSearchNN(node, point, node, 0)
        print 'point =', point, ', best =', best.location

if __name__ == '__main__':
    # test1()
    test2()
