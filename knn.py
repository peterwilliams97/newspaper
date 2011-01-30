from __future__ import division
"""

Simple k nearest neighbors implementation

Created on 29/01/2011

@author: peter
"""
import  math, pickle
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

def blend(a,b,r):
    """ Blend a and b with ratio r """
    return (r*a + b)/(1.0 + r)
    
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
    verbose = False
    
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
    ratio = 4.0
    for k in range(1):
        #print len(inputs), inputs
        for i in range(1,len(inputs)):
            new_els = [[blend(inputs[i-1][j], inputs[i][j], ratio) for j in range(num_dimensions)],
                       [blend(inputs[i-1][j], inputs[i][j], 1.0/ratio) for j in range(num_dimensions)]]
            #print 'new_els = ', new_els
            inputs += new_els
        inputs.sort()
    if verbose:
        print 'centroids', centroids
        print 'inputs', len(inputs), inputs
        print 'data', data
        print 'data_class', data_class
    inputs_class = [np.argmin(np.array([abs(inp[0] - cent[0]) for cent in centroids])) for inp in inputs]
    if verbose:
        for i,inp in enumerate(inputs):
            print '%2d:'%i, [abs(inp[0] - cent[0]) for cent in centroids], inputs_class[i]
    inputs_class = [np.argmin(np.array([abs(inp[0] - cent[0]) for cent in centroids])) for inp in inputs]
    if verbose:
        print 'inputs_class', inputs_class
    #exit()
    return np.array(data), np.array(data_class), np.array(inputs), np.array(inputs_class)

def test_knn_on_sample(title, num_instances, num_classes, num_dimensions, max_delta):
    """ Test get_knn() by running it on some synthetic samples
        title: name of test
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
        print '-'*40 + ':', title, num_instances, num_classes, num_dimensions, max_delta 
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

def make_pickle_filename(name):
    return 'knn.%s.pkl' % name

def get_pickled_base(name):
    f = open(make_pickle_filename(name), 'rb')
    val = pickle.load(f)
    f.close()
    return val

def set_pickled(name, val):
    f = open(make_pickle_filename(name), 'wb')
    val = pickle.dump(val,f)
    f.close()

def get_pickled(name, default):
    try:
        val = get_pickled_base(name)
    except:
        set_pickled(name, default)
        val = get_pickled_base(name)
    return val

def test_knn():
    # Need to seed random number generator to give same result for each run
    np.random.seed(111)
    test_settings = [(4, 2, 50, 0.499),
                     (4, 2, 2, 0.1),
                     (35, 5, 3, 0.3),
                     ( 6, 2, 1, 0.1),
                     (35, 5, 1, 0.4),
                     (10055, 5, 17, 0.4),
                     #(10055, 15, 27, 0.49)
                     ]

    title = 'base test' 
    for num_instances, num_classes, num_dimensions, max_delta in test_settings:
        if not test_knn_on_sample(title, num_instances, num_classes, num_dimensions, max_delta):
            exit()
    
    test_number = 1
    # highest_max_delta convergeed to 0.324486403921 in previous testing
    highest_max_delta = get_pickled('highest_max_delta', 0.4999)           
    while True:
        title = 'test %02d' % test_number
        for num_instances, num_classes, num_dimensions, max_delta in test_settings:
            while True:
                if test_knn_on_sample(title,num_instances, num_classes, num_dimensions, highest_max_delta):
                    break
                highest_max_delta *= 0.99
                set_pickled('highest_max_delta', highest_max_delta)
        print '*** test:', test_number, ', highest_max_delta:', highest_max_delta 
        test_number += 1
            
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
    