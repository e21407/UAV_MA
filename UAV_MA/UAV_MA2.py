# coding:utf-8  
'''
Created on 2018-03-13

@author: liubaichuan
'''

import random
import math

#===================== global variable ======================#
CandPathIDSet_for_2_UAVs = {}  ## {<Src-UAV,Dst-UAV>:[path1_id,path2_id,...]}, the candidate path-set for all  pair of UAVs. !!!! SPECIAL-CASE-20161109: EVEN a SW to itself has an individual path_ID, 2016-1109!!!!!
Path_database = {}  # # {<Path_id>:pathContent}, e.g., pathContent:[(1, 2), (2, 5), (5, 3)]; or EMPTY list [].
Info_of_task = {}  # # {<workflow_id, task_id>:[Cap]}
Info_of_WF = {}  # #{<worlflow_ID>: list_of_a_flow}, list_of_a_flow=[(currTask_ID, succTask_ID, needed_bandwidth)...]
Cap_links = {}  # #   {<u,v>:CapVal}, the Capacity set of all links 
Info_of_UAV = {}  # #{<UAV_ID>:CapVal}, the compute capacity of all UAVs

var_x_wtk = {}  # # {<workflow_ID, task_ID, UAV_ID>: int},x_(k)^(w,t) == 1,if task t of workflow w is assigned  to UAV k
var_y_wpab = {}  # # {<workflow_ID, path_ID, task_a_ID, task_b_ID>}, y_(a,b)^(w,p) == 1, if task a and task b in workflow w use path p to transfer data
Timers = {}  # #{<WF_ID, taskA_ID, taskB_ID>:[ts_begin, timer_len, pathID_old, pathID_new, UAVID_old, UAVID_new]}
#=============================================================
Global_PATH_ID_START_COUNTING = 0  # MUST NOT be changed from 0, 2016-1109.

#===================== input file name ======================#
CandPaths_file = "_input_PathSet.txt"
Info_of_WF_file = "_input_Info_of_workflow_a_flow.txt"
CapLinks_file = "_input_Cap_links.txt"
Info_of_task_file = "_input_Info_of_task_a_flow.txt"
Info_of_UAVs_file = "_input_Info_of_UAVs.txt"

#=================================================
global_Aggregated_TR_in_acrs = {}  # # {(u,v): aggregated-TR-in-arc-uv }
global_system_throughput = 0.0
global_weighted_RoutingCost = 0.0
global_weighted_computeCost = 0.0
WEIGHT_OF_ROUTING_COST = 1
WEIGHT_OF_COMPUTE_COST = 1

# ==================================== USE-CASE ==============================================
T = 500;  # # The total running period of system.
STEP_TO_RUN = 0.001;  # # The length of time-slot, e.g., 0.001 second is the BEST step after testing.
STEP_TO_CHECK_TIMER = STEP_TO_RUN;  # # The step (length of interval) of check timer-expiration, e.g., 0.1 second.
Beta = 6;  # # The parameter in the theoretical derivation.
Tau = 0;  # # The alpha regarding the Markov_Chain.
step_times = 0
#=================================================
Lst_Assignable_UAV_ID = [8, 9, 12, 13, 16, 17, 20, 21, 24, 25]  # list of UAV's ID which can be assigned task

#=================================================
LogRun = open('Log_running.txt', 'w')
LogVar_X = open('log_Var_X.txt', 'w')
LogVar_Y = open('log_Var_Y.txt', 'w')
LogReplacement = open('logReplacement.txt', 'w')
LogPerformanceRecord = open('log_performance.txt', 'w')

