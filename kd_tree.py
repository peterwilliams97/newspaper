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

max_depth = 4
class Node:
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
    node = Node()
    node.location = point_list[median]
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

if __name__ == '__main__':
    test1()
