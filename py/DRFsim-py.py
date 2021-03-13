''' Simulator for Placement Engine '''
from __future__ import division
from decimal import *
from gurobipy import quicksum
import heapq
import gurobipy as gp
from gurobipy import GRB
import math
import sys
from model_def import LP_Models, workload_Init

solverName = sys.argv[1]

# Initialize input parameters
total_ticks = 30

l = 2 # total 2 nodes available
n = 4 # total 4 functions 
m = 2 # 2 kinds of resources

func_1 = {'desiredPodCountSLO': 6, 'podCPUUsage': 5.0, 'podMemUsage': 1.0, 'functionName': "fairnessData_1"}
func_2 = {'desiredPodCountSLO': 5, 'podCPUUsage': 1.0, 'podMemUsage': 5.0, 'functionName': "fairnessData_2"}
func_3 = {'desiredPodCountSLO': 5, 'podCPUUsage': 5.0, 'podMemUsage': 1.0, 'functionName': "fairnessData_3"}
func_4 = {'desiredPodCountSLO': 2, 'podCPUUsage': 1.0, 'podMemUsage': 1.0, 'functionName': "fairnessData_4"}
func_null = {'desiredPodCountSLO': 0, 'podCPUUsage': 1.0, 'podMemUsage': 1.0, 'functionName': "fairnessData_null"}

node_1 = {'CPUCapacity': 25, 'MemCapacity': 10}
node_2 = {'CPUCapacity': 10, 'MemCapacity': 25}
node = [node_1, node_2]

for clk in range(total_ticks):
    # Workload Initialization
    if clk >= 0 and clk < 3:
        func = [func_1, func_null, func_null, func_4]
    elif clk >= 3 and clk < 5:
        func = [func_1, func_2, func_null, func_4]
    elif clk >= 5 and clk < 10:
        func = [func_1, func_2, func_3, func_4]
    elif clk >= 10 and clk < 20:
        func = [func_1, func_null, func_3, func_4]
    elif clk >= 20 and clk < 25:
        func = [func_1, func_2, func_3, func_4]
    else:
        func = [func_1, func_2, func_null, func_4]

    # nr, resource_needed, dominant_resource, total_resource, required_uniform_share = workload_Init(func, l, n, m, node_1, node_2)
    # print(func)
    if solverName[0] == 'L' and solverName[1] == 'P':
        output  = LP_Models(func, l, n, m, node_1, node_2, solverName)
    elif solverName == 'maxmin':
        print("maxmin fairness")
        # output = maxmin_Models(func, l, n, m, node_1, node_2)
    # elif solverName[:3] == 'drf':
        # print("DRF algorithm")
    else:
        print('''
            Please select the correct model:
                LP1 LP2 LP3 maxmin
                drf+worstfit drf+alignment drf+berkeley
            ''')
        exit(1)
    print("placed_pods_list: ", output)
    