#====debug variable======
len_of_var_y_flag = 0
len_of_var_y = 0

 
def initialize(_in_CandPaths_file, _in_Info_of_WF_file, _in_CapLinks_file, _in_Info_of_task_file, _in_Info_of_UAVs_file):
    # ---- 1 Read the Given path data :
    global CandPathIDSet_for_2_UAVs, Path_database
    unique_PathID_idx = Global_PATH_ID_START_COUNTING;  # ## !! Lable of each path.
    # _input_PathSet.txt
    with open(_in_CandPaths_file, "rU") as f:
        for lines in f:
            line = lines.strip('\n')
            if len(line) > 0:
                lineContent = line.split('\t')
                SrcUAV_id = int(lineContent[1]);
                DstUAV_id = int(lineContent[3]);
                strPath = str(lineContent[5]);
                
                # ## --!! Case-I. (if path=="[]") SPECIAL-CASE-20161109-handling: from each switch to itself, there is no length-positive-path.
                # ## --!! Case-II. (if path!="[]") Normal-case-handling: from each switch to other one, there is length-positive-path.
                # ## --!! We handle both the two cases simultaneously: by analyzing the content of the path.
                One_path_in_seg = [];
                pathContent = strPath.split(">")
                for i in range(len(pathContent)):
                    if i + 1 in range(len(pathContent)):
                        One_path_in_seg.append((str(pathContent[i]), str(pathContent[i + 1])));
    
                # # -- a. !!! We first record the normal-sequence One_path_in_seg for (SrcSW, DstSW);
                ## --- a.1 store this new path to path_database. !!!!! One_path_in_seg possibly an EMPTY list [].!!!!
                if unique_PathID_idx not in Path_database:
                    Path_database[unique_PathID_idx] = One_path_in_seg;  ## !!!!! One_path_in_seg possibly an EMPTY list [].!!!!
                
                # # --- a.2 record this path to the CandPathIDSet_for_2_SWs
                if (SrcUAV_id, DstUAV_id) not in CandPathIDSet_for_2_UAVs:
                    CandPathIDSet_for_2_UAVs[(SrcUAV_id, DstUAV_id)] = [];
                CandPathIDSet_for_2_UAVs[(SrcUAV_id, DstUAV_id)].append(unique_PathID_idx);
                unique_PathID_idx += 1

                # # -- b. !!! We ALSO record the reverse-path for  (SrcSW, DstSW), i.e., path for (DstSW, SrcSW).
                reversedPath = pathContent[::-1];  # # Reverse the content of this path.
                reverse_path_in_seg = [];
                for i in range(len(reversedPath)):
                    if i + 1 in range(len(reversedPath)):
                        reverse_path_in_seg.append((str(reversedPath[i]), str(reversedPath[i + 1])));
                # # --- b.1 store this new path to the path_database
                if unique_PathID_idx not in Path_database:
                    Path_database[unique_PathID_idx] = reverse_path_in_seg;
                # # --- b.2 record this path to the CandPathIDSet_for_2_SWs
                if (DstUAV_id, SrcUAV_id) not in CandPathIDSet_for_2_UAVs:
                    CandPathIDSet_for_2_UAVs[(DstUAV_id, SrcUAV_id)] = [];
                CandPathIDSet_for_2_UAVs[(DstUAV_id, SrcUAV_id)].append(unique_PathID_idx);
                unique_PathID_idx += 1  # #!!###:~
    
    #----------- 2 Read the Given Info_of_WF data  
    global Info_of_WF
    # _input_Info_of_workflow.txt
    with open(_in_Info_of_WF_file, 'rU') as f:
        for lines in f:
            line = lines.strip('\n')
            lineContent = line.split("\t")
            WF_ID = int(lineContent[1])
            currTask_ID = int(lineContent[3])
            succTask_ID = int(lineContent[5])
            needed_bandwidth = float(lineContent[7])
            
            info_of_a_flow = (currTask_ID, succTask_ID, needed_bandwidth)
            if WF_ID not in Info_of_WF:
                list_flows = []
                list_flows.append(info_of_a_flow)
                Info_of_WF[WF_ID] = list_flows
            else:
                
                Info_of_WF[WF_ID].append(info_of_a_flow)
     
    # ---- 3 Read the link-Capacity, and all nodes and all edges:           
    global Cap_links
    # _input_Cap_links.txt
    with open(_in_CapLinks_file, 'rU') as f:
        for lines in f:
            line = lines.strip('\n')
            lineContent = line.split("\t")
            u_id = str(lineContent[1]);
            v_id = str(lineContent[3]);
            CapVal = float(lineContent[5]);
            # # --- a. record cap_links.
            if (u_id, v_id) not in Cap_links:
                Cap_links[(u_id, v_id)] = CapVal  # #
                
            # # --- b. initialize the global_Aggregated_TR_in_acrs.
            if (u_id, v_id) not in global_Aggregated_TR_in_acrs:
                global_Aggregated_TR_in_acrs[(u_id, v_id)] = 0  # ## ---- 3 Read the Capacity of links:~    
    
    #---- 4. Read the given Info_of_task data
    global Info_of_task;
    # _input_Info_of_task.txt
    with open(_in_Info_of_task_file, 'rU') as f:
        for lines in f:
            line = lines.strip('\n')
            lineContent = line.split("\t")
            workflow_ID = int(lineContent[1])
            task_ID = int(lineContent[3])
            CapVal = float(lineContent[5])
            
            if (workflow_ID, task_ID) not in Info_of_task:
                Info_of_task[(workflow_ID, task_ID)] = CapVal
                
    #---- 5. Read the given Info_of_UAV data
    global Info_of_UAV
    # _input_Info_of_UAVs.txt
    with open(_in_Info_of_UAVs_file, "rU") as f:
        for lines in f:
            line = lines.strip('\n')
            lineContent = line.split("\t")
            UAV_ID = int(lineContent[1])
            CapVal = float(lineContent[3])
            
            if UAV_ID not in Info_of_UAV:
                Info_of_UAV[UAV_ID] = CapVal
  
