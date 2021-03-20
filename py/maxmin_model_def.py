from __future__ import division
from decimal import *
import heapq
import random
import math
from math import gcd
import numpy as np
import time

def workload_Init(func, l, n, m, node_1, node_2):
    nr = []
    resource_needed = []
    for i in range(n):
        nr.append(func[i]['desiredPodCountSLO'])
        resource_needed.append([func[i]['podCPUUsage'], func[i]['podMemUsage']])
    # print("required pods number by each functon:", nr)
    # print("pod resource requested by each function is ", resource_needed)
    total_requested_pods = sum(nr)
    a = [([resource_needed[i]] *(nr[i])) for i in range(n)] # Initialize the resource request of each Pod
    # print("pod resource requested for each function is ", a)

    c = list(zip([node_1['CPUCapacity'], node_2['CPUCapacity']], [node_1['MemCapacity'], node_2['MemCapacity']]))# combine cpu and memory to initailize the resource capacity of each node
    # print("resource on each node is ", c)

    c_cpu_total = 0
    c_mem_total = 0
    for i in range(l):
        c_cpu_total += c[i][0]
        c_mem_total += c[i][1]
    # print("total cpu is: ", c_cpu_total)
    # print("total mem is: ", c_mem_total)
    total_resource = [c_cpu_total, c_mem_total]
    dominant_resource = [] # first is the amount of required dominant resource, second is the total resource for that type of resource
    dominant_resource_flags = [] # 0 is cpu, 1 is memory
    minimum_dominant_resource = [resource_needed[0][0], c_cpu_total] # first is the amount of required dominant resource, second is total resource for that type of resource
    nodes_remainings = c[:]

    for i in range(n): # calculate the dominant resource for each function
        cpu_share = resource_needed[i][0]/c_cpu_total
        mem_share = resource_needed[i][1]/c_mem_total
        if (cpu_share >= mem_share):
            dominant_resource_flags.append(0)
            dominant_resource.append([resource_needed[i][0], c_cpu_total])    
            if minimum_dominant_resource[0]/minimum_dominant_resource[1] > cpu_share:
                minimum_dominant_resource = [resource_needed[i][0], c_cpu_total]
        else:
            dominant_resource_flags.append(1)
            dominant_resource.append([resource_needed[i][1], c_mem_total])
            if minimum_dominant_resource[0]/minimum_dominant_resource[1] > mem_share:
                minimum_dominant_resource = [resource_needed[i][1], c_mem_total]

    # Calcuate dr for each function
    required_uniform_share = []
    for i in range(n):
        required_uniform_share.append((dominant_resource[i][0] * minimum_dominant_resource[1])/(dominant_resource[i][1] * minimum_dominant_resource[0]))

    return a, nr, c, resource_needed, dominant_resource, total_resource, required_uniform_share, nodes_remainings

