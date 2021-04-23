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
total_ticks = 1

l = 10 # total 40 nodes available
# n = 200
n = int(sys.argv[1])
m = 2 # 2 kinds of resources

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
elif sys.argv[2] == 'efficient-drf+worstfit':
    algs = ['efficient', 'drf+worstfit']
elif sys.argv[2] == 'efficient-drf+berkeley':
    algs = ['efficient', 'drf+berkeley']
elif sys.argv[2] == 'efficient-drf+alignment':
    algs = ['efficient', 'drf+alignment']
elif sys.argv[2] == 'efficient-LP1':
    algs = ['efficient', 'LP1']
elif sys.argv[2] == 'efficient-LP2':
    algs = ['efficient', 'LP2']

cpu_allocation_result = {'maxmin': [], 'drf+worstfit': [], 'drf+berkeley': [], 'drf+alignment': [], 'LP1': [], 'LP2': [], 'efficient': []}
mem_allocation_result = {'maxmin': [], 'drf+worstfit': [], 'drf+berkeley': [], 'drf+alignment': [], 'LP1': [], 'LP2': [], 'efficient': []}

delta = []
cpu_request = [0] * total_ticks
mem_request = [0] * total_ticks
for clk in range(total_ticks):
    if clk % 50 == 0:
        print("clk: ", clk)
    node, func, cpu_request[clk], mem_request[clk]  = wrk_generator(l, n, m, clk)
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
            delta.append((time.time() - tick) * 1)
            # print("Execution time of {}: {} us".format(solverName, (time.time() - tick) * 1000000))
            cpu_lp_alloc = [0] * len(output) 
            mem_lp_alloc = [0] * len(output)
            for i in range(len(output)):
                cpu_lp_alloc[i] = output[i] * func[i]['podCPUUsage']
                mem_lp_alloc[i] = output[i] * func[i]['podMemUsage']
            # print("[t = {}] cpu_lp_alloc: {} \tmem_lp_alloc: {}".format(clk, cpu_lp_alloc, mem_lp_alloc))
            if solverName == 'LP1':
                cpu_allocation_result['LP1'].append(cpu_lp_alloc)
                mem_allocation_result['LP1'].append(mem_lp_alloc)
            elif solverName == 'LP2':
                cpu_allocation_result['LP2'].append(cpu_lp_alloc)
                mem_allocation_result['LP2'].append(mem_lp_alloc)

        elif solverName == 'maxmin':
            # tick = time.time()
            cpu_maxmin_alloc, mem_maxmin_alloc = maxmin_Models(func, l, n, m, node)
            # delta.append((time.time() - tick) * 1000000)
            # print("[t = {}] cpu_maxmin_alloc: {} \tmem_maxmin_alloc: {}".format(clk, cpu_maxmin_alloc, mem_maxmin_alloc))
            cpu_allocation_result['maxmin'].append(cpu_maxmin_alloc)
            mem_allocation_result['maxmin'].append(mem_maxmin_alloc)

        elif solverName[:3] == 'drf':
            # print("DRF algorithm")
            # print("\n============== {} cycle =============".format(clk))
            # tick = time.time()
            cpu_drf_alloc, mem_drf_alloc, computation_time = DRF_Var(func, node, cpu, mem, solverName)
            delta.append(computation_time)
            # print("Execution time of {}: {} us".format(solverName, (time.time() - tick) * 1000000))
            # print("[t = {}] cpu_drf_alloc: {} \tmem_drf_alloc: {}".format(clk, cpu_drf_alloc, mem_drf_alloc))
            if solverName == 'drf+worstfit':
                cpu_allocation_result['drf+worstfit'].append(cpu_drf_alloc)
                mem_allocation_result['drf+worstfit'].append(mem_drf_alloc)
            elif solverName == 'drf+berkeley':
                cpu_allocation_result['drf+berkeley'].append(cpu_drf_alloc)
                mem_allocation_result['drf+berkeley'].append(mem_drf_alloc)
            elif solverName == 'drf+alignment':
                cpu_allocation_result['drf+alignment'].append(cpu_drf_alloc)
                mem_allocation_result['drf+alignment'].append(mem_drf_alloc)

        elif solverName == 'efficient':
            tick = time.time()
            output = Efficient_Models(func, l, n, m, node)
            delta.append((time.time() - tick) * 1)
            cpu_lp_alloc = [0] * len(output) 
            mem_lp_alloc = [0] * len(output)
            for i in range(len(output)):
                cpu_lp_alloc[i] = output[i] * func[i]['podCPUUsage']
                mem_lp_alloc[i] = output[i] * func[i]['podMemUsage']
            # print("[t = {}] cpu_lp_alloc: {} \tmem_lp_alloc: {}".format(clk, cpu_lp_alloc, mem_lp_alloc))
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
# print("Average completion time (second): ", sum(delta)/len(delta))