#==================== end of initialize function===================


def Assign_task_to_UAV_randomly():
    global CandPathIDSet_for_2_UAVs, Path_database, Info_of_task, Info_of_WF, Cap_links, Info_of_UAV
    
    numOfUAVs = len(Lst_Assignable_UAV_ID)
    for WF_ID, content in Info_of_WF.items():
        for a_flow in content:
            currTaskID = a_flow[0]
            succTaskID = a_flow[1]
            # --- assign the task to the UAV and find the path randomly
            while 1:
                idx_UAV1 = random.randint(0, numOfUAVs - 1)
                idx_UAV2 = random.randint(0, numOfUAVs - 1)
                if idx_UAV1 == idx_UAV2:
                    print 'hit'
                    continue
                UAV_ID1 = Lst_Assignable_UAV_ID[idx_UAV1]
                UAV_ID2 = Lst_Assignable_UAV_ID[idx_UAV2]
                pathID_list = Find_pathID_list_for_a_pair_of_UAVs(UAV_ID1, UAV_ID2)
                if pathID_list:
                    # print 'deal'
                    if not Check_whether_a_task_has_assignment(WF_ID, currTaskID):
                        var_x_wtk[(WF_ID, currTaskID, UAV_ID1)] = 1
                    if not Check_whether_a_task_has_assignment(WF_ID, succTaskID):
                        var_x_wtk[(WF_ID, succTaskID, UAV_ID2)] = 1
                    idx_path = random.randint(0, len(pathID_list) - 1)
                    # pathID = Path_database.keys()[pathID_list(idx_path)]
                    pathID = pathID_list[idx_path]
                    # #注意这里在选路之前没有进行判断路径上的带宽是否满足两个任务之间的数据传输要求
                    var_y_wpab[WF_ID, pathID, currTaskID, succTaskID] = 1
                    LogReplacement.write('initialize set -- WF_ID:%d, pathID:%d, currTaskID:%d, succTaskID:%d\n\n' % (WF_ID, pathID, currTaskID, succTaskID))
                    break
    print 'initialize_assign_taAssign_task_to_UAV_randomly============end of function initialize_assign_taAssign_task_to_UAV_randomlyef Check_whether_a_task_has_assignment(WF_ID, task_ID):
    for w, t, _ in var_x_wtk:
        if w == WF_ID and t == task_ID:
            # return 1 means the task has assigned to a UAV
            return 1
    # return 0 means the task has not assigned to a UAV
    return 0

 
