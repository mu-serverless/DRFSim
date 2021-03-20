from __future__ import division
from decimal import *
import heapq
import random
import math
from math import gcd
import numpy as np
import time

def std_DRF():
    #perfect drf, without considering the node fragment issue
    current_pods = [0]*n
    dominant_resource = [] #the list of dominant resource for each function

    #print(minimum_dominant_resource[0][0])
    #calculate the dominant resource for each function
    for i in range(n):
        cpu_share = resource_needed[i][0]/c_cpu_total
        mem_share = resource_needed[i][1]/c_mem_total
        if (cpu_share >= mem_share):
            dominant_resource.append(0) 
        else:
            dominant_resource.append(1)
            
    drf_functions = []
    #initilize functions and remaining resources
    for i in range(n):
        dominant_share = (current_pods[i] * resource_needed[i][dominant_resource[i]])/total_resource[dominant_resource[i]]
        heapq.heappush(drf_functions, (dominant_share, ((nr[i] - current_pods[i]),i)))


    drf_total_placed_pods = 0
    drf_placed_pods_list = [0]*n
    left_cpu = c_cpu_total 
    left_mem = c_mem_total 
    while drf_functions: 
        min_fun = heapq.heappop(drf_functions) 
        #print(min_fun) 
        fun_index = min_fun[1][1] 
        required_resource = resource_needed[fun_index]
        #update remaining resource
        l_cpu = left_cpu - required_resource[0] 
        l_mem = left_mem - required_resource[1] 
        if l_cpu < 0 or l_mem < 0:
            continue
        left_cpu = l_cpu
        left_mem = l_mem
        drf_total_placed_pods += 1
        #recalcuate the domainant share and update the queue
        remaining_pods_number = min_fun[1][0] - 1
        #print("place one pod for function ", fun_index, "remaining pods number is:", remaining_pods_number)
        drf_placed_pods_list[fun_index] =  drf_placed_pods_list[fun_index] + 1
        if remaining_pods_number > 0:
            dominant_share = required_resource[dominant_resource[fun_index]]/total_resource[dominant_resource[fun_index]] + min_fun[0]
            heapq.heappush(drf_functions, (dominant_share, (remaining_pods_number,fun_index)))
            
    drf_total_cpu_utage = 0
    drf_total_mem_utage = 0
    for i in range(n):
        drf_total_cpu_utage += drf_placed_pods_list[i] * resource_needed[i][0]
        drf_total_mem_utage += drf_placed_pods_list[i] * resource_needed[i][1]
        
    print("drf total_cpu_utage:", drf_total_cpu_utage/c_cpu_total, "drf total_mem_utage:", drf_total_mem_utage/c_mem_total )
    print("drf_placed_pods_list: ", drf_placed_pods_list)
    #print("required_pod_list:    ", nr)

    print("drf total_placed_pods:", drf_total_placed_pods," total_requested_pods:",total_requested_pods)
    drf_f,drf_e,drf_t = fairness_efficiency(drf_placed_pods_list, resource_needed,dominant_resource, total_resource, n, 2)
    print("perfect drf fairness is:",drf_f, " perfect drf efficiency is:", drf_e, "perfect drf f_mult_e is:", drf_t)

    drf_jain_index = jainIndex(drf_placed_pods_list, resource_needed,dominant_resource, total_resource, n)
    print("perfect drf  jain index is:", drf_jain_index)

    drf_alpha_f,drf_min_share = alpha_fairness(drf_placed_pods_list, resource_needed,dominant_resource, total_resource, n,10,nr)
    print("perfect alpha fairness is:", drf_alpha_f, "drf min_share is:", drf_min_share)

    drf_dominant_share_list = []
    required_dominant_share_list = []
    for i in range(n):
        s = (drf_placed_pods_list[i]* resource_needed[i][dominant_resource[i]])/total_resource[dominant_resource[i]]
        drf_dominant_share_list.append(s)
        r_s = (nr[i]*resource_needed[i][dominant_resource[i]])/total_resource[dominant_resource[i]]
        required_dominant_share_list.append(r_s)


    v_f = variance_fairness(required_dominant_share_list, drf_dominant_share_list, n)
    print("perfect drf v_f is:", v_f)


    drf_violation_index = violation_index(nr, resource_needed, drf_placed_pods_list, dominant_resource, total_resource, n)
    print("drf violation index is:", drf_violation_index)

    deviation_max_min = deviation(drf_dominant_share_list, max_min_ds, n)
    print("deviation from max min:", deviation_max_min)