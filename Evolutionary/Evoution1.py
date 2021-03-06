import math
import operator
from random import uniform
import numpy as np
from collections import defaultdict
import numpy as np
import primefac
from DifferentialEvolution.differential_evolution_functions import Mutation,Repair_Solution,Select_Random
import random
data=np.array
matrix=np.array

def mapping(data, data_K, matrix, matrix_K, feature):   #A, A_K, neuron_data, neuron_K,features
    """

    :param data: entire population
    :param matrix: Neuron matrix on which "solutions in data" is to be mapped
    :return: Mapped matrix "matrix"
    """

    max_mapped = math.ceil(data.shape[0]/matrix.shape[0])  # Maximum no. of solutions that can be mapped to a single neuron

    dd={} #Dictionary for distance
    neuron_to_data_mapping = {}
    data_to_neuron_mapping = {}
    data_neurons_sorted_dist = {}
    U = np.arange(matrix.shape[0]) # Set of neurons in lattice
    for i in range(len(data)): # For each population neuron
        temp1_K=np.copy(data_K[i])

        '''During finding minimum distance between input and the weight vector
            chose the dimension of one which has max appended zero[Line 33- Line47]'''
        datacounter=temp1_K*feature
        for j in range(len(matrix)):
            temp1 = np.copy(data[i])
            temp2 = np.copy(matrix[j])
            temp2_K=np.copy(matrix_K[j])
            matrixcounter=temp2_K*feature
            if matrixcounter>datacounter:
                for some_counter in range (datacounter,len(temp2)):
                    temp2[some_counter]=0
            elif matrixcounter<datacounter:
                for some_counter in range (matrixcounter,len(temp1)):
                    temp1[some_counter]=0
            elif matrixcounter== datacounter:
                pass

            dist = np.linalg.norm(temp1 - temp2)
            dd[j]=dist
        data_neurons_sorted_dist[i] = sorted(dd.items(), key=operator.itemgetter(1))  # Sort the dictionary in ascending order

    data_neurons_sorted_dist = sorted(data_neurons_sorted_dist.items(), key=lambda x:x[1][0][1]) # Sort data according to closest distance to neuron
    while(data_neurons_sorted_dist):
        closest_neuron = data_neurons_sorted_dist[0][1][0][0]
        if(not neuron_to_data_mapping.has_key(closest_neuron)):
            neuron_to_data_mapping[closest_neuron] = [data_neurons_sorted_dist[0][0]]
            data_to_neuron_mapping[data_neurons_sorted_dist[0][0]] = closest_neuron
            del data_neurons_sorted_dist[0]
        elif(len(neuron_to_data_mapping[closest_neuron]) < max_mapped):
            neuron_to_data_mapping[closest_neuron].append(data_neurons_sorted_dist[0][0])
            data_to_neuron_mapping[data_neurons_sorted_dist[0][0]] = closest_neuron
            del data_neurons_sorted_dist[0]
        elif(len(neuron_to_data_mapping[closest_neuron]) >= max_mapped):
            del data_neurons_sorted_dist[0][1][0]
            temp = data_neurons_sorted_dist[0]
            del data_neurons_sorted_dist[0]
            counter = 0
            while(counter < len(data_neurons_sorted_dist) and data_neurons_sorted_dist[counter][1][0][1] < temp[1][0][1]):
                counter += 1
            data_neurons_sorted_dist.insert(counter,temp)
        else:
            print("Unknown case encountered")
            raise AssertionError

    return neuron_to_data_mapping, data_to_neuron_mapping