def Find_pathID_list_for_a_pair_of_UAVs(UAV_ID1, UAV_ID2):
    if (UAV_ID1, UAV_ID2) in CandPathIDSet_for_2_UAVs:
        return CandPathIDSet_for_2_UAVs[(UAV_ID1, UAV_ID2)]
    return []


#=====================================================================================
# == If all the one-hop of a workflow can be assigned to the UAV swarm then that workflow is satisfied
def Get_list_of_satisfied_WF_ID():
    global var_y_wpab, Info_of_WF
    ret_satisfied_WF_ID = []
    flag_of_a_WF = 0
    for WF_ID, lst_of_a_flow in Info_of_WF.items():
        flag_of_a_WF = 1
        for a_flow in lst_of_a_flow:
            flag_of_a_flow = 0
            for w, p, a, b in var_y_wpab:
                if w == WF_ID and a == a_flow[0] and b == a_flow[1]:
                    flag_of_a_flow = 1
                    break
            if flag_of_a_flow == 0:
                flag_of_a_WF = 0
                break
        if flag_of_a_WF == 1:
            ret_satisfied_WF_ID.append(WF_ID)
    return ret_satisfied_WF_ID
#=========================end of function Get_list_of_satisfied_WF_ID()===============


#=====================================================================================
def Update_system_metrics_in_Main():
    global Info_of_WF, Path_database, Info_of_UAV, Info_of_task, var_x_wtk, var_y_wpab
    global global_system_throughput, global_weighted_RoutingCost, global_weighted_computeCost
    global WEIGHT_OF_ROUTING_COST, WEIGHT_OF_COMPUTE_COST
    lst_of_satisfied_WF_ID = Get_list_of_satisfied_WF_ID()
    
    system_throughput = 0.0
    routingCost = 0.0
    computeCost = 0.0
    
    for WF_ID in lst_of_satisfied_WF_ID:
        for a_flow in Info_of_WF[WF_ID]:
            taskA_ID = a_flow[0]
            taskB_ID = a_flow[1]
            bandwidth = a_flow[2]
            # --1 calculate the system throughput 
            system_throughput += bandwidth
            # --2 calculate the routing cost
            IU_PathID = Get_the_IU_pathID_between_two_task(WF_ID, taskA_ID, taskB_ID) 
            if IU_PathID != -1:
                routingCost += len(Path_database[IU_PathID])
                
    # --3 calculate the compute cost
    for key, val in Info_of_UAV.items():
        task_list_assigned_to_a_UAV = Get_the_task_list_assigned_to_a_UAV(key)
        total_Cap_of_a_UAV = 0
        for WF_ID, task_ID in task_list_assigned_to_a_UAV:
            if(WF_ID, task_ID) in Info_of_task:
                total_Cap_of_a_UAV += Info_of_task[(WF_ID, task_ID)]
        computeCost += total_Cap_of_a_UAV / val         
            
    weighted_routing_cost = WEIGHT_OF_ROUTING_COST * routingCost
    weighted_compute_cost = WEIGHT_OF_COMPUTE_COST * computeCost
    
    # # ---- update the current Objectives
    global_system_throughput = system_throughput
    global_weighted_RoutingCost = weighted_routing_cost
    global_weighted_computeCost = weighted_compute_cost         
#========end of function Update_system_metrics_in_Main() ==============================


def Get_objVal_of_configurations_in_whole_system():
    return global_system_throughput - global_weighted_RoutingCost - global_weighted_computeCost


def Get_the_IU_pathID_between_two_task(WF_ID, taskA_ID, taskB_ID):
    global var_y_wpab
    for w, p, a, b in var_y_wpab:
        if w == WF_ID and a == taskA_ID and b == taskB_ID:
            return p
    return -1

# def Get_the_UAV_ID_of_a_task(WF_ID, task_ID):
#     global var_x_wtk
#     for w, t, u in var_x_wtk:
#         if w == WF_ID and t == task_ID:
#             return u
#     return -1


def Get_the_IU_UAV_ID_of_a_task(WF_ID, task_ID):
    global var_x_wtk
    for w, t, u in var_x_wtk:
        if w == WF_ID and t == task_ID:
            return u
    return -1


