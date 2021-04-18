''' Simulator for Placement Engine '''
from __future__ import division
from decimal import *
import math
import sys, time
from lp_model_def import LP_Models
from efficient_model import Efficient_Models
from maxmin_model_def import maxmin_Models
from var_drf_def import DRF_Var
from wrkGen import wrk_generator

# Initialize input parameters
total_ticks = 1000

l = 40 # total 40 nodes available
# n = 200
n = int(sys.argv[1])
m = 2 # 2 kinds of resources

delta = []
# algs = ['maxmin', 'drf+worstfit', 'drf+berkeley', 'drf+alignment']
if sys.argv[2] == 'drf+worstfit':
    algs = ['maxmin', 'drf+worstfit']
elif sys.argv[2] == 'drf+berkeley':
    algs = ['maxmin', 'drf+berkeley']
elif sys.argv[2] == 'drf+alignment':
    algs = ['maxmin', 'drf+alignment']
elif sys.argv[2] == 'LP1':
    algs = ['maxmin', 'LP1']
elif sys.argv[2] == 'LP2':
    algs = ['maxmin', 'LP2']
# algs = ['maxmin'] 
# maxmin_cpu_result = []
# maxmin_mem_result = []
# drf_worstfit_cpu_result = []
# drf_worstfit_mem_result = []
# drf_berkeley_cpu_result = []
# drf_berkeley_mem_result = []
# drf_alignment_cpu_result = []
# drf_alignment_mem_result = []
# lp1_cpu_result = []
# lp1_mem_result = []
# lp2_cpu_result = []
# lp2_mem_result = []
# efficient_cpu_result = []
# efficient_mem_result = []

cpu_allocation_result = {'maxmin': [], 'drf+worstfit': [], 'drf+berkeley': [], 'drf+alignment': [], 'lp1': [], 'lp2': [], 'efficient': []}
mem_allocation_result = {'maxmin': [], 'drf+worstfit': [], 'drf+berkeley': [], 'drf+alignment': [], 'lp1': [], 'lp2': [], 'efficient': []}

for clk in range(total_ticks):
    if clk % 50 == 0:
        print("clk: ", clk)
    node, func = wrk_generator(l, n, m, clk)
    cpu = 0
    mem = 0
    for i in range(len(node)):
        cpu = cpu + node[i]['CPUCapacity']
        mem = mem + node[i]['MemCapacity']
    # print("cpu: {}, mem: {}".format(cpu, mem))
    for solverName in algs:
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
                # lp1_cpu_result.append(cpu_lp_alloc)
                # lp1_mem_result.append(mem_lp_alloc)
                cpu_allocation_result['lp1'].append(cpu_lp_alloc)
                mem_allocation_result['lp1'].append(mem_lp_alloc)
            elif solverName == 'LP2':
                # lp2_cpu_result.append(cpu_lp_alloc)
                # lp2_mem_result.append(mem_lp_alloc)
                cpu_allocation_result['lp2'].append(cpu_lp_alloc)
                mem_allocation_result['lp2'].append(mem_lp_alloc)

        elif solverName == 'maxmin':
            tick = time.time()
            cpu_maxmin_alloc, mem_maxmin_alloc = maxmin_Models(func, l, n, m, node)
            delta.append((time.time() - tick) * 1000000)
            # print("[t = {}] cpu_maxmin_alloc: {} \tmem_maxmin_alloc: {}".format(clk, cpu_maxmin_alloc, mem_maxmin_alloc))
            # maxmin_cpu_result.append(cpu_maxmin_alloc)
            # maxmin_mem_result.append(mem_maxmin_alloc)
            cpu_allocation_result['maxmin'].append(cpu_maxmin_alloc)
            mem_allocation_result['maxmin'].append(mem_maxmin_alloc)

        elif solverName[:3] == 'drf':
            # print("DRF algorithm")
            # print("\n============== {} cycle =============".format(clk))
            tick = time.time()
            cpu_drf_alloc, mem_drf_alloc = DRF_Var(func, node, cpu, mem, solverName)
            delta.append((time.time() - tick) * 1000000)
            # print("Execution time of {}: {} us".format(solverName, (time.time() - tick) * 1000000))
            # print("[t = {}] cpu_drf_alloc: {} \tmem_drf_alloc: {}".format(clk, cpu_drf_alloc, mem_drf_alloc))
            if solverName == 'drf+worstfit':
                # drf_worstfit_cpu_result.append(cpu_drf_alloc)
                # drf_worstfit_mem_result.append(mem_drf_alloc)
                cpu_allocation_result['drf+worstfit'].append(cpu_drf_alloc)
                mem_allocation_result['drf+worstfit'].append(mem_drf_alloc)
            elif solverName == 'drf+berkeley':
                # drf_berkeley_cpu_result.append(cpu_drf_alloc)
                # drf_berkeley_mem_result.append(mem_drf_alloc)
                cpu_allocation_result['drf+berkeley'].append(cpu_drf_alloc)
                mem_allocation_result['drf+berkeley'].append(mem_drf_alloc)
            elif solverName == 'drf+alignment':
                # drf_alignment_cpu_result.append(cpu_drf_alloc)
                # drf_alignment_mem_result.append(mem_drf_alloc)
                cpu_allocation_result['drf+alignment'].append(cpu_drf_alloc)
                mem_allocation_result['drf+alignment'].append(mem_drf_alloc)

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
            remaining_cpu = cpu - sum(cpu_lp_alloc)
            remaining_mem = mem - sum(mem_lp_alloc)
            unmet_cpu = [0] * len(output)
            unmet_mem = [0] * len(output)
            for i in range(len(output)):
                unmet_cpu[i] = cpu_slo[i] - cpu_lp_alloc[i]
                unmet_mem[i] = mem_slo[i] - mem_lp_alloc[i]
            # print("[t = {}] remaining_cpu: {} \tremaining_mem: {}".format(clk, remaining_cpu, remaining_mem))
            # print("[t = {}] unmet_cpu: {} \tunmet_mem: {}".format(clk, unmet_cpu, unmet_mem))
            # print("")
            # efficient_cpu_result.append(cpu_lp_alloc)
            # efficient_mem_result.append(mem_lp_alloc)
            cpu_allocation_result['efficient'].append(cpu_lp_alloc)
            mem_allocation_result['efficient'].append(mem_lp_alloc)


        else:
            print('''
                Please select the correct model:
                    LP1 LP2 LP3 maxmin
                    drf+worstfit drf+alignment drf+berkeley
                ''')
            exit(1)
        # print("[t = {}] placed_pods_list: {}".format(clk, output))
    # print("Average completion time (milisecond): ", sum(delta)/len(delta))


