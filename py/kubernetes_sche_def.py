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

# The unused capacity is calculated on a scale of 0-MaxNodeScore
# 0 being the lowest priority and `MaxNodeScore` being the highest.
# The more unused resources the higher the score is.
def leastRequestedScore(req, cap):
    if cap == 0:
        return 0
    if req > cap:
        return 0
    return float(cap - req) / float(cap)

def leastResourceScore(requested, allocable):
    cpuScore = leastRequestedScore(requested['podCPUUsage'], allocable['CPUCapacity'])
    memScore = leastRequestedScore(requested['podMemUsage'], allocable['MemCapacity'])
    nodeScore = cpuScore + memScore
    return float(nodeScore / 2)

def fractionOfCapacity(requested, capacity):
    if capacity == 0:
        return 1
    return float(requested) / float(capacity)

def balancedResourceScorer(requested, allocable):
    cpuFraction = fractionOfCapacity(requested['podCPUUsage'], allocable['CPUCapacity'])
    memFraction = fractionOfCapacity(requested['podMemUsage'], allocable['MemCapacity'])
    
    # This to find a node which has most balanced CPU, memory and volume usage.
    if cpuFraction > 1 or memFraction > 1:
        # if requested >= capacity, the corresponding host should never be preferred.
        return 0

    # Upper and lower boundary of difference between cpuFraction and memFraction are -1 and 1
    # respectively. Multiplying the absolute value of the difference by `MaxNodeScore` scales the value to
    # 0-MaxNodeScore with 0 representing well balanced allocation and `MaxNodeScore` poorly balanced. Subtracting it from
    # `MaxNodeScore` leads to the score which also scales from 0 to `MaxNodeScore` while `MaxNodeScore` representing well balanced.
    diff = abs(cpuFraction - memFraction)
    return (1 - diff)

def nodeScoring(fIndex, fairnessDataList, availableReourcePerNode, remainingReourcePerNode):
    num = len(availableReourcePerNode)
    nodeScore = [0] * num

    for i in range(len(availableReourcePerNode)):
        if remainingReourcePerNode[i]['CPUCapacity'] > 0 and remainingReourcePerNode[i]['MemCapacity'] > 0:
            if remainingReourcePerNode[i]['CPUCapacity'] >= fairnessDataList[fIndex]['podCPUUsage'] and remainingReourcePerNode[i]['MemCapacity'] >= fairnessDataList[fIndex]['podMemUsage']:
                # nodeScore[i] = (remainingReourcePerNode[i]['CPUCapacity'] - fairnessDataList[fIndex]['podCPUUsage']) / float(remainingReourcePerNode[i]['CPUCapacity']) + \
                               # (remainingReourcePerNode[i]['MemCapacity'] - fairnessDataList[fIndex]['podMemUsage']) / float(remainingReourcePerNode[i]['MemCapacity'])
                score1 = balancedResourceScorer(fairnessDataList[fIndex], remainingReourcePerNode[i])
                score2 = leastResourceScore(fairnessDataList[fIndex], remainingReourcePerNode[i])
                nodeScore[i] = score1 + score2
            else:
                nodeScore[i] = -1
        else:
            nodeScore[i] = -1
    return MaxFloatSlice(nodeScore)

def Kubernetes_sche(func, availableReourcePerNode):
    fairnessDataList = []
    remainingFunctions = len(func)
    for i in range(len(func)): # set the desiredCPU, desiredMem, and remainingPodCount
        tmp = {'desiredCPU': func[i]['podCPUUsage'] * func[i]['desiredPodCountSLO'], 'desiredMem': func[i]['podMemUsage'] * func[i]['desiredPodCountSLO'],
                'remainingPodCount': func[i]['desiredPodCountSLO'], 'allocatedCPUFair': 0, 'allocatedMemFair': 0, 'desiredPodCountSLO': func[i]['desiredPodCountSLO'],
                'podCPUUsage': func[i]['podCPUUsage'], 'podMemUsage': func[i]['podMemUsage'], 'placementDecision': []}
        fairnessDataList.append(tmp)
        if func[i]['desiredPodCountSLO'] == 0:
            remainingFunctions = remainingFunctions - 1

    remainingReourcePerNode = []
    for i in range(len(availableReourcePerNode)): # set the desiredCPU, desiredMem, and remainingPodCount
        tmp = {'CPUCapacity': 0.0, 'MemCapacity': 0.0}
        remainingReourcePerNode.append(tmp)
    for i in range(len(availableReourcePerNode)): # init the remainingReourcePerNode
        remainingReourcePerNode[i]['CPUCapacity'] = availableReourcePerNode[i]['CPUCapacity']
        remainingReourcePerNode[i]['MemCapacity'] = availableReourcePerNode[i]['MemCapacity']

    # num = len(fairnessDataList) # Number of Functions
    # placementCompleted = 0
    # for i in range(len(fairnessDataList)):
    #     if fairnessDataList[i]['remainingPodCount'] <= 0:
    #         placementCompleted = placementCompleted + 1

    # Placement logic
    for funcIndex in range(len(func)):
        for podIndex in range(fairnessDataList[funcIndex]['desiredPodCountSLO']):
            nodeScore, nodeIndex = nodeScoring(funcIndex, fairnessDataList, availableReourcePerNode, remainingReourcePerNode)
            if nodeScore == -1:
                continue
            fairnessDataList[funcIndex]['allocatedCPUFair'] += fairnessDataList[funcIndex]['podCPUUsage']
            fairnessDataList[funcIndex]['allocatedMemFair'] += fairnessDataList[funcIndex]['podMemUsage']
            # fairnessDataList[funcIndex]['remainingPodCount'] -= 1
            fairnessDataList[funcIndex]['placementDecision'].append(nodeIndex)
            # if fairnessDataList[funcIndex]['remainingPodCount'] <= 0:
                # placementCompleted = placementCompleted + 1

            remainingReourcePerNode[nodeIndex]['CPUCapacity'] -= fairnessDataList[funcIndex]['podCPUUsage']
            remainingReourcePerNode[nodeIndex]['MemCapacity'] -= fairnessDataList[funcIndex]['podMemUsage']
    # Allocation results
    # for i in range(len(fairnessDataList)): # set the desiredPodCountFair
        # fairnessDataList[i]['desiredPodCountFair'] = int(math.ceil(fairnessDataList[i]['allocatedCPUFair'] / fairnessDataList[i]['podCPUUsage']))

    cpu_drf_alloc = [0] * len(fairnessDataList)
    mem_drf_alloc = [0] * len(fairnessDataList)
    for i in range(len(fairnessDataList)):
        cpu_drf_alloc[i] = fairnessDataList[i]['allocatedCPUFair']
        mem_drf_alloc[i] = fairnessDataList[i]['allocatedMemFair']
        # print("fairnessDataList[{}]['placementDecision']: {}".format(i, fairnessDataList[i]['placementDecision']))
    return cpu_drf_alloc, mem_drf_alloc