'''
cpu_unfairness_over_time = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
mem_unfairness_over_time = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
if sys.argv[2] == 'drf+worstfit':
    candidates = ['drf+worstfit']
elif sys.argv[2] == 'drf+berkeley':
    candidates = ['drf+berkeley']
elif sys.argv[2] == 'drf+alignment':
    candidates = ['drf+alignment']
elif sys.argv[2] == 'LP1':
    candidates = ['LP1']
elif sys.argv[2] == 'LP2':
    candidates = ['LP2']
for i in range(total_ticks):
    cpu_tmp = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
    mem_tmp = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
    for j in range(n):
        for k in candidates:
            cpu_tmp[k] = cpu_tmp[k] + abs(cpu_allocation_result['maxmin'][i][j] - cpu_allocation_result[k][i][j])
            mem_tmp[k] = mem_tmp[k] + abs(mem_allocation_result['maxmin'][i][j] - mem_allocation_result[k][i][j])
    for p in candidates:
        cpu_unfairness_over_time[p] = cpu_unfairness_over_time[p] + cpu_tmp[p]
        mem_unfairness_over_time[p] = mem_unfairness_over_time[p] + mem_tmp[p]
print("cpu_unfairness_over_time: {},\n mem_unfairness_over_time: {}".format(cpu_unfairness_over_time, mem_unfairness_over_time))
'''
cpu_inefficiency_over_time = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
mem_inefficiency_over_time = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
cpu_unmet_over_time = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
mem_unmet_over_time = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
if sys.argv[2] == 'efficient-drf+worstfit':
    candidates = ['drf+worstfit']
elif sys.argv[2] == 'efficient-drf+berkeley':
    candidates = ['drf+berkeley']
elif sys.argv[2] == 'efficient-drf+alignment':
    candidates = ['drf+alignment']
elif sys.argv[2] == 'efficient-LP1':
    candidates = ['LP1']
elif sys.argv[2] == 'efficient-LP2':
    candidates = ['LP2']
for i in range(total_ticks):
    cpu_tmp = {'efficient': 0, 'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
    mem_tmp = {'efficient': 0, 'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
    for j in range(n):
        for k in candidates:
            cpu_tmp[k] = cpu_tmp[k] + cpu_allocation_result[k][i][j]
            mem_tmp[k] = mem_tmp[k] + mem_allocation_result[k][i][j]
        cpu_tmp['efficient'] = cpu_tmp['efficient'] + cpu_allocation_result['efficient'][i][j]
        mem_tmp['efficient'] = mem_tmp['efficient'] + mem_allocation_result['efficient'][i][j]
    for p in candidates:
        cpu_inefficiency_over_time[p] = cpu_inefficiency_over_time[p] + abs(cpu_tmp['efficient'] - cpu_tmp[p])
        mem_inefficiency_over_time[p] = mem_inefficiency_over_time[p] + abs(mem_tmp['efficient'] - mem_tmp[p])
        cpu_unmet_over_time[p] = cpu_unmet_over_time[p] + abs(cpu_request[i] - cpu_tmp[p])
        mem_unmet_over_time[p] = mem_unmet_over_time[p] + abs(mem_request[i] - mem_tmp[p])
# print("cpu_inefficiency_over_time: {},\n mem_inefficiency_over_time: {}".format(cpu_inefficiency_over_time, mem_inefficiency_over_time))
print("cpu_unmet_over_time: {},\n mem_unmet_over_time: {}".format(cpu_unmet_over_time, mem_unmet_over_time))
# Calculate degree of unfairness
'''
cpu_unfairness_over_time = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
mem_unfairness_over_time = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
candidates = ['drf+worstfit', 'drf+berkeley', 'drf+alignment']
for i in range(total_ticks):
    cpu_tmp = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
    mem_tmp = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
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
cpu_inefficiency_over_time = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
mem_inefficiency_over_time = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
candidates = ['drf+worstfit', 'drf+berkeley', 'drf+alignment']
for i in range(total_ticks):
    cpu_tmp = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
    mem_tmp = {'drf+worstfit': 0, 'drf+berkeley': 0, 'drf+alignment': 0, 'LP1': 0, 'LP2': 0}
    for j in range(n):
        for k in candidates:
            cpu_tmp[k] = cpu_tmp[k] + abs(cpu_allocation_result['efficient'][i][j] - cpu_allocation_result[k][i][j])
            mem_tmp[k] = mem_tmp[k] + abs(mem_allocation_result['efficient'][i][j] - mem_allocation_result[k][i][j])
    for p in candidates:
        cpu_inefficiency_over_time[p] = cpu_inefficiency_over_time[p] + cpu_tmp[p]
        mem_inefficiency_over_time[p] = mem_inefficiency_over_time[p] + mem_tmp[p]
print("cpu_inefficiency_over_time: {}, mem_inefficiency_over_time: {}".format(cpu_inefficiency_over_time, mem_inefficiency_over_time))
'''
