from decimal import *
from gurobipy import quicksum
import gurobipy as gp
from gurobipy import GRB
import math

def workload_Init(func, l, n, m, node_1, node_2):
    nr = []
    resource_needed = []
    for i in range(n):
        nr.append(func[i]['desiredPodCountSLO'])
        resource_needed.append([func[i]['podCPUUsage'], func[i]['podMemUsage']])
    print("required pods number by each functon:", nr)
    print("pod resource requested by each function is ", resource_needed)
    total_requested_pods = sum(nr)
    a = [([resource_needed[i]] *(nr[i])) for i in range(n)] # Initialize the resource request of each Pod
    # print("pod resource requested for each function is ", a)

    c = list(zip([node_1['CPUCapacity'], node_2['CPUCapacity']], [node_1['MemCapacity'], node_2['MemCapacity']]))# combine cpu and memory to initailize the resource capacity of each node
    print("resource on each node is ", c)

    c_cpu_total = 0
    c_mem_total = 0
    for i in range(l):
        c_cpu_total += c[i][0]
        c_mem_total += c[i][1]
    # print("total cpu is: ", c_cpu_total)
    # print("total mem is: ", c_mem_total)
    total_resource = [c_cpu_total, c_mem_total]
    dominant_resource = [] # first is the amount of required dominant resource, second is the total resource for that type of resource
    dominant_resource_flags = [] # 0 is cpu, 1 is memory
    minimum_dominant_resource = [resource_needed[0][0], c_cpu_total] # first is the amount of required dominant resource, second is total resource for that type of resource
    nodes_remainings = c[:]

    for i in range(n): # calculate the dominant resource for each function
        cpu_share = resource_needed[i][0]/c_cpu_total
        mem_share = resource_needed[i][1]/c_mem_total
        if (cpu_share >= mem_share):
            dominant_resource_flags.append(0)
            dominant_resource.append([resource_needed[i][0], c_cpu_total])    
            if minimum_dominant_resource[0]/minimum_dominant_resource[1] > cpu_share:
                minimum_dominant_resource = [resource_needed[i][0], c_cpu_total]
        else:
            dominant_resource_flags.append(1)
            dominant_resource.append([resource_needed[i][1], c_mem_total])
            if minimum_dominant_resource[0]/minimum_dominant_resource[1] > mem_share:
                minimum_dominant_resource = [resource_needed[i][1], c_mem_total]

    # Calcuate dr for each function
    required_uniform_share = []
    for i in range(n):
        required_uniform_share.append((dominant_resource[i][0] * minimum_dominant_resource[1])/(dominant_resource[i][1] * minimum_dominant_resource[0]))

    return a, nr, c, resource_needed, dominant_resource, total_resource, required_uniform_share, nodes_remainings