def Get_the_task_list_assigned_to_a_UAV(UAV_ID):
    global var_x_wtk
    ret_result_list = []
    for w, t, u in var_x_wtk:
        if u == UAV_ID:
            ret_result_list.append((w, t))
    return ret_result_list    


def Select_a_rdm_NIU_UAV_for_the_task(WF_ID, task_ID):
    ret_NIU_UAV_ID = -1
    # -- 1. get the id list of not in-use UAV
    # list_NIU_UAV = Get_list_of_NIU_UAV_ID_to_the_task(WF_ID, task_ID)
    list_NIU_UAV = Get_list_of_NIU_UAV_ID_to_the_task2(WF_ID, task_ID)
    # -- 2. pick up one rdmly from the list.
    size_of_list = len(list_NIU_UAV)
    if size_of_list > 0:
        idx_targetUAV = random.randint(0, size_of_list - 1)
        ret_NIU_UAV_ID = list_NIU_UAV[idx_targetUAV]
    return ret_NIU_UAV_ID

# def Get_list_of_NIU_UAV_ID_to_the_task(WF_ID, task_ID):
#     global Info_of_UAV
#     IU_UAV_ID = Get_the_IU_UAV_ID_of_a_task(WF_ID, task_ID)
#     ret_result_list = [UAV_ID for UAV_ID in Info_of_UAV if UAV_ID != IU_UAV_ID]
#     return ret_result_list

    
# this function select a not-in use UAV ID from Lst_Assignable_UAV_ID
def Get_list_of_NIU_UAV_ID_to_the_task2(WF_ID, task_ID):
    global Info_of_UAV
    IU_UAV_ID = Get_the_IU_UAV_ID_of_a_task(WF_ID, task_ID)
    ret_result_list = [UAV_ID for UAV_ID in Lst_Assignable_UAV_ID if UAV_ID != IU_UAV_ID]
    return ret_result_list


def Select_a_rdm_NIU_path_for_the_task(WF_ID, taskA_ID, taskB_ID):
    ret_NIU_path_ID = -1
    # get the id list of not in-use path
    list_NIU_path = Get_list_of_NIU_pathIDs_between_2_task(WF_ID, taskA_ID, taskB_ID)
    # pick up one randomly from the list
    size_of_list = len(list_NIU_path)
    if size_of_list > 0:
        idx_targetPath = random.randint(0, size_of_list - 1)
        ret_NIU_path_ID = list_NIU_path[idx_targetPath]
    return ret_NIU_path_ID


def Get_list_of_NIU_pathIDs_between_2_task(WF_ID, taskA_ID, taskB_ID):
    # find the id of the UAV which is assigned to run the task
    UAV_ID_to_taskA = Get_the_IU_UAV_ID_of_a_task(WF_ID, taskA_ID)
    UAV_ID_to_taskB = Get_the_IU_UAV_ID_of_a_task(WF_ID, taskB_ID)
    # find the path_id set of the two UAVs 
    List_path_ID_for_a_pair_UAVs = Find_pathID_list_for_a_pair_of_UAVs(UAV_ID_to_taskA, UAV_ID_to_taskB)
    # remove the in-use path_id from the result
    IU_path_ID = Get_the_IU_pathID_between_two_task(WF_ID, taskA_ID, taskB_ID)
    ret_reslut_lst = [pathID for pathID in List_path_ID_for_a_pair_UAVs if pathID != IU_path_ID]
    return ret_reslut_lst


def Select_a_rdm_path_for_a_pair_of_UAVs(UAV1_ID, UAV2_ID):
    candPath = Find_pathID_list_for_a_pair_of_UAVs(UAV1_ID, UAV2_ID)
    idx_targetPath = random.randint(0, len(candPath) - 1)
    return candPath[idx_targetPath]


