from __future__ import division
from decimal import *
import heapq
import random
import math
# from math import gcd
import numpy as np
import time

def MinFloatSlice(a):
    min_a = a[0]
    index = 0
    for i in range(len(a)):
        if min_a > a[i]:
            min_a = a[i]
            index = i

    return min_a, index


def MaxFloatSlice(a):
    max_a = a[0]
    index = 0
    for i in range(len(a)):
        if max_a < a[i]:
            max_a = a[i]
            index = i

    return max_a, index

def leastResourceScorer(resToWeightMap resourceToWeightMap)::
    nodeScore = 0
    weightSum = 0
    for resource, weight in resToWeightMap:
        resourceScore = leastRequestedScore(requested[resource], allocable[resource])
        nodeScore += resourceScore * weight
        weightSum += weight
    
    return nodeScore / weightSum

# The unused capacity is calculated on a scale of 0-MaxNodeScore
# 0 being the lowest priority and `MaxNodeScore` being the highest.
# The more unused resources the higher the score is.
def leastRequestedScore(requested, capacity):
    if capacity == 0:
        return 0
    
    if requested > capacity:
        return 0

    return ((capacity - requested) * int(framework.MaxNodeScore)) / capacity

def fractionOfCapacity(requested, capacity):
    if capacity == 0:
        return 1
    
    return float(requested) / float(capacity)

def balancedResourceScorer(requested, allocable):
    cpuFraction = fractionOfCapacity(requested["ResourceCPU"], allocable["ResourceCPU"])
    memoryFraction = fractionOfCapacity(requested["ResourceMemory"], allocable["ResourceMemory"])
    
    # This to find a node which has most balanced CPU, memory and volume usage.
    if cpuFraction >= 1 or memoryFraction >= 1:
        # if requested >= capacity, the corresponding host should never be preferred.
        return 0

    # Upper and lower boundary of difference between cpuFraction and memoryFraction are -1 and 1
    # respectively. Multiplying the absolute value of the difference by `MaxNodeScore` scales the value to
    # 0-MaxNodeScore with 0 representing well balanced allocation and `MaxNodeScore` poorly balanced. Subtracting it from
    # `MaxNodeScore` leads to the score which also scales from 0 to `MaxNodeScore` while `MaxNodeScore` representing well balanced.
    diff = math.Abs(cpuFraction - memoryFraction)
    return 1 - diff

def DRF_Var(func, availableReourcePerNode, clusterCPU, clusterMem, solverName):

    return cpu_drf_alloc, mem_drf_alloc
