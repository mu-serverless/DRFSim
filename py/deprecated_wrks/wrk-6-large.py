''' Simulator for Placement Engine '''
from __future__ import division
from decimal import *
import math
import sys, time
from lp_model_def import LP_Models
from efficient_model import Efficient_Models
from maxmin_model_def import maxmin_Models
from var_drf_def import DRF_Var

# solverName = sys.argv[1]

# Initialize input parameters
total_ticks = 30

l = 40 # total 40 nodes available
# n = 100 * l / 4 * 2  # total 4 functions 
n = 100
m = 2 # 2 kinds of resources

func_1 = {'desiredPodCountSLO': 6, 'podCPUUsage': 5.0, 'podMemUsage': 1.0, 'functionName': "fairnessData_1"}
func_2 = {'desiredPodCountSLO': 5, 'podCPUUsage': 1.0, 'podMemUsage': 5.0, 'functionName': "fairnessData_2"}
func_3 = {'desiredPodCountSLO': 5, 'podCPUUsage': 5.0, 'podMemUsage': 1.0, 'functionName': "fairnessData_3"}
func_4 = {'desiredPodCountSLO': 2, 'podCPUUsage': 5.0, 'podMemUsage': 5.0, 'functionName': "fairnessData_4"}
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

node_1 = {'CPUCapacity': 50 * scale, 'MemCapacity': 20 * scale}
node_2 = {'CPUCapacity': 20 * scale, 'MemCapacity': 50 * scale}
cpu = node_1['CPUCapacity'] + node_2['CPUCapacity']
mem = node_1['MemCapacity'] + node_2['MemCapacity']

node = [node_1, node_2] * int(l / 2)

delta = []
algs = ['maxmin', 'drf+worstfit', 'drf+berkeley', 'drf+alignment'] 
# algs = ['maxmin'] 
maxmin_cpu_result = []
maxmin_mem_result = []
drf_worstfit_cpu_result = []
drf_worstfit_mem_result = []
drf_berkeley_cpu_result = []
drf_berkeley_mem_result = []
drf_alignment_cpu_result = []
drf_alignment_mem_result = []
lp1_cpu_result = []
lp1_mem_result = []
lp2_cpu_result = []
lp2_mem_result = []
efficient_cpu_result = []
efficient_mem_result = []
for solverName in algs:
    for clk in range(total_ticks):
        if clk >= 0 and clk < 3: # Workload Initialization
            func = [func_1, func_null, func_null, func_4] * int(n / 4)
        elif clk >= 3 and clk < 5:
            func = [func_1, func_2, func_null, func_4] * int(n / 4)
        elif clk >= 5 and clk < 10:
            func = [func_1, func_2, func_3, func_4] * int(n / 4)
        elif clk >= 10 and clk < 20:
            func = [func_1, func_null, func_3, func_4] * int(n / 4)
        elif clk >= 20 and clk < 25:
            func = [func_1, func_2, func_3, func_4] * int(n / 4)
        else:
            func = [func_1, func_2, func_null, func_4] * int(n / 4)

        # func = [func_1, func_2, func_3, func_4] * int(n / 4)
        
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
            if solverName == 'LP1':
                lp1_cpu_result.append(cpu_lp_alloc)
                lp1_mem_result.append(mem_lp_alloc)
            elif solverName == 'LP2':
                lp2_cpu_result.append(cpu_lp_alloc)
                lp2_mem_result.append(mem_lp_alloc)

        elif solverName == 'maxmin':
            tick = time.time()
            cpu_maxmin_alloc, mem_maxmin_alloc = maxmin_Models(func, l, n, m, node)
            delta.append((time.time() - tick) * 1000000)
            # print("[t = {}] cpu_maxmin_alloc: {} \tmem_maxmin_alloc: {}".format(clk, cpu_maxmin_alloc, mem_maxmin_alloc))
            maxmin_cpu_result.append(cpu_maxmin_alloc)
            maxmin_mem_result.append(mem_maxmin_alloc)

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
            if solverName == 'drf+worstfit':
                drf_worstfit_cpu_result.append(cpu_drf_alloc)
                drf_worstfit_mem_result.append(mem_drf_alloc)
            elif solverName == 'drf+berkeley':
                drf_berkeley_cpu_result.append(cpu_drf_alloc)
                drf_berkeley_mem_result.append(mem_drf_alloc)
            elif solverName == 'drf+alignment':
                drf_alignment_cpu_result.append(cpu_drf_alloc)
                drf_alignment_mem_result.append(mem_drf_alloc)

        elif solverName == 'efficient':
            tick = time.time()
            output = Efficient_Models(func, l, n, m, node)
            delta.append((time.time() - tick) * 1000000)
            cpu_lp_alloc = [0] * len(output) 
            mem_lp_alloc = [0] * len(output)
            for i in range(len(output)):
                cpu_lp_alloc[i] = output[i] * func[i]['podCPUUsage']
                mem_lp_alloc[i] = output[i] * func[i]['podMemUsage']
            # print("[t = {}] cpu_lp_alloc: {} \tmem_lp_alloc: {}".format(clk, cpu_lp_alloc, mem_lp_alloc))
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
            efficient_cpu_result.append(cpu_lp_alloc)
            efficient_mem_result.append(mem_lp_alloc)

        else:
            print('''
                Please select the correct model:
                    LP1 LP2 LP3 maxmin
                    drf+worstfit drf+alignment drf+berkeley
                ''')
            exit(1)
        # print("[t = {}] placed_pods_list: {}".format(clk, output))
    # print("Average completion time (milisecond): ", sum(delta)/len(delta))

print(maxmin_cpu_result)
print("")
print(maxmin_mem_result)
print("")
print(drf_worstfit_cpu_result)
print("")
print(drf_worstfit_mem_result)
print("")
print(drf_berkeley_cpu_result)
print("")
print(drf_berkeley_mem_result)
print("")
print(drf_alignment_cpu_result)
print("")
print(drf_alignment_mem_result)
print("")
print(lp1_cpu_result)
print("")
print(lp1_mem_result)
print("")