#===this function will do replacement process when a task assignment or path is changed
def Replace_the_selected_newUAV_or_path_for_a_flow(WF_ID, taskA_ID, taskB_ID, UAVID_old, UAVID_new, pathID_old, pathID_new):
    LogReplacement.write('do replacement for --WF_ID:%d,  taskA_ID:%d, taskB_ID:%d, UAVID_old:%d, UAVID_new:%d, pathID_old:%d, pathID_new:%d\n' % (WF_ID, taskA_ID, taskB_ID, UAVID_old, UAVID_new, pathID_old, pathID_new))
    global var_x_wtk, var_y_wpab
    global len_of_var_y, len_of_var_y_flag
    if UAVID_old != UAVID_new:
        # replace the task to a new UAV
        if (WF_ID, taskB_ID, UAVID_old) in var_x_wtk.keys():
            del var_x_wtk[(WF_ID, taskB_ID, UAVID_old)]
            LogReplacement.write('del var_x_wtk of --WF_ID:%d, taskB_ID:%d, UAVID_old:%d\n' % (WF_ID, taskB_ID, UAVID_old))
        var_x_wtk[(WF_ID, taskB_ID, UAVID_new)] = 1
        LogReplacement.write('set var_x_wtk to 1 -- WF_ID:%d, taskB_ID:%d, UAVID_new:%d\n' % (WF_ID, taskB_ID, UAVID_new))
        
    # change the path to the new UAV
    if (WF_ID, pathID_old, taskA_ID, taskB_ID) in  var_y_wpab.keys():
        del var_y_wpab[(WF_ID, pathID_old, taskA_ID, taskB_ID)]
        LogReplacement.write('del var_y_wpab --WF_ID:%d, pathID_old:%d, taskA_ID:%d, taskB_ID:%d\n' % (WF_ID, pathID_old, taskA_ID, taskB_ID))
    var_y_wpab[(WF_ID, pathID_new, taskA_ID, taskB_ID)] = 1
    LogReplacement.write('set var_y_wpab to 1 --WF_ID:%d, pathID_new:%d, taskA_ID:%d, taskB_ID:%d\n' % (WF_ID, pathID_new, taskA_ID, taskB_ID))
    LogReplacement.write('\n')
    len_of_var_y = len(var_y_wpab)
    if len_of_var_y != len_of_var_y_flag:
        len_of_var_y_flag = len_of_var_y


#===================begin================================================================
def Fake_Replace_UAV_or_Path_for_a_task_to_return_estimated_sysObj(WF_ID, taskA_ID, taskB_ID, UAVID_old, UAVID_new, pathID_old, pathID_new):
    # do replace
    LogReplacement.write('fake replace main\n')
    Replace_the_selected_newUAV_or_path_for_a_flow(WF_ID, taskA_ID, taskB_ID, UAVID_old, UAVID_new, pathID_old, pathID_new)    
    
    # ESTIMATE Xf' after swapping the host-MBox and path;
    Update_system_metrics_in_Main()    
    estimated_sysObj = Get_objVal_of_configurations_in_whole_system()
    # Swap-BACK, after estimating the next-config-objVal.
    LogReplacement.write('swap back main\n')
    Replace_the_selected_newUAV_or_path_for_a_flow(WF_ID, taskA_ID, taskB_ID, UAVID_new, UAVID_old, pathID_new, pathID_old)
    
    return estimated_sysObj
#=======end of function Fake_Replace_UAV_or_Path_for_a_task_to_return_estimated_sysObj==================


# #=====result_list:[(currTask_ID, succTask_ID, needed_bandwidth)...]
def Find_the_flow_list_of_successor_task(WF_ID, task_ID):
    global Info_of_WF
    ret_result_list = []
    if WF_ID in Info_of_WF:
        ret_result_list = [a_flow for a_flow in Info_of_WF[WF_ID] if a_flow[0] == task_ID]
    return ret_result_list   


def Find_the_flow_list_of_predecessor_task(WF_ID, task_ID):
    global Info_of_WF
    ret_result_list = []
    if WF_ID in Info_of_WF:
        ret_result_list = [a_flow for a_flow in Info_of_WF[WF_ID] if a_flow[1] == task_ID]
    return ret_result_list 


