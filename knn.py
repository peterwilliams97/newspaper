from __future__ import division
"""

Simple k nearest neighbors implementation

Created on 29/01/2011

@author: peter
"""
import random, math
import numpy as np

def get_knn(k, data, data_class, inputs):
    """ Naive implementation of k nearest neighbors
        k: number of nearest neighbors
        data: training data instances
        data_class: classes of each training data instance
        inputs: inputs to classify
        returns: classes of each input instance
    """
    num_inputs = np.shape(inputs)[0]
    if False:
        print 'num_inputs =', num_inputs
        print 'data =', data
        print 'data_class =', data_class
        print 'inputs =', inputs
    closest = np.zeros(num_inputs)

    for n in range(num_inputs):
        distances = np.sqrt(np.sum((data - inputs[n,:])**2, axis = 1))
        #print 'i =', inputs[n,:]
        #print 'd =', distances
    
        indices = np.argsort(distances, axis = 0)
        #print 'indices =', indices
        
        classes = data_class[indices[:k]]
        #print 'classes =', classes
    
        classes = np.unique(classes)
        #print 'unique classes =', classes
        if len(classes) == 1:
            closest[n] = np.unique(classes)
        else:
            #print 'x'*10
            counts = np.zeros(max(classes) + 1)
            for i in range(k):
                counts[data_class[indices[i]]] += 1
            #print 'counts =', counts
            closest[n] = np.argmax(counts)

    return closest

def rand(max_delta):
    """ Return a random number in range [-max_delta..max_delta] """
    return (np.random.random() - 0.5) * max_delta/0.5
    
def make_data(num_instances, num_classes, num_dimensions, max_delta):
    """ Make classification test data 
        num_instances: number of training samples
        num_classes: number of different classes for samples
        num_dimensions: number of attributes in data
        max_delta: each attribute of each training sample is in range 
                    [centroid-max_deta,centroid+max_delta]
        returns: data,data_class,inputs,inputs_class
            data: training samples
            data_class: classes of training samples
            inputs: test samples
            inputs_class: classes of test samples
    """
    
    print 'make_data', num_instances, num_classes, num_dimensions
    instances_per_class = int(math.ceil(num_instances/num_classes))
    centroids = [[i+1] * num_dimensions for i in range(num_classes)]
    data_class = []
    data = []
    for i in range(num_instances):
        clazz = i//instances_per_class
        cent = centroids[clazz]
        val = [cent[j] + rand(max_delta) for j in range(num_dimensions)]
        data_class.append(clazz)
        data.append(val)
    inputs = sorted(centroids) 
    for k in range(2):
        print len(inputs), inputs
        for i in range(1,len(inputs)):
            inputs.append([(1.1*inputs[i-1][j] + 0.9*inputs[i][j])/2 for j in range(num_dimensions)])
        inputs.sort()
    if False:
        print centroids
        print len(inputs), inputs
        print data
        print data_class
        print '***', [[abs(inp[0] - cent[0]) for cent in centroids] for inp in inputs]
    inputs_class = [np.argmin(np.array([abs(inp[0] - cent[0]) for cent in centroids])) for inp in inputs]
    if False:
        for i,inp in enumerate(inputs):
            print '%2d:'%i, [abs(inp[0] - cent[0]) for cent in centroids], inputs_class[i]
    inputs_class = [np.argmin(np.array([abs(inp[0] - cent[0]) for cent in centroids])) for inp in inputs]
    print inputs_class
    #exit()
    return np.array(data), np.array(data_class), np.array(inputs), np.array(inputs_class)

def test_knn_on_sample(num_instances, num_classes, num_dimensions, max_delta):
    """ Test get_knn() by running it on some synthetic samples
        num_instances: number of training samples
        num_classes: number of different classes for samples
        num_dimensions: number of attributes in data
        max_delta: each attribute of each training sample is in range 
                    [centroid-max_deta,centroid+max_delta]
        return: True iff all samples are classified correctly
    """
    print '#'*40
    data,data_class,inputs,inputs_class = make_data(num_instances, num_classes, num_dimensions, max_delta)
    print '='*40
    print 'num_instances, num_classes, num_dimensions, max_delta =', num_instances, num_classes, num_dimensions, max_delta
    for k in range(1, min(10,num_instances//num_classes)+1):
        print '-'*40
        closest = get_knn(k, data, data_class, inputs)
        print 'k =', k
        print 'closest =', closest
        print 'inputs_class =', inputs_class
        matches = [closest[i] == inputs_class[i] for i in range(inputs_class.shape[0])]
        print 'matches =', matches
        if not all(matches):
            print 'mismatch!'
            return False
    
    return True

def test_knn():
    test_settings = [(35, 5, 3, 0.3),
                     ( 6, 2, 1, 0.1),
                     (35, 5, 1, 0.4),
                     (10055, 5, 17, 0.4),
                     (15, 27, 0.49)]
    for num_instances, num_classes, num_dimensions, max_delta in test_settings:
        if not test_knn_on_sample(num_instances, num_classes, num_dimensions, max_delta):
            exit()
            
def test_knn0():
    if False:
        data = np.array([[1,2,3],[3,1,2],[2,3,1],[4,5,6],[6,4,5],[5,6,4]])
        data_class = np.array([0,0,0,1,1,1])
        inputs = np.array([[2,2,2],[5,5,5],[3.4,3.5,3.6]])
         
    num_instances, num_classes, num_dimensions, max_delta = 35, 5, 3, 0.3
    num_instances, num_classes, num_dimensions, max_delta = 6, 2, 1, 0.1
    #num_instances, num_classes, num_dimensions, max_delta = 35, 5, 1, 0.3
    num_instances, num_classes, num_dimensions, max_delta = 35, 5, 1, 0.4
    #num_instances, num_classes, num_dimensions, max_delta = 10055, 5, 17, 0.4
    #num_instances, num_classes, num_dimensions, max_delta = 1090055, 15, 27, 0.49
    data,data_class,inputs,inputs_class = make_data(num_instances, num_classes, num_dimensions, max_delta)
   
    for k in range(1, min(10,num_instances//num_classes)+1):
        print '-'*20
        closest = get_knn(k, data, data_class, inputs)
        print 'k =', k
        print 'closest =', closest
        print 'inputs_class =', inputs_class
        matches = [closest[i] == inputs_class[i] for i in range(inputs_class.shape[0])]
        print 'matches =', matches
        if not all(matches):
            print 'mismatch!'
            exit()

if __name__ == '__main__':
    test_knn()
    