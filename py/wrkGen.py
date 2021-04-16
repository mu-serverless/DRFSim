from __future__ import division
from decimal import *
import random
import math

'''
l: # of nodes
n: # of functions
m: types of resources
nr: the # of pods requested by each function
a: the resource demand of each pod

output:
[func_1, func_2, ..., func_1000]
func_$ = {'desiredPodCountSLO': 6, 'podCPUUsage': 5.0, 'podMemUsage': 1.0}

'''

def random_numbers(n, k, range_int, clk):
    """generate n numbers with sum k, random number in range_int, d is the demension"""
    random.seed(clk + 1)
    nums = [random.randint(range_int[0], range_int[1]) for i in range(n)]
    s = sum(nums)
    r_list = []
    for i in range(n-1):
        v = math.floor((nums[i]/s)*k)
        r_list.append(v)
    ss = sum(r_list)
    last_elem = k - ss
    r_list.append(last_elem)
    return r_list

def wrk_generator(l, n, m, clk):
    # l = 5  # total number of nodes available
    # n = 10 # total number of functions 
    # m = 2   # kinds of resources

    random.seed(clk) # change seed can generate different dataset
    nr = [random.randint(1, 16) for i in range(n)] # Initialize the number of pods requested by each function, pod number is between 1-16
    # print("required pods number by each functon:", nr)
    total_requested_pods = sum(nr)

    n1 = int(0.9 * n) # 90% percentage functions require less than 400m memory
    n2 = n - n1
    resource_needed1 = [[random.randint(1,8), (random.randint(1, 4))/10] for i in range(n1)] # CPU between 1-8, memory less 400m
    resource_needed2 = [[random.randint(1,8), (random.randint(5,20))/10] for i in range(n2)] # CPU between 1-8, memory between 500m-2G
    resource_needed = resource_needed1 + resource_needed2
    # print("pod resource requested by each function is ", resource_needed)

    # calculate the total requested resource for generating nodes resource
    total_requested_cpu = 0
    total_requested_mem = 0
    for i in range(n):
        total_requested_cpu += nr[i] * resource_needed[i][0]
        total_requested_mem += nr[i] * resource_needed[i][1]
    # print("total_requested_cpu:", total_requested_cpu, " total_requested_mem:", total_requested_mem, "\n") 

    fake_sum_cpu = int(total_requested_cpu * 0.8) # The total CPU in the cluster can only meet 80% of the demand
    upper_bound = int(fake_sum_cpu / l)
    lower_bound = int(upper_bound / 2)
    c_node_cpus = random_numbers(l, fake_sum_cpu, [lower_bound, upper_bound], clk) # generate random cpu number for each node, which satisfy the total CPU is 80% of the demand 
    fake_sum_mem = int(total_requested_mem * 0.6)# The total memory in the cluster can only meet 60% of the demand
    upper_bound2 = int(fake_sum_mem/l)
    lower_bound2 = int(upper_bound2/2)
    c_node_mems = random_numbers(l, fake_sum_mem, [lower_bound2, upper_bound2], clk) # generate random memory number for each node, which satisfy the total memory is 60% of the demand
    # print("cpu capacity: {}, mem capacity: {}".format(sum(c_node_cpus), sum(c_node_mems)))
    # print("cpu capacity: {}, mem capacity: {}".format(c_node_cpus, c_node_mems))

    # Formatting node resource capacity
    node = []
    for i in range(len(c_node_cpus)):
        tmp = {'CPUCapacity': c_node_cpus[i], 'MemCapacity': c_node_mems[i]}
        node.append(tmp)

    # Formatting function resource demand
    func = []
    for i in range(n):
        tmp = {'desiredPodCountSLO': nr[i], 'podCPUUsage': resource_needed[i][0], 'podMemUsage': resource_needed[i][1]}
        func.append(tmp)

    return node, func