def Print_Current_Sys_Info():
    Sys_performance = global_system_throughput - global_weighted_RoutingCost - global_weighted_computeCost
    print "-performance\t%2.3f\t-throughput\t%2.3f\t-RoutingCost\t%2.3f\t-computeCost\t%2.3f\t" % (Sys_performance, global_system_throughput, global_weighted_RoutingCost, global_weighted_computeCost)


def Set_timer_for_all_task_flows(current_ts):
    for WF_ID, lst_task_flows in Info_of_WF.items():
        for a_flow in lst_task_flows:
            taskA_ID, taskB_ID = a_flow[0], a_flow[1]
            Set_timer_for_a_task_flow(current_ts, WF_ID, taskA_ID, taskB_ID)
            

#========================================================================
def Set_timer_for_a_task_flow(current_ts, WF_ID, taskA_ID, taskB_ID):
    feasible_newUAV_ID_rdm = Select_a_rdm_NIU_UAV_for_the_task(WF_ID, taskB_ID)
    if -1 == feasible_newUAV_ID_rdm:
        return
    
    UAVID_new = feasible_newUAV_ID_rdm
    UAVID_old = Get_the_IU_UAV_ID_of_a_task(WF_ID, taskB_ID)
    pathID_old = Get_the_IU_pathID_between_two_task(WF_ID, taskA_ID, taskB_ID)
    # pathID_new = Select_a_rdm_NIU_path_for_the_task(WF_ID, taskA_ID, taskB_ID)
    
    #=========================================
    UAVID_of_TaskA = Get_the_IU_UAV_ID_of_a_task(WF_ID, taskA_ID)
#     while UAVID_of_TaskA == UAVID_new:
#         #print 'hithit'
#         UAVID_new = Select_a_rdm_NIU_UAV_for_the_task(WF_ID, taskB_ID)
    #=========================================
    pathID_new = Select_a_rdm_path_for_a_pair_of_UAVs(UAVID_of_TaskA, UAVID_new)
    Update_system_metrics_in_Main()
    Xf = Get_objVal_of_configurations_in_whole_system()
    
    Xf_prime = Fake_Replace_UAV_or_Path_for_a_task_to_return_estimated_sysObj(WF_ID, taskA_ID, taskB_ID, UAVID_old, UAVID_new, pathID_old, pathID_new)
    
    # write to log
    LogRun.write('WF_ID:%s, taskA_ID:%s, taskB_ID:%s, From UAV %s to UAV %s, old desUAVID:%s\n' % (str(WF_ID), str(taskA_ID), str(taskB_ID), str(UAVID_of_TaskA), str(UAVID_new), str(UAVID_old)))
    LogRun.write('From path %s to path %s\n' % (str(pathID_old), str(pathID_new)))
    LogRun.write('old_path:%s\n' % str(Path_database[pathID_old]))
    LogRun.write('new_path:%s\n' % str(Path_database[pathID_new]))
    LogRun.write('Xf:%f, Xf_prime:%f, gap:%f \n\n' % (Xf, Xf_prime, Xf_prime - Xf))
    
    # print Xf_prime - Xf
    # print 'Xf:%f, Xf_prime:%f, gap:%f'%(Xf, Xf_prime, Xf_prime - Xf)
    exp_item = math.exp(Tau - 0.5 * Beta * (Xf_prime - Xf))
    mean_timer_exp = 1.0 * exp_item / (len(Lst_Assignable_UAV_ID) - 1);
    # print 'exp_item: %f'%exp_item
    lambda_exp_random_number_seed = 1.0 / mean_timer_exp;
    # lambda_exp_random_number_seed = mean_timer_exp
    Timer_val_exp = random.expovariate(lambda_exp_random_number_seed);
    
    Timer_Key = (WF_ID, taskA_ID, taskB_ID)
    if Timer_Key not in Timers.keys():
        Timers[Timer_Key] = [0, 0, -1, -1, -1, -1]
        Timers[Timer_Key][0] = current_ts
        Timers[Timer_Key][1] = Timer_val_exp
        Timers[Timer_Key][2] = pathID_old
        Timers[Timer_Key][3] = pathID_new
        Timers[Timer_Key][4] = UAVID_old
        Timers[Timer_Key][5] = UAVID_new
    else:
        Timers[Timer_Key][0] = current_ts
        Timers[Timer_Key][1] = Timer_val_exp
        Timers[Timer_Key][2] = pathID_old
        Timers[Timer_Key][3] = pathID_new
        Timers[Timer_Key][4] = UAVID_old
        Timers[Timer_Key][5] = UAVID_new
        
