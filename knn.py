from __future__ import division
"""

Simple k nearest neighbors implementation

Created on 29/01/2011

@author: peter
"""
import  math, pickle
import numpy as np

def get_knn(k, training_data, training_data_class, test_data):
    """ Naive implementation of k nearest neighbors
        k: number of nearest neighbors
        training_data: training training_data instances
        training_data_class: classes of each training training_data instance
        test_data: test_data to classify
        returns: classes of each input instance
    """
    num_inputs = np.shape(test_data)[0]
    if False:
        print 'num_inputs =', num_inputs
        print 'training_data =', training_data
        print 'training_data_class =', training_data_class
        print 'test_data =', test_data
    closest = np.zeros(num_inputs)

    for n in range(num_inputs):
        distances = np.sqrt(np.sum((training_data - test_data[n,:])**2, axis = 1))
        #print 'i =', test_data[n,:]
        #print 'd =', distances
    
        indices = np.argsort(distances, axis = 0)
        #print 'indices =', indices
        
        classes = training_data_class[indices[:k]]
        #print 'classes =', classes
    
        classes = np.unique(classes)
        #print 'unique classes =', classes
        if len(classes) == 1:
            closest[n] = np.unique(classes)
        else:
            #print 'x'*10
            counts = np.zeros(max(classes) + 1)
            for i in range(k):
                counts[training_data_class[indices[i]]] += 1
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
    """ Make classification test training_data 
        num_instances: number of training samples
        num_classes: number of different classes for samples
        num_dimensions: number of attributes in training_data
        max_delta: each attribute of each training sample is in range 
                    [centroid-max_deta,centroid+max_delta]
        returns: training_data,training_data_class,test_data,test_data_class
            training_data: training samples
            training_data_class: classes of training samples
            test_data: test samples
            test_data_class: classes of test samples
    """
    verbose = False
    
    print 'make_data', num_instances, num_classes, num_dimensions
    instances_per_class = int(math.ceil(num_instances/num_classes))
    centroids = [[i+1] * num_dimensions for i in range(num_classes)]
    training_data_class = []
    training_data = []
    for i in range(num_instances):
        clazz = i//instances_per_class
        cent = centroids[clazz]
        val = [cent[j] + rand(max_delta) for j in range(num_dimensions)]
        training_data_class.append(clazz)
        training_data.append(val)
    test_data = sorted(centroids) 
    ratio = 4.0
    for k in range(1):
        #print len(test_data), test_data
        for i in range(1,len(test_data)):
            new_els = [[blend(test_data[i-1][j], test_data[i][j], ratio) for j in range(num_dimensions)],
                       [blend(test_data[i-1][j], test_data[i][j], 1.0/ratio) for j in range(num_dimensions)]]
            #print 'new_els = ', new_els
            test_data += new_els
        test_data.sort()
    if verbose:
        print 'centroids', centroids
        print 'test_data', len(test_data), test_data
        print 'training_data', training_data
        print 'training_data_class', training_data_class
    test_data_class = [np.argmin(np.array([abs(inp[0] - cent[0]) for cent in centroids])) for inp in test_data]
    if verbose:
        for i,inp in enumerate(test_data):
            print '%2d:'%i, [abs(inp[0] - cent[0]) for cent in centroids], test_data_class[i]
    test_data_class = [np.argmin(np.array([abs(inp[0] - cent[0]) for cent in centroids])) for inp in test_data]
    if verbose:
        print 'test_data_class', test_data_class
    #exit()
    return np.array(training_data), np.array(training_data_class), np.array(test_data), np.array(test_data_class)

def test_knn_on_sample(title, num_instances, num_classes, num_dimensions, max_delta):
    """ Test get_knn() by running it on some synthetic samples
        title: name of test
        num_instances: number of training samples
        num_classes: number of different classes for samples
        num_dimensions: number of attributes in training_data
        max_delta: each attribute of each training sample is in range 
                    [centroid-max_deta,centroid+max_delta]
        return: True iff all samples are classified correctly
    """
    print '#'*40
    training_data,training_data_class,test_data,test_data_class = make_data(num_instances, num_classes, num_dimensions, max_delta)
    print '='*40
    print 'num_instances, num_classes, num_dimensions, max_delta =', num_instances, num_classes, num_dimensions, max_delta
    for k in range(1, min(10,num_instances//num_classes)+1):
        print '-'*40 + ':', title, num_instances, num_classes, num_dimensions, max_delta 
        closest = get_knn(k, training_data, training_data_class, test_data)
        print 'k =', k
        print 'closest =', closest
        print 'test_data_class =', test_data_class
        matches = [closest[i] == test_data_class[i] for i in range(test_data_class.shape[0])]
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
        training_data = np.array([[1,2,3],[3,1,2],[2,3,1],[4,5,6],[6,4,5],[5,6,4]])
        training_data_class = np.array([0,0,0,1,1,1])
        test_data = np.array([[2,2,2],[5,5,5],[3.4,3.5,3.6]])
         
    num_instances, num_classes, num_dimensions, max_delta = 35, 5, 3, 0.3
    num_instances, num_classes, num_dimensions, max_delta = 6, 2, 1, 0.1
    #num_instances, num_classes, num_dimensions, max_delta = 35, 5, 1, 0.3
    num_instances, num_classes, num_dimensions, max_delta = 35, 5, 1, 0.4
    #num_instances, num_classes, num_dimensions, max_delta = 10055, 5, 17, 0.4
    #num_instances, num_classes, num_dimensions, max_delta = 1090055, 15, 27, 0.49
    training_data,training_data_class,test_data,test_data_class = make_data(num_instances, num_classes, num_dimensions, max_delta)
   
    for k in range(1, min(10,num_instances//num_classes)+1):
        print '-'*20
        closest = get_knn(k, training_data, training_data_class, test_data)
        print 'k =', k
        print 'closest =', closest
        print 'test_data_class =', test_data_class
        matches = [closest[i] == test_data_class[i] for i in range(test_data_class.shape[0])]
        print 'matches =', matches
        if not all(matches):
            print 'mismatch!'
            exit()

if __name__ == '__main__':
    test_knn()
    