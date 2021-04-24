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


def scoreWorstFit(fIndex, fairnessDataList, availableReourcePerNode, remainingReourcePerNode):
    num = len(availableReourcePerNode)
    nodeScore = [0] * num
    # print("In scoreWorstFit, remainingReourcePerNode = {}".format(remainingReourcePerNode))
    for i in range(len(availableReourcePerNode)):
        if remainingReourcePerNode[i]['CPUCapacity'] > 0 and remainingReourcePerNode[i]['MemCapacity'] > 0:
            if remainingReourcePerNode[i]['CPUCapacity'] >= fairnessDataList[fIndex]['podCPUUsage'] and remainingReourcePerNode[i]['MemCapacity'] >= fairnessDataList[fIndex]['podMemUsage']:
                nodeScore[i] = (remainingReourcePerNode[i]['CPUCapacity'] - fairnessDataList[fIndex]['podCPUUsage']) / float(availableReourcePerNode[i]['CPUCapacity']) + \
                               (remainingReourcePerNode[i]['MemCapacity'] - fairnessDataList[fIndex]['podMemUsage']) / float(availableReourcePerNode[i]['MemCapacity'])
            else:
                nodeScore[i] = -1
        else:
            nodeScore[i] = -1
    return MaxFloatSlice(nodeScore)

def scoreAlignment(fIndex, fairnessDataList, availableReourcePerNode, remainingReourcePerNode):
    num = len(availableReourcePerNode)
    nodeScore = [0] * num
    # print("In scoreWorstFit, remainingReourcePerNode = {}".format(remainingReourcePerNode))
    for i in range(len(availableReourcePerNode)):
        if remainingReourcePerNode[i]['CPUCapacity'] > 0 and remainingReourcePerNode[i]['MemCapacity'] > 0:
            if remainingReourcePerNode[i]['CPUCapacity'] >= fairnessDataList[fIndex]['podCPUUsage'] and remainingReourcePerNode[i]['MemCapacity'] >= fairnessDataList[fIndex]['podMemUsage']:
                nodeScore[i] = (remainingReourcePerNode[i]['CPUCapacity'] * fairnessDataList[fIndex]['podCPUUsage']) / float(availableReourcePerNode[i]['CPUCapacity'] * availableReourcePerNode[i]['CPUCapacity']) + \
                               (remainingReourcePerNode[i]['MemCapacity'] * fairnessDataList[fIndex]['podMemUsage']) / float(availableReourcePerNode[i]['MemCapacity'] * availableReourcePerNode[i]['MemCapacity'])
            else:
                nodeScore[i] = -1
        else:
            nodeScore[i] = -1
    return MaxFloatSlice(nodeScore)

def scoreBerkeley(fIndex, fairnessDataList, availableReourcePerNode, remainingReourcePerNode):
    num = len(availableReourcePerNode)
    nodeScore = [0] * num
    # print("In scoreWorstFit, remainingReourcePerNode = {}".format(remainingReourcePerNode))
    for i in range(len(availableReourcePerNode)):
        if remainingReourcePerNode[i]['CPUCapacity'] > 0 and remainingReourcePerNode[i]['MemCapacity'] > 0:
            if remainingReourcePerNode[i]['CPUCapacity'] >= fairnessDataList[fIndex]['podCPUUsage'] and remainingReourcePerNode[i]['MemCapacity'] >= fairnessDataList[fIndex]['podMemUsage']:
                nodeScore[i] = (remainingReourcePerNode[i]['CPUCapacity'] - fairnessDataList[fIndex]['podCPUUsage']) / float(remainingReourcePerNode[i]['CPUCapacity']) + \
                               (remainingReourcePerNode[i]['MemCapacity'] - fairnessDataList[fIndex]['podMemUsage']) / float(remainingReourcePerNode[i]['MemCapacity'])
            else:
                nodeScore[i] = -1
        else:
            nodeScore[i] = -1
    return MaxFloatSlice(nodeScore)