#================end of function Set_timer_for_a_task_flow================
        

def Check_expiration_of_timers(current_ts):
    ret_timer_result = {}
    for key, val in Timers.items():
        ts_begin = val[0]
        len_timer = val[1]
        pathID_old = val[2]
        pathID_new = val[3]
        UAVID_old = val[4]
        UAVID_new = val[5]
        
        if current_ts >= ts_begin + len_timer:
            if key not in ret_timer_result.keys():
                ret_timer_result[key] = [-1, -1, -1, -1];
                ret_timer_result[key][0] = pathID_old;
                ret_timer_result[key][1] = pathID_new;
                ret_timer_result[key][2] = UAVID_old;
                ret_timer_result[key][3] = UAVID_new;
                
    return ret_timer_result    


def Delete_expired_timer_items_after_replacement(WF_ID, taskA_ID, taskB_ID):
    if (WF_ID, taskA_ID, taskB_ID) in Timers.keys():
        del Timers[(WF_ID, taskA_ID, taskB_ID)]


def RESET(current_ts):
    Set_timer_for_all_task_flows(current_ts)


def main():
    print "123 main() begin" 
    global step_times
    initialize(CandPaths_file, Info_of_WF_file, CapLinks_file, Info_of_task_file, Info_of_UAVs_file)
    initialize_assign_taAssign_task_to_UAV_randomlym_metrics_in_Main()
    Print_Current_Sys_Info()
    # print (global_system_throughput, global_weighted_RoutingCost, global_weighted_computeCost)
    Set_timer_for_all_task_flows(0.0)
    
    current_ts = 0.0
    last_ts_to_check_timer = 0.0
    
    while(current_ts <= T):
        RESET_Msg = 0
        ##### -- C.1 listen to the event of any timer's expiration.
        if (current_ts - last_ts_to_check_timer >= STEP_TO_CHECK_TIMER):
            # ## --- C.1.0 Update the timer-checking time-slot.
            last_ts_to_check_timer = current_ts
            ret_timer_check_result = Check_expiration_of_timers(current_ts)
            
            if ret_timer_check_result:
                RESET_Msg = 1
                for key, val in ret_timer_check_result.items():
                    WF_ID = key[0]
                    taskA_ID = key[1]
                    taskB_ID = key[2] 
                    pathID_old = val[0];  # # Get the returned pathID_old.
                    pathID_new = val[1];  # # Get the returned pathID_new.
                    UAVID_old = val[2];  # # Get the returned Dst_MBox_cur.
                    UAVID_new = val[3];  # # Get the returned Dst_MBox_new.
                   
                    # do replace
                    LogReplacement.write('true repalce\n')
                    Replace_the_selected_newUAV_or_path_for_a_flow(WF_ID, taskA_ID, taskB_ID, UAVID_old, UAVID_new, pathID_old, pathID_new)    
                    # find the successor task
                
                    Delete_expired_timer_items_after_replacement(WF_ID, taskA_ID, taskB_ID)
                    
        if 1 == RESET_Msg:
            RESET(current_ts)
        
        current_ts += STEP_TO_RUN
        step_times += 1
        performance = global_system_throughput - global_weighted_RoutingCost - global_weighted_computeCost
        LogPerformanceRecord.write("-step:%d\t-performance\t%2.3f\t-throughput\t%2.3f\t-RoutingCost\t%2.3f\t-computeCost\t%2.3f\n" % (step_times, performance, global_system_throughput, global_weighted_RoutingCost, global_weighted_computeCost))
        if (step_times % 1 == 0):
            Update_system_metrics_in_Main()
            Print_Current_Sys_Info()         
                    
    print "finish"


###### =============================== Begin to run ============================== #######
if __name__ == '__main__':


    main()