def generate_matingPool(H, i, x, x_K, feature, matrix, matrix_K, pop_data, pop_length, neuron_to_data_mapping, data_to_neuron_mapping, lattice, beta=0):   #H, i, A[i],A_K[i], neuron_weight, neuron_K, beta=0.7
    """
    :param H: Number of solutions in mating pool of each neuron (size of H<=no. of neuron in Lattice)
    :param i: current solution no.
    :param x: current solution
    :param x_K:  clusters K of current solution
    :param matrix: neuron weight matrix
    :param matrix_K: clusters K of each neuron
    :param beta:
    :return: mating pool of current solution x
    """

    dd={}
    mating_pool=[]
    flag=0
    if uniform(0,1)<beta:
        flag=0
        mapped_neuron = data_to_neuron_mapping[i]
        neuron_index = lattice[mapped_neuron]

        for j in range(len(matrix)):
            other_neuron = lattice[j]
            dist = np.linalg.norm(np.asarray(lattice[j])-np.asarray(neuron_index))
            dd[j] = dist
        sorted_x = sorted(dd.items(), key=operator.itemgetter(1))

        counter=0
        for k, v in sorted_x:
            if(counter < H):
                data_point = 0
                while(data_point < len(neuron_to_data_mapping[k]) and counter < H):
                    if(not np.array_equal(pop_data[neuron_to_data_mapping[k][data_point]], x)):
                        mating_pool.insert(counter,neuron_to_data_mapping[k][data_point])
                        counter += 1
                    data_point += 1
            else:
                break
    else:
        flag=1
        #print "Random probability is greater than Beta for this neuron therefore assign population as the mating pool for neuron {0}".format(i)
        for i in range(pop_length):
            if(not np.array_equal(pop_data[i],x)):
                mating_pool.append(i)
        #print  "Mating pool for solution {} in population".format(i),mating_pool
    return np.asarray(mating_pool),flag

def Generate(Idata,Q, neuron_to_data_mapping, data_to_neuron_mapping, neuron_weights, H, population,i, x, x_K, feature,flag, max_solution_length, b, a,CR=0,F=0, mutation_prob=0,eta=0):
            #Idata,MatingPool, neuron_weight, H, A, i,A[i], A_K[i],feature,flag,CR=0.8,F=0.8,mutation_prob=0.6,eta=20
    """
    :param Idata: Normalised Dataset
    :param Q: Mating pool
    :param neuron_weights: Neuron weight matrix
    :param population: Archive population
    :param i: current solution index
    :param x: current solution
    :param x_K: current solution corresponding clusters
    :param flag: Flag value
    :param max_solution_length: maximum length of the solutions
    :param b:upper bound of each variable
    :param a: lower bound of each variable
    :param CR: cross-over probability
    :param H: Size of mating pool
    :return: New solution
    """
    mp=uniform(0,1)
    yRep = []
    y1, y2 = Select_Random(Q, neuron_weights, population,i,flag, x)
    # print "solution y1 : ", y1
    # print "solution y2 : ", y2
    y_dash = []
    x_copy=np.copy(x)
    count=None
    nsol = np.zeros((len(x)))
    x_count= x_K*feature
    for j in range(x_count):
        if CR >= uniform(0,1): # CR value specified as 0.8
            m = y1[j] - y2[j]
            y_dash.insert(j, x_copy[j] + F * m)  # Value of taken as F=0.9
        else:
            y_dash.insert(j, x_copy[j])                      #Otherwise
    y_dash.extend(0 for j in range(len(x_copy)-x_count))
    y_dash = np.array(y_dash)
    yRep = Repair_Solution(y_dash, population, neuron_weights, flag, x_K, x_count, b, a, feature)  # Repaired solution

    for m in range(x_count): # Since x_count holds nonzero count of y_dash and so of yRep
        if mutation_prob > uniform(0,1):  # Mutation probability
            DeltaR = uniform(0, 1)
            if DeltaR < 0.5:
                #print "upper and lower value for {0}th component for solution {1} :".format(m,i), b[m],",",a[m]
                if b[m]==a[m]:
                    b[m]=1
                    a[m]=0
                p=eta + 1
                temp2 = math.pow(((b[m] - yRep[m]) / (b[m] - a[m])),p)
                temp1=((2 * DeltaR) + (1 - 2 * DeltaR) *temp2 )
                t1=1 /float(p)
                di = math.pow(abs(temp1), t1)-1
                #print "a, di : ", tt, di
                nsol[m] = Mutation(yRep[m], di, b[m], a[m])
            else:
                #print "upper and lower value for {0}th component for solution {1} :".format(m, i), b[m], ",", a[m]
                if b[m] == a[m]:
                    b[m] = 1
                    a[m] = 0
                p=float((eta + 1))
                temp1 = math.pow(((yRep[m] - a[m]) / (b[m] - a[m])),p)
                temp2= 1/p
                ist_power = math.pow(abs(2 - 2 * DeltaR + (2 * DeltaR - 1) * temp1), temp2)
                #print "  math.pow(2 - 2 * DeltaR + (2 * DeltaR - 1) * temp1, p)  =  ", ist_power
                di = 1 - ist_power
                nsol[m] = Mutation(yRep[m], di, b[m], a[m])
        else:
            nsol[m] = yRep[m]

    if mp < 0.75:
        #print "Normal mutation  for solution {0} ".format(i)
        return list(nsol), x_K

    elif mp>=0.75 and mp<0.9:
        """Insertion Mutation"""

        count=x_count
        idx= random.randint(0,len(Idata)-1) # generate random no.(idx) which will be used as index to fetch data from Idata
        data_value = np.copy(Idata[idx]) # Extract data from Actual data

        #print "xcount and max sol length :", x_count,",", max_solution_length
        if x_count < max_solution_length: # If count=0, that means Repaired solution yRep if full and insertion mutation cannot be performed
            #print "Insert mutation  for solution {0} ".format(i)
            for j in range(len(data_value)):
                nsol[count]=data_value[j]
                count+=1
            nsol = list(nsol)
            return nsol, x_K+1
        else:
            #print "Insert mutation, but no change  for solution {0} ".format(i)
            nsol=list(nsol)
            return nsol, x_K

    elif mp>=0.9  and mp<=1.0:
        """Deletion Mutation"""

        count=x_count
        data_length= len(Idata[0])
        if count > 2*data_length : # Why 2? As minimum 2 cluster should be there in solution.For 2 cluster "chromosome length" = 2* data_length and "count" gives the nonzero
            """Perform deletion mutation""" # values in yRep. So  yRep should contain more nonzero value than "chromosome length"
            #print "Deletion Mutation  for solution {0} ".format(i)
            for j in range (data_length):
                nsol[count-1]=0
                count-=1
            nsol=list(nsol)
            #print "New Solution", nsol
            return nsol,x_K-1
        else:
            #print "Deletion Mutation, but no change for solution {0}".format(i)
            nsol = list(nsol)
            #print "New Solution remain same : ", nsol
            return nsol, x_K



