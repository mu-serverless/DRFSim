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
total_ticks = 1

l = 40 # total 40 nodes available
# n = 100 * l / 4 * 2  # total 4 functions 
n = 100
m = 2 # 2 kinds of resources

func_1 = {'desiredPodCountSLO': 6, 'podCPUUsage': 5.0, 'podMemUsage': 1.0, 'functionName': "fairnessData_1"}
func_2 = {'desiredPodCountSLO': 5, 'podCPUUsage': 1.0, 'podMemUsage': 5.0, 'functionName': "fairnessData_2"}
func_3 = {'desiredPodCountSLO': 5, 'podCPUUsage': 5.0, 'podMemUsage': 1.0, 'functionName': "fairnessData_3"}
func_4 = {'desiredPodCountSLO': 2, 'podCPUUsage': 1.0, 'podMemUsage': 1.0, 'functionName': "fairnessData_4"}
func_null = {'desiredPodCountSLO': 0, 'podCPUUsage': 0.01, 'podMemUsage': 0.01, 'functionName': "fairnessData_null"}
# func_null = {'desiredPodCountSLO': 0, 'podCPUUsage': 0, 'podMemUsage': 0, 'functionName': "fairnessData_null"}

if n == 100:
    scale = 1 # 100 functions
elif n == 200:
    scale = 2 # 200 functions
elif n == 400:
    scale = 4
elif n == 800:
    scale = 8
elif n == 1600:
    scale = 16
elif n == 3200:
    scale = 32
elif n == 6400:
    scale = 64 # 6400 functions
else:
    scale = 1
    exit("n is not allowed")

node_1 = {'CPUCapacity': 25 * scale, 'MemCapacity': 10 * scale}
node_2 = {'CPUCapacity': 10 * scale, 'MemCapacity': 25 * scale}
cpu = node_1['CPUCapacity'] + node_2['CPUCapacity']
mem = node_1['MemCapacity'] + node_2['MemCapacity']

node = [node_1, node_2] * int(l / 2)

delta = []
for clk in range(total_ticks):

    func = [func_1, func_2, func_3, func_4] * int(n / 4)
    
    if solverName[0] == 'L' and solverName[1] == 'P':
        tick = time.time()
        output  = LP_Models(func, l, n, m, node, solverName)
        delta.append((time.time() - tick) * 1000000)
        # print("Execution time of {}: {} us".format(solverName, (time.time() - tick) * 1000000))
        cpu_lp_alloc = [0] * len(output) 
        mem_lp_alloc = [0] * len(output)
        for i in range(len(output)):
            cpu_lp_alloc[i] = output[i] * func[i]['podCPUUsage']
            mem_lp_alloc[i] = output[i] * func[i]['podMemUsage']
        # print("[t = {}] placed_pods_list: {}".format(clk, output))
        # print("[t = {}] cpu_lp_alloc: {} \tmem_lp_alloc: {}".format(clk, cpu_lp_alloc, mem_lp_alloc))
    elif solverName == 'maxmin':
        tick = time.time()
        cpu_maxmin_alloc, mem_maxmin_alloc = maxmin_Models(func, l, n, m, node)
        delta.append((time.time() - tick) * 1000000)
        # print("[t = {}] cpu_maxmin_alloc: {} \tmem_maxmin_alloc: {}".format(clk, cpu_maxmin_alloc, mem_maxmin_alloc))
    elif solverName[:3] == 'drf':
        # print("DRF algorithm")
        # print("\n============== {} cycle =============".format(clk))
        tick = time.time()
        # cpu_drf_alloc, mem_drf_alloc = DRF_Var(func, node, (25 + 10) * l / 2, (10 + 25) * l / 2, solverName)
        cpu_drf_alloc, mem_drf_alloc = DRF_Var(func, node, cpu * l / 2, mem * l / 2, solverName)
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
print("Average completion time (milisecond): ", sum(delta)/len(delta))