'''
#The following is calculating the max-min fair share based on the dominant resource, assuming CPU and memory are divisible
def get_ds(remaining_resource, remaining_funs, resource_requirement, one_pod_ds, n, min_ds_idx):
    sum_cpu = 0
    sum_mem = 0
    for i in range(n):
        fun_idx = remaining_funs[i][1]
        sum_cpu += resource_requirement[fun_idx][0]/one_pod_ds[fun_idx]
        sum_mem += resource_requirement[fun_idx][1]/one_pod_ds[fun_idx]
    sum_cpu += resource_requirement[min_ds_idx][0]/one_pod_ds[min_ds_idx]
    sum_mem += resource_requirement[min_ds_idx][1]/one_pod_ds[min_ds_idx]
    
    return (remaining_resource[0]/sum_cpu, remaining_resource[1]/sum_mem) 

def update_resource_ds(current_ds, allocated_ds, remaining_resource, remaining_funs, resource_requirement, one_pod_ds, n, min_ds_index):
    for i in range(n):
        fun_idx = remaining_funs[i][1]
        used_cpu = (allocated_ds/one_pod_ds[fun_idx])* resource_requirement[fun_idx][0]
        used_mem = (allocated_ds/one_pod_ds[fun_idx])* resource_requirement[fun_idx][1]
        remaining_resource[0] = remaining_resource[0] - used_cpu
        remaining_resource[1] = remaining_resource[1] - used_mem
        #print("fun_idx:", fun_idx)
        current_ds[fun_idx] += allocated_ds
        
    used_cpu = (allocated_ds/one_pod_ds[min_ds_index])* resource_requirement[min_ds_index][0]
    used_mem = (allocated_ds/one_pod_ds[min_ds_index])* resource_requirement[min_ds_index][1]
    remaining_resource[0] = remaining_resource[0] - used_cpu
    remaining_resource[1] = remaining_resource[1] - used_mem
    current_ds[min_ds_index] += allocated_ds
    
def max_min(required_pods, resource_requirement, dominant_resource_flags, total_resource,n):
    one_pod_ds = []
    required_ds = []
    current_ds = [0]*n
    remaining_resource = total_resource[:]
    for i in range(n):
        i_ds = resource_requirement[i][dominant_resource_flags[i]]/total_resource[dominant_resource_flags[i]]
        one_pod_ds.append(i_ds)
        rds = required_pods[i] * i_ds
        #print("rds:", rds)
        heapq.heappush(required_ds, (rds, i)) # value is (func_index)
        
    while len(required_ds) > 0: 
        min_rds = heapq.heappop(required_ds) 
        #print(min_rds) 
        min_ds = min_rds[0]
        min_ds_index = min_rds[1]
        min_ds -= current_ds[min_ds_index]
        ds_cpu, ds_mem = get_ds(remaining_resource, required_ds, resource_requirement, one_pod_ds,len(required_ds), min_ds_index)
        x = min(ds_cpu, ds_mem)
        if x > min_ds:
            update_resource_ds(current_ds, min_ds, remaining_resource, required_ds, resource_requirement, one_pod_ds, len(required_ds), min_ds_index) 
        else:
            update_resource_ds(current_ds, x, remaining_resource, required_ds, resource_requirement, one_pod_ds, len(required_ds), min_ds_index)
            break
            
    return current_ds
#deviation from the max-min fairness share
def deviation(ds1, ds2, n):
    deviation = 0
    for i in range(n):
        deviation += abs(ds2[i] - ds1[i])
    return deviation
'''
def LP_Models(func, l, n, m, node_1, node_2, solverName):
    '''
    nr = []
    resource_needed = []
    for i in range(n):
        nr.append(func[i]['desiredPodCountSLO'])
        resource_needed.append([func[i]['podCPUUsage'], func[i]['podMemUsage']])
    print("required pods number by each functon:", nr)
    print("pod resource requested by each function is ", resource_needed)
    total_requested_pods = sum(nr)
    a = [([resource_needed[i]] *(nr[i])) for i in range(n)] # Initialize the resource request of each Pod
    # print("pod resource requested for each function is ", a)

    c = list(zip([node_1['CPUCapacity'], node_2['CPUCapacity']], [node_1['MemCapacity'], node_2['MemCapacity']]))# combine cpu and memory to initailize the resource capacity of each node
    print("resource on each node is ", c)

    c_cpu_total = 0
    c_mem_total = 0
    for i in range(l):
        c_cpu_total += c[i][0]
        c_mem_total += c[i][1]
    # print("total cpu is: ", c_cpu_total)
    # print("total mem is: ", c_mem_total)
    total_resource = [c_cpu_total, c_mem_total]

    # LP mode
    dominant_resource = [] # first is the amount of required dominant resource, second is the total resource for that type of resource
    dominant_resource_flags = [] # 0 is cpu, 1 is memory
    minimum_dominant_resource = [resource_needed[0][0], c_cpu_total] # first is the amount of required dominant resource, second is total resource for that type of resource
    nodes_remainings = c[:]

    for i in range(n): # calculate the dominant resource for each function
        cpu_share = resource_needed[i][0]/c_cpu_total
        mem_share = resource_needed[i][1]/c_mem_total
        if (cpu_share >= mem_share):
            dominant_resource_flags.append(0)
            dominant_resource.append([resource_needed[i][0], c_cpu_total])    
            if minimum_dominant_resource[0]/minimum_dominant_resource[1] > cpu_share:
                minimum_dominant_resource = [resource_needed[i][0], c_cpu_total]
        else:
            dominant_resource_flags.append(1)
            dominant_resource.append([resource_needed[i][1], c_mem_total])
            if minimum_dominant_resource[0]/minimum_dominant_resource[1] > mem_share:
                minimum_dominant_resource = [resource_needed[i][1], c_mem_total]

    # Calcuate dr for each function
    required_uniform_share = []
    for i in range(n):
        required_uniform_share.append((dominant_resource[i][0] * minimum_dominant_resource[1])/(dominant_resource[i][1] * minimum_dominant_resource[0]))
    '''
    a, nr, c, resource_needed, dominant_resource, total_resource, required_uniform_share, nodes_remainings = workload_Init(func, l, n, m, node_1, node_2)
    # Generate indices for W_rik
    python_list = []
    for i in range(l):
        for r in range(n):
            for k in range(nr[r]):
                python_list.append((i,r,k))
    w_indices = gp.tuplelist(python_list)
    placed_pods_list = [0] * n

    try:
        with gp.Env(empty=True) as env:
            env.setParam('OutputFlag', 0)
            env.start()
            with gp.Model(env=env) as model:
                # model = gp.Model() # Create a new model
                w = model.addVars(w_indices, vtype = GRB.BINARY, name = 'pod_matrix') # Create variables
                # Set objective
                if solverName == "LP1":
                    # LP1
                    model.setObjective(quicksum(quicksum(quicksum(w[i, r, k]/(math.pow(2, required_uniform_share[r]*(k+1))) for k in range(nr[r])) for r in range(n)) for i in range(l)), GRB.MAXIMIZE)
                elif solverName == "LP2":
                    # LP2
                    model.setObjective(quicksum(quicksum(quicksum(w[i, r, k]/(required_uniform_share[r]*(k+1)) for k in range(nr[r])) for r in range(n)) for i in range(l)), GRB.MAXIMIZE)
                elif solverName == "LP3":
                    # LP3
                    model.setObjective(quicksum(quicksum(quicksum(w[i, r, k]/(math.pow(required_uniform_share[r]*(k+1),2)) for k in range(nr[r])) for r in range(n)) for i in range(l)), GRB.MAXIMIZE)
                else:
                    print("No matched model")
                    exit(1)
                # Add constraint: pack each Pod in exactly one node
                model.addConstrs((quicksum(w[i, r, k] for i in range(l)) <= 1 for r in range(n)
                                                                               for k in range(nr[r])), "c0")
                for i in range(l):
                    model.addConstrs((quicksum(quicksum(a[r][k][j] * w[i, r, k] for k in range(nr[r])) for r in range(n)) <= c[i][j] for j in range(m)), "c1" + str(i))

                model.optimize() # Optimize model
                total_placed_pods = 0
                for i in range(l): # print out the result
                    for r in range(n):
                        for k in range(nr[r]):
                            if w[i,r,k].X == 1.0:
                                total_placed_pods += 1
                                placed_pods_list[r] += 1
                                # print(r, " ", k, " ", i, " ", w[i,r,k].X, "\n")
                                left_cpu = nodes_remainings[i][0] - resource_needed[r][0]
                                left_mem = nodes_remainings[i][1] - resource_needed[r][1]
                                nodes_remainings[i] = (left_cpu, left_mem)
                # print("total_placed_pods:", total_placed_pods,"total_requested_pods", total_requested_pods)
    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ': ' + str(e))

    except AttributeError:
        print('Encountered an attribute error')
        print('Optimization was stopped with status %d' % model.status)
        # do IIS, find infeasible constraints
    return placed_pods_list