def Mapsize(n):

    factors = list( primefac.primefac(n) )
    #print factors
    if len(factors)==1:
        return 1, n
    elif len(factors)==2:
        return factors[0],factors[1]
    else:
        x=int(math.floor(len(factors)/2))
        #print x

        p1=1
        p2=1
        p3=1
        for i in range(x+1):
            p1=p1*factors[i]
        for j in range(x+1,len(factors)):
            p2 = p2 * factors[j]
        return p1,p2

def calculate_dunn_index( data, label,n_cluster=0):
    data=data.tolist()
    d1=[]
    d2=[]
    d3=[]
    cluster_data=defaultdict(list)
    for i in range (n_cluster):
        for j in range (len(label)):
            if label[j]==i:
                cluster_data[i].append(data[j])

    for k,v in cluster_data.iteritems():

        cluster_list=cluster_data[k]
        for i in range (len(cluster_list)):
            temp1=cluster_list[i]
            for j in range(len(cluster_list)):
                temp2 = cluster_list[j]

                dist = np.linalg.norm(np.asarray(temp1) - np.asarray(temp2))
                d1.insert(j,dist)

            d2.insert(i,max(d1))
            d1=[]

        d3.insert(k,max(d2))
        d2=[]
    xmax= max(d3)
    #################################################################################################
    #Calcuation of minimum distance
    d1=[]
    d2=[]
    d3=[]
    d4=[]
    for k, v in cluster_data.iteritems():
        cluster_list=cluster_data[k]

        for j in range(len(cluster_list)):
            temp1=cluster_list[j]
            for key,value in cluster_data.iteritems():
                if not key==k:
                    other_cluster_list=cluster_data[key]
                    for index in range ((len(other_cluster_list))):
                        temp2=other_cluster_list[index]
                        dist=np.linalg.norm(np.asarray(temp1)-np.asarray(temp2))
                        d1.insert(index,dist)

                    d2.insert(key,min(d1))
                    d1=[]
            d3.insert(j,min(d2))
            d2=[]
        d4.insert(k,min(d3))
    xmin=min(d4)
    dunn_index= xmin/xmax
    return dunn_index