cpu_unfairness_over_time = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'lp1': 0, 'lp2': 0}
mem_unfairness_over_time = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'lp1': 0, 'lp2': 0}
if sys.argv[2] == 'drf+worstfit':
    candidates = ['drf+worstfit']
elif sys.argv[2] == 'drf+berkeley':
    candidates = ['drf+berkeley']
elif sys.argv[2] == 'drf+alignment':
    candidates = ['drf+alignment']
for i in range(total_ticks):
    cpu_tmp = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'lp1': 0, 'lp2': 0}
    mem_tmp = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'lp1': 0, 'lp2': 0}
    for j in range(n):
        for k in candidates:
            cpu_tmp[k] = cpu_tmp[k] + abs(cpu_allocation_result['maxmin'][i][j] - cpu_allocation_result[k][i][j])
            mem_tmp[k] = mem_tmp[k] + abs(mem_allocation_result['maxmin'][i][j] - mem_allocation_result[k][i][j])
    for p in candidates:
        cpu_unfairness_over_time[p] = cpu_unfairness_over_time[p] + cpu_tmp[p]
        mem_unfairness_over_time[p] = mem_unfairness_over_time[p] + mem_tmp[p]
print("cpu_unfairness_over_time: {}, mem_unfairness_over_time: {}".format(cpu_unfairness_over_time, mem_unfairness_over_time))

# Calculate degree of unfairness
'''
cpu_unfairness_over_time = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'lp1': 0, 'lp2': 0}
mem_unfairness_over_time = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'lp1': 0, 'lp2': 0}
candidates = ['drf+worstfit', 'drf+berkeley', 'drf+alignment']
for i in range(total_ticks):
    cpu_tmp = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'lp1': 0, 'lp2': 0}
    mem_tmp = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'lp1': 0, 'lp2': 0}
    for j in range(n):
        for k in candidates:
            cpu_tmp[k] = cpu_tmp[k] + abs(cpu_allocation_result['maxmin'][i][j] - cpu_allocation_result[k][i][j])
            mem_tmp[k] = mem_tmp[k] + abs(mem_allocation_result['maxmin'][i][j] - mem_allocation_result[k][i][j])
    for p in candidates:
        cpu_unfairness_over_time[p] = cpu_unfairness_over_time[p] + cpu_tmp[p]
        mem_unfairness_over_time[p] = mem_unfairness_over_time[p] + mem_tmp[p]
print("cpu_unfairness_over_time: {}, mem_unfairness_over_time: {}".format(cpu_unfairness_over_time, mem_unfairness_over_time))
'''

# Calculate degree of inefficiency
'''
cpu_inefficiency_over_time = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'lp1': 0, 'lp2': 0}
mem_inefficiency_over_time = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'lp1': 0, 'lp2': 0}
candidates = ['drf+worstfit', 'drf+berkeley', 'drf+alignment']
for i in range(total_ticks):
    cpu_tmp = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'lp1': 0, 'lp2': 0}
    mem_tmp = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'lp1': 0, 'lp2': 0}
    for j in range(n):
        for k in candidates:
            cpu_tmp[k] = cpu_tmp[k] + abs(cpu_allocation_result['efficient'][i][j] - cpu_allocation_result[k][i][j])
            mem_tmp[k] = mem_tmp[k] + abs(mem_allocation_result['efficient'][i][j] - mem_allocation_result[k][i][j])
    for p in candidates:
        cpu_inefficiency_over_time[p] = cpu_inefficiency_over_time[p] + cpu_tmp[p]
        mem_inefficiency_over_time[p] = mem_inefficiency_over_time[p] + mem_tmp[p]
print("cpu_inefficiency_over_time: {}, mem_inefficiency_over_time: {}".format(cpu_inefficiency_over_time, mem_inefficiency_over_time))
'''
