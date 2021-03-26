''' Simulator for Placement Engine '''
from __future__ import division
from decimal import *
import math
import sys, time
from lp_model_def import LP_Models
from maxmin_model_def import maxmin_Models
from var_drf_def import DRF_Var

solverName = sys.argv[1]

# Initialize input parameters
total_ticks = 30

l = 40 # total 40 nodes available
n = 100 * l # total 4 functions 
m = 2 # 2 kinds of resources

func_1 = {'desiredPodCountSLO': 6, 'podCPUUsage': 5.0, 'podMemUsage': 1.0, 'functionName': "fairnessData_1"}
func_2 = {'desiredPodCountSLO': 5, 'podCPUUsage': 1.0, 'podMemUsage': 5.0, 'functionName': "fairnessData_2"}
func_3 = {'desiredPodCountSLO': 5, 'podCPUUsage': 5.0, 'podMemUsage': 1.0, 'functionName': "fairnessData_3"}
func_4 = {'desiredPodCountSLO': 2, 'podCPUUsage': 1.0, 'podMemUsage': 1.0, 'functionName': "fairnessData_4"}
func_null = {'desiredPodCountSLO': 0, 'podCPUUsage': 0.01, 'podMemUsage': 0.01, 'functionName': "fairnessData_null"}
# func_null = {'desiredPodCountSLO': 0, 'podCPUUsage': 0, 'podMemUsage': 0, 'functionName': "fairnessData_null"}

node_1 = {'CPUCapacity': 25, 'MemCapacity': 10}
node_2 = {'CPUCapacity': 10, 'MemCapacity': 25}
node = [node_1, node_2, node_1, node_2, node_1, node_2, node_1, node_2,
        node_1, node_2, node_1, node_2, node_1, node_2, node_1, node_2,
        node_1, node_2, node_1, node_2, node_1, node_2, node_1, node_2,
        node_1, node_2, node_1, node_2, node_1, node_2, node_1, node_2,
        node_1, node_2, node_1, node_2, node_1, node_2, node_1, node_2]

delta = []
for clk in range(total_ticks):

    func = [func_1, func_2, func_3, func_4] * 25 * l
    
    if solverName[0] == 'L' and solverName[1] == 'P':
        tick = time.time()
        output  = LP_Models(func, l, n, m, node, solverName)
        delta.append((time.time() - tick) * 1000000)
        # print("Execution time of {}: {} us".format(solverName, (time.time() - tick) * 1000000))
        # print("[t = {}] placed_pods_list: {}".format(clk, output))
    elif solverName == 'maxmin':
        # output = maxmin_Models(func, l, n, m, node_1, node_2)
        cpu_maxmin_alloc, mem_maxmin_alloc = maxmin_Models(func, l, n, m, node_1, node_2)
        print("[t = {}] cpu_maxmin_alloc: {} \tmem_maxmin_alloc: {}".format(clk, cpu_maxmin_alloc, mem_maxmin_alloc))
    elif solverName[:3] == 'drf':
        # print("DRF algorithm")
        # print("\n============== {} cycle =============".format(clk))
        tick = time.time()
        cpu_drf_alloc, mem_drf_alloc = DRF_Var(func, node, 280, 280, solverName)
        delta.append((time.time() - tick) * 1000000)
        # print("Execution time of {}: {} us".format(solverName, (time.time() - tick) * 1000000))
        # exit("Stop at the 1st cycle")
        # print("[t = {}] cpu_drf_alloc: {} \tmem_drf_alloc: {}".format(clk, cpu_drf_alloc, mem_drf_alloc))
    else:
        print('''
            Please select the correct model:
                LP1 LP2 LP3 maxmin
                drf+worstfit drf+alignment drf+berkeley
            ''')
        exit(1)
    # print("[t = {}] placed_pods_list: {}".format(clk, output))
print("Average completion time (us): ", sum(delta)/len(delta))
