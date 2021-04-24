from __future__ import division
from decimal import *
import heapq
import random
import math
# from math import gcd
import numpy as np
import time

def workload_Init(l, node):
    c = []
    for i in range(l):
        c.append((node[i]['CPUCapacity'], node[i]['MemCapacity']))
    return c

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


def maxmin_Models(func, l, n, m, node):
    c = workload_Init(l, node)

    c_cpu_total = 0
    c_mem_total = 0
    for i in range(l):
        c_cpu_total += c[i][0]
        c_mem_total += c[i][1]
    # print("c_cpu_total: {}, c_mem_total: {}".format(c_cpu_total, c_mem_total))
    # exit("stop")

    cpu_maxmin_alloc, mem_maxmin_alloc = maxMinCalculation(func, c_cpu_total, c_mem_total)

    return cpu_maxmin_alloc, mem_maxmin_alloc