def maxMinCalculation(func, clusterCPUAvailable, clusterMemAvailable):
    fairnessDataList_CPU = []
    remainingFunctions = len(func)
    for i in range(len(func)): # set the desiredCPU, desiredMem, and remainingPodCount
        tmp = {'desiredCPU': func[i]['podCPUUsage'] * func[i]['desiredPodCountSLO'], 'remainingPodCount': func[i]['desiredPodCountSLO'], 'allocatedCPUFair': 0}
        fairnessDataList_CPU.append(tmp)
        if func[i]['desiredPodCountSLO'] == 0:
            remainingFunctions = remainingFunctions - 1
    # print("func: {}".format(func))
    # print("fairnessDataList_CPU: {}".format(fairnessDataList_CPU))
    remainingCPU = clusterCPUAvailable
    while remainingFunctions > 0:
        # print("remainingCPU = ", remainingCPU)
        # print("remainingFunctions = ", remainingFunctions)
        if remainingCPU < 0.01:
            break
        # time.sleep(1)
        fairShareCPU = remainingCPU / float(remainingFunctions)
        for i in range(len(fairnessDataList_CPU)):
            if fairnessDataList_CPU[i]['desiredCPU'] - fairnessDataList_CPU[i]['allocatedCPUFair'] > 0 and fairnessDataList_CPU[i]['remainingPodCount'] > 0: # Need CPU
                if fairnessDataList_CPU[i]['desiredCPU'] - fairnessDataList_CPU[i]['allocatedCPUFair'] <= fairShareCPU:
                    fairnessDataList_CPU[i]['remainingPodCount'] = 0
                    remainingCPU = remainingCPU - (fairnessDataList_CPU[i]['desiredCPU'] - fairnessDataList_CPU[i]['allocatedCPUFair'])
                    fairnessDataList_CPU[i]['allocatedCPUFair'] = fairnessDataList_CPU[i]['allocatedCPUFair'] + (fairnessDataList_CPU[i]['desiredCPU'] - fairnessDataList_CPU[i]['allocatedCPUFair'])
                    remainingFunctions = remainingFunctions - 1
                    # print("func-{}: ".format(i))
                else:
                    fairnessDataList_CPU[i]['allocatedCPUFair'] = fairnessDataList_CPU[i]['allocatedCPUFair'] + fairShareCPU
                    remainingCPU = remainingCPU - fairShareCPU
            # print("func-{}: allocatedCPU: {}\tremainingCPU = {}".format(i, fairnessDataList_CPU[i]['allocatedCPUFair'], remainingCPU))

    remainingFunctions = len(func)
    fairnessDataList_MEM = []
    for i in range(len(func)): # set the desiredCPU, desiredMem, and remainingPodCount
        tmp = {'desiredMem': func[i]['podMemUsage'] * func[i]['desiredPodCountSLO'], 'remainingPodCount': func[i]['desiredPodCountSLO'], 'allocatedMemFair': 0}
        fairnessDataList_MEM.append(tmp)
        if func[i]['desiredPodCountSLO'] == 0:
            remainingFunctions = remainingFunctions - 1
    # print("fairnessDataList_MEM: {}".format(fairnessDataList_MEM))
    remainingMem = clusterMemAvailable
    while remainingFunctions > 0:
        # print("remainingMem = ", remainingMem)
        # print("remainingFunctions = ", remainingFunctions)
        if remainingMem < 0.01:
            break
        fairShareMem = remainingMem / float(remainingFunctions)
        for i in range(len(fairnessDataList_MEM)):
            if fairnessDataList_MEM[i]['desiredMem'] - fairnessDataList_MEM[i]['allocatedMemFair'] > 0 and fairnessDataList_MEM[i]['remainingPodCount'] > 0: # Need CPU
                if fairnessDataList_MEM[i]['desiredMem'] - fairnessDataList_MEM[i]['allocatedMemFair'] <= fairShareMem:
                    fairnessDataList_MEM[i]['remainingPodCount'] = 0
                    remainingMem = remainingMem - (fairnessDataList_MEM[i]['desiredMem'] - fairnessDataList_MEM[i]['allocatedMemFair'])
                    fairnessDataList_MEM[i]['allocatedMemFair'] = fairnessDataList_MEM[i]['allocatedMemFair'] + (fairnessDataList_MEM[i]['desiredMem'] - fairnessDataList_MEM[i]['allocatedMemFair'])
                    remainingFunctions = remainingFunctions - 1
                else:
                    fairnessDataList_MEM[i]['allocatedMemFair'] = fairnessDataList_MEM[i]['allocatedMemFair'] + fairShareMem
                    remainingMem = remainingMem - fairShareMem
            # print("func-{}: allocatedCPU: {}\tremainingMem = {}".format(i, fairnessDataList_MEM[i]['allocatedMemFair'], remainingMem))

    maxMinCPUValue = []
    maxMinMemValue = []
    for i in range(len(func)):
        maxMinCPUValue.append(fairnessDataList_CPU[i]['allocatedCPUFair'])
        maxMinMemValue.append(fairnessDataList_MEM[i]['allocatedMemFair'])
    return maxMinCPUValue, maxMinMemValue


def maxmin_Models(func, l, n, m, node_1, node_2):
    a, nr, c, resource_needed, dominant_resource, total_resource, required_uniform_share, nodes_remainings = workload_Init(func, l, n, m, node_1, node_2)

    c_cpu_total = 0
    c_mem_total = 0
    for i in range(l):
        c_cpu_total += c[i][0]
        c_mem_total += c[i][1]
    # print("c_cpu_total: {}, c_mem_total: {}".format(c_cpu_total, c_mem_total))
    # exit("stop")

    cpu_maxmin_alloc, mem_maxmin_alloc = maxMinCalculation(func, c_cpu_total, c_mem_total)

    return cpu_maxmin_alloc, mem_maxmin_alloc