def DRF_Var(func, availableReourcePerNode, clusterCPU, clusterMem, solverName):
    fairnessDataList = []
    remainingFunctions = len(func)
    for i in range(len(func)): # set the desiredCPU, desiredMem, and remainingPodCount
        tmp = {'desiredCPU': func[i]['podCPUUsage'] * func[i]['desiredPodCountSLO'], 'desiredMem': func[i]['podMemUsage'] * func[i]['desiredPodCountSLO'],
                'remainingPodCount': func[i]['desiredPodCountSLO'], 'allocatedCPUFair': 0, 'allocatedMemFair': 0, 'desiredPodCountSLO': func[i]['desiredPodCountSLO'],
                'podCPUUsage': func[i]['podCPUUsage'], 'podMemUsage': func[i]['podMemUsage'], 'placementDecision': []}
        fairnessDataList.append(tmp)
        if func[i]['desiredPodCountSLO'] == 0:
            remainingFunctions = remainingFunctions - 1

    # remainingReourcePerNode := make([]ResourceCapacity, len(availableReourcePerNode))
    remainingReourcePerNode = []
    for i in range(len(availableReourcePerNode)): # set the desiredCPU, desiredMem, and remainingPodCount
        tmp = {'CPUCapacity': 0.0, 'MemCapacity': 0.0}
        remainingReourcePerNode.append(tmp)

    for i in range(len(availableReourcePerNode)): # init the remainingReourcePerNode
        remainingReourcePerNode[i]['CPUCapacity'] = availableReourcePerNode[i]['CPUCapacity']
        remainingReourcePerNode[i]['MemCapacity'] = availableReourcePerNode[i]['MemCapacity']

    # for i in range(len(fairnessDataList)): # set the desiredCPU, desiredMem, and remainingPodCount
    #   fairnessDataList[i]['desiredCPU'] = fairnessDataList[i]['podCPUUsage'] * float64(fairnessDataList[i]['desiredPodCountSLO'])
    #   fairnessDataList[i]['desiredMem'] = fairnessDataList[i]['podMemUsage'] * float64(fairnessDataList[i]['desiredPodCountSLO'])
    #   fairnessDataList[i]['remainingPodCount'] = fairnessDataList[i]['desiredPodCountSLO']

    num = len(fairnessDataList) # Number of Functions
    placementCompleted = 0
    for i in range(len(fairnessDataList)):
        if fairnessDataList[i]['remainingPodCount'] <= 0:
            placementCompleted = placementCompleted + 1

    tick = time.time()
    while 1:
        # print("placementCompleted: ",placementCompleted)
        if placementCompleted == num:
            break

        domainShare = [0] * num
        for i in range(len(fairnessDataList)):
            if fairnessDataList[i]['remainingPodCount'] > 0:
                CPUShare = fairnessDataList[i]['allocatedCPUFair'] / float(clusterCPU)
                MemShare = fairnessDataList[i]['allocatedMemFair'] / float(clusterMem)
                domainShare[i] = max(CPUShare, MemShare)
            else:
                domainShare[i] = math.inf
        # print("domainShare: ",domainShare)
        minDominantShareVal, _null = MinFloatSlice(domainShare) # Find the min dominant share value
        totalDemand = [0] * num
        for i in range(len(domainShare)):
            if minDominantShareVal == domainShare[i]:
                totalDemand[i] = fairnessDataList[i]['desiredCPU'] + fairnessDataList[i]['desiredMem']
            else:
                totalDemand[i] = math.inf

        _null, funcIndex = MinFloatSlice(totalDemand)

        if solverName == "drf+worstfit":
            # find_node, node_index = score_worstfit(node_resource, l, required_resource, c)
            nodeScore, nodeIndex = scoreWorstFit(funcIndex, fairnessDataList, availableReourcePerNode, remainingReourcePerNode)
        elif solverName == "drf+alignment":
            # find_node, node_index = score_alignment(node_resource, l, required_resource, total_resource)
            nodeScore, nodeIndex = scoreAlignment(funcIndex, fairnessDataList, availableReourcePerNode, remainingReourcePerNode)
        elif solverName == "drf+berkeley":
            # find_node, node_index = score_berkeley(node_resource, l, required_resource)
            nodeScore, nodeIndex = scoreBerkeley(funcIndex, fairnessDataList, availableReourcePerNode, remainingReourcePerNode)
        else:
            print("wrong solverName")
            exit(1)

        if nodeScore == -1:
            fairnessDataList[funcIndex]['remainingPodCount'] = 0
            placementCompleted = placementCompleted + 1
            continue

        fairnessDataList[funcIndex]['allocatedCPUFair'] += fairnessDataList[funcIndex]['podCPUUsage']
        fairnessDataList[funcIndex]['allocatedMemFair'] += fairnessDataList[funcIndex]['podMemUsage']
        fairnessDataList[funcIndex]['remainingPodCount'] -= 1 
        fairnessDataList[funcIndex]['placementDecision'].append(nodeIndex)
        if fairnessDataList[funcIndex]['remainingPodCount'] <= 0:
            placementCompleted = placementCompleted + 1

        remainingReourcePerNode[nodeIndex]['CPUCapacity'] -= fairnessDataList[funcIndex]['podCPUUsage']
        remainingReourcePerNode[nodeIndex]['MemCapacity'] -= fairnessDataList[funcIndex]['podMemUsage']
        # print("fairnessDataList[{}]['placementDecision']: {}".format(1, fairnessDataList[1]['placementDecision']))
    delta = (time.time() - tick) * 1

    for i in range(len(fairnessDataList)): # set the desiredPodCountFair
        fairnessDataList[i]['desiredPodCountFair'] = int(math.ceil(fairnessDataList[i]['allocatedCPUFair'] / fairnessDataList[i]['podCPUUsage']))

    cpu_drf_alloc = [0] * len(fairnessDataList)
    mem_drf_alloc = [0] * len(fairnessDataList)
    for i in range(len(fairnessDataList)):
        cpu_drf_alloc[i] = fairnessDataList[i]['desiredPodCountFair'] * fairnessDataList[i]['podCPUUsage']
        mem_drf_alloc[i] = fairnessDataList[i]['desiredPodCountFair'] * fairnessDataList[i]['podMemUsage']
        # print("fairnessDataList[{}]['placementDecision']: {}".format(i, fairnessDataList[i]['placementDecision']))
    return cpu_drf_alloc, mem_drf_alloc, delta
