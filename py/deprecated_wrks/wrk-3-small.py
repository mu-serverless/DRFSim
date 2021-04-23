''' Simulator for Placement Engine '''
from __future__ import division
from decimal import *
import math
import sys, time
from lp_model_def import LP_Models
from efficient_model import Efficient_Models
from maxmin_model_def import maxmin_Models
from var_drf_def import DRF_Var

solverName = sys.argv[1]

# Initialize input parameters
total_ticks = 30

l = 2 # total 2 nodes available
n = 4 # total 4 functions 
m = 2 # 2 kinds of resources

func_1 = {'desiredPodCountSLO': 6, 'podCPUUsage': 5.0, 'podMemUsage': 3.0, 'functionName': "fairnessData_1"}
func_2 = {'desiredPodCountSLO': 5, 'podCPUUsage': 2.0, 'podMemUsage': 5.0, 'functionName': "fairnessData_2"}
func_3 = {'desiredPodCountSLO': 5, 'podCPUUsage': 4.0, 'podMemUsage': 1.0, 'functionName': "fairnessData_3"}
func_4 = {'desiredPodCountSLO': 2, 'podCPUUsage': 2.0, 'podMemUsage': 2.0, 'functionName': "fairnessData_4"}
func_null = {'desiredPodCountSLO': 0, 'podCPUUsage': 0.01, 'podMemUsage': 0.01, 'functionName': "fairnessData_null"}
# func_null = {'desiredPodCountSLO': 0, 'podCPUUsage': 0, 'podMemUsage': 0, 'functionName': "fairnessData_null"}

node_1 = {'CPUCapacity': 25, 'MemCapacity': 15}
node_2 = {'CPUCapacity': 20, 'MemCapacity': 10}
node = [node_1, node_2]

delta = []
for clk in range(total_ticks):
    if clk >= 0 and clk < 3: # Workload Initialization
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
        print("[t = {}] cpu_lp_alloc: {} \tmem_lp_alloc: {}".format(clk, cpu_lp_alloc, mem_lp_alloc))
    elif solverName == 'maxmin':
        # output = maxmin_Models(func, l, n, m, node_1, node_2)
        cpu_maxmin_alloc, mem_maxmin_alloc = maxmin_Models(func, l, n, m, node)
        print("[t = {}] cpu_maxmin_alloc: {} \tmem_maxmin_alloc: {}".format(clk, cpu_maxmin_alloc, mem_maxmin_alloc))
    elif solverName[:3] == 'drf':
        # print("DRF algorithm")
        # print("\n============== {} cycle =============".format(clk))
        tick = time.time()
        cpu_drf_alloc, mem_drf_alloc = DRF_Var(func, node, 35, 35, solverName)
        delta.append((time.time() - tick) * 1000000)
        # print("Execution time of {}: {} us".format(solverName, (time.time() - tick) * 1000000))
        # exit("Stop at the 1st cycle")
        print("[t = {}] cpu_drf_alloc: {} \tmem_drf_alloc: {}".format(clk, cpu_drf_alloc, mem_drf_alloc))
    elif solverName == 'efficient':
        tick = time.time()
        output = Efficient_Models(func, l, n, m, node)
        delta.append((time.time() - tick) * 1000000)
        cpu_lp_alloc = [0] * len(output) 
        mem_lp_alloc = [0] * len(output)
        for i in range(len(output)):
            cpu_lp_alloc[i] = output[i] * func[i]['podCPUUsage']
            mem_lp_alloc[i] = output[i] * func[i]['podMemUsage']
        print("[t = {}] cpu_lp_alloc: {} \tmem_lp_alloc: {}".format(clk, cpu_lp_alloc, mem_lp_alloc))
        # print("cpu_lp_alloc: {}".format(cpu_lp_alloc))
        # print("mem_lp_alloc: {}".format(mem_lp_alloc))
        # print("[t = {}] output: {}".format(clk, output))
        cpu_slo = [0] * len(output)
        mem_slo = [0] * len(output)
        for i in range(len(output)):
            cpu_slo[i] = func[i]['desiredPodCountSLO'] * func[i]['podCPUUsage']
            mem_slo[i] = func[i]['desiredPodCountSLO'] * func[i]['podMemUsage']
        # print("[t = {}] cpu_slo: {} \tmem_slo: {}".format(clk, cpu_slo, mem_slo))
        remaining_cpu = 35 - sum(cpu_lp_alloc)
        remaining_mem = 35 - sum(mem_lp_alloc)
        unmet_cpu = [0] * len(output)
        unmet_mem = [0] * len(output)
        for i in range(len(output)):
            unmet_cpu[i] = cpu_slo[i] - cpu_lp_alloc[i]
            unmet_mem[i] = mem_slo[i] - mem_lp_alloc[i]
        # print("[t = {}] remaining_cpu: {} \tremaining_mem: {}".format(clk, remaining_cpu, remaining_mem))
        # print("[t = {}] unmet_cpu: {} \tunmet_mem: {}".format(clk, unmet_cpu, unmet_mem))
        # print("")
    else:
        print('''
            Please select the correct model:
                LP1 LP2 LP3 maxmin
                drf+worstfit drf+alignment drf+berkeley
            ''')
        exit(1)
    # print("[t = {}] placed_pods_list: {}".format(clk, output))
# print("Average completion time (us): ", sum(delta)/len(delta))
