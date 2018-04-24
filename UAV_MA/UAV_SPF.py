# coding:utf-8  
'''
Created on 2018-03-13

@author: liubaichuan
'''

import random
import math

#===================== input file name ======================#
CandPaths_file = "input_data/_input_PathSet2.txt"
Info_of_WF_file = "input_data/_input_Info_of_workflow6.txt"
Info_of_task_file = "input_data/_input_Info_of_task6.txt"
CapLinks_file = "input_data/_input_Cap_links10000.txt"
Info_of_UAVs_file = "input_data/_input_Info_of_nodes.txt"

#===================== global variable ======================#
CandPathIDSet_for_2_UAVs = {}  ## {<Src-UAV,Dst-UAV>:[path1_id,path2_id,...]}, the candidate path-set for all  pair of UAVs. !!!! SPECIAL-CASE-20161109: EVEN a SW to itself has an individual path_ID, 2016-1109!!!!!
Path_database = {}  # # {<Path_id>:pathContent}, e.g., pathContent:[(1, 2), (2, 5), (5, 3)]; or EMPTY list [].
Info_of_task = {}  # # {<workflow_id, task_id>:[Cap]}
Info_of_WF = {}  # #{<worlflow_ID>: list_of_a_flow}, list_of_a_flow=[(currTask_ID, succTask_ID, needed_bandwidth)...]
Cap_links = {}  # #   {<u,v>:CapVal}, the Capacity set of all links 
Info_of_Node = {}  # #{<Node_ID>:CapVal}, the compute capacity of all nodes
LstUAV=[]   # list that record the ID of UAVs
LstEdgeServer = [] # list that record the ID of edge server
LstCloudServer = [] # list that record the ID of cloud server
LstNode = []

var_x_wtk = {}  # # {<workflow_ID, task_ID, UAV_ID>: int},x_(k)^(w,t) == 1,if task t of workflow w is assigned  to UAV k
var_y_wpab = {}  # # {<workflow_ID, path_ID, task_a_ID, task_b_ID>}, y_(a,b)^(w,p) == 1, if task a and task b in workflow w use path p to transfer data

#=============================================================
Global_PATH_ID_START_COUNTING = 0  # MUST NOT be changed from 0, 2016-1109.

#=================================================
Aggregated_TR_in_acrs = {}  # {(u,v): aggregated-TR-in-arc-uv }. This variable record the aggregated traffic rate on each UAV link
global_system_throughput = 0.0
global_weighted_RoutingCost = 0.0
global_weighted_computeCost = 0.0
global_weighted_throughput = 0.0
WEIGHT_OF_COMPUTE_COST = 1
WEIGHT_OF_ROUTING_COST = 1
WEIGHT_OF_THROUGHPUT = 1

EdgeServerLinkCoefficient = 5
CloudServerLinkCoefficient = 6

# ==================================== USE-CASE ==============================================
step_times = 0
#=================================================
# Lst_Assignable_UAV_ID = [8, 9, 12, 13, 16, 17, 20, 21, 24, 25]  # list of UAV's ID which can be assigned task
Lst_Assignable_UAV_ID = []  # list of UAV's ID which can be assigned task

#=================================================
# LogRun = open('Log_running.txt', 'w')
# LogVar_X = open('log_Var_X.txt', 'w')
# LogVar_Y = open('log_Var_Y.txt', 'w')
# LogReplacement = open('logReplacement.txt', 'w')
LogPerformanceRecord = open('logPerformance_SPF.txt', 'w')


# read the data from files and 
def initializeReadData(_in_CandPaths_file, _in_Info_of_WF_file, _in_CapLinks_file, _in_Info_of_task_file, _in_Info_of_UAVs_file):
    # ---- 1 Read the Given path data :
    global CandPathIDSet_for_2_UAVs, Path_database, Lst_Assignable_UAV_ID
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
                
                # record the UAV ID which can be assigned to run a task
                if SrcUAV_id not in Lst_Assignable_UAV_ID:
                    Lst_Assignable_UAV_ID.append(SrcUAV_id)
                if DstUAV_id not in Lst_Assignable_UAV_ID:
                    Lst_Assignable_UAV_ID.append(DstUAV_id)
                
                # ## --!! Case-I. (if path=="[]") SPECIAL-CASE-20161109-handling: from each switch to itself, there is no length-positive-path.
                # ## --!! Case-II. (if path!="[]") Normal-case-handling: from each switch to other one, there is length-positive-path.
                # ## --!! We handle both the two cases simultaneously: by analyzing the content of the path.
                One_path_in_seg = [];
                pathContent = strPath.split(">")
                for i in range(len(pathContent)):
                    if i + 1 in range(len(pathContent)):
                        One_path_in_seg.append((str(pathContent[i]), str(pathContent[i + 1])));
    
                # # -- a. !!! We first record the normal-sequence One_path_in_seg for (SrcUAV, DstUAV);
                ## --- a.1 store this new path to path_database. !!!!! One_path_in_seg possibly an EMPTY list [].!!!!
                if unique_PathID_idx not in Path_database:
                    Path_database[unique_PathID_idx] = One_path_in_seg;  ## !!!!! One_path_in_seg possibly an EMPTY list [].!!!!
                
                # # --- a.2 record this path to the CandPathIDSet_for_2_UAVs
                if (SrcUAV_id, DstUAV_id) not in CandPathIDSet_for_2_UAVs:
                    CandPathIDSet_for_2_UAVs[(SrcUAV_id, DstUAV_id)] = [];
                CandPathIDSet_for_2_UAVs[(SrcUAV_id, DstUAV_id)].append(unique_PathID_idx);
                unique_PathID_idx += 1

                # # -- b. !!! We ALSO record the reverse-path for  (SrcUAV, DstUAV), i.e., path for (DstUAV, SrcUAV).
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
                
            # # --- b. initializeReadData the global_Aggregated_TR_in_acrs.
            if (u_id, v_id) not in Aggregated_TR_in_acrs:
                Aggregated_TR_in_acrs[(u_id, v_id)] = 0  # ## ---- 3 Read the Capacity of links:~    
    
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
                
    #---- 5. Read the given Info_of_Node data
    global Info_of_Node
    # _input_Info_of_nodes.txt
    with open(_in_Info_of_UAVs_file, "rU") as f:
        for lines in f:
            line = lines.strip('\n')
            lineContent = line.split("\t")
            node_ID = int(lineContent[1])
            CapVal = float(lineContent[3])
            LstNode.append(node_ID)
                
            if node_ID not in Info_of_Node:
                Info_of_Node[node_ID] = CapVal
  
#==================== end of initializeReadData function===================


# randomly assign task to UAV and find a path for the tasks have communication
def Assign_task_to_UAV_randomly(WFs):
    global CandPathIDSet_for_2_UAVs, Path_database, Info_of_task, Cap_links, Info_of_Node
    global LstUAV
    numOfUAVs = len(LstNode)
    for WF_ID, content in WFs.items():
        for a_flow in content:
            currTaskID = a_flow[0]
            succTaskID = a_flow[1]
            # --- assign the task to the UAV and find the path randomly
            tryNo = 10  #give up assigning this work flow if fail 10 times
            while tryNo > 0:
                # randomly select  UAVs
                idx_UAV1 = random.randint(0, numOfUAVs - 1)
                idx_UAV2 = random.randint(0, numOfUAVs - 1)
                if succTaskID == 0: #0 means this task is a special task to transfer data to the back end, so its UAV should be fixed.
                    idx_UAV2 = numOfUAVs - 1
                if idx_UAV1 == idx_UAV2:    # avoid 2 tasks in a task flow are assigned to the same UAV 
                    # print 'hit'
                    # continue
                    if idx_UAV1 == numOfUAVs - 1:
                        idx_UAV1 -= 1
                    else:
                        idx_UAV1 += 1
                    
                UAV_ID1 = LstNode[idx_UAV1]
                UAV_ID2 = LstNode[idx_UAV2]
                pathID_list = Find_pathID_list_for_a_pair_of_UAVs(UAV_ID1, UAV_ID2)
                if pathID_list:
                    # Find out the shortest paths
                    # 1. get the length of shortest path
                    shortest_len_of_p = 100000
                    for p_id in pathID_list:
                        lenCurP = len(Path_database[p_id])
                        if lenCurP < shortest_len_of_p:
                            shortest_len_of_p = lenCurP
                    # 2. get the shortest paths
                    shortest_paths_id = []
                    for p_id in pathID_list:
                        if len(Path_database[p_id]) == shortest_len_of_p:
                            shortest_paths_id.append(p_id)
                            
                    # randomly select path
                    idx_path = random.randint(0, len(shortest_paths_id) - 1)
                    pathID = shortest_paths_id[idx_path]
                    # check path
                    if not Check_whether_a_path_is_feasible_to_the_taskSegment(pathID, WF_ID, currTaskID, succTaskID):
                        tryNo -= 1
                        continue
                    # assign the task to the UAV
                    if not Check_whether_a_task_has_assignment(WF_ID, currTaskID):
                        var_x_wtk[(WF_ID, currTaskID, UAV_ID1)] = 1
                    if not Check_whether_a_task_has_assignment(WF_ID, succTaskID):
                        var_x_wtk[(WF_ID, succTaskID, UAV_ID2)] = 1
                    
                    # var_y_wpab[WF_ID, pathID, currTaskID, succTaskID] = 1
                    One_a_Path(pathID, WF_ID, currTaskID, succTaskID)
                    print 'WF_ID:%d, taskA:%d, taskB:%d' %(WF_ID, currTaskID, succTaskID)
                    break
#     print 'Assign_task_to_UAV_randomly done'
#=======================end of function Assign_task_to_UAV_randomly========     


#============================================================================
def Check_whether_a_path_is_feasible_to_the_taskSegment(pathID, WF_ID, taskA_ID, taskB_ID):
    global Path_database, Info_of_WF, Cap_links, Aggregated_TR_in_acrs
    path_content = Path_database[pathID]
    if path_content:
        # get the need bandwidth of a task flow
        needed_bandwidth = Get_the_need_bandwidth_of_a_task_flow(WF_ID, taskA_ID, taskB_ID)
        # check whether all the available bandwidth of segment in a path are larger than the needed bandwidth of a task flow
        for segment in path_content:
            aggregated_TR = Aggregated_TR_in_acrs[segment]
            link_cap = Cap_links[segment]
            if link_cap - aggregated_TR < needed_bandwidth:
                # if one of the available bandwidth of segment in a path is unsatisfied, the this path is not feasible
                return 0
    return 1
#============================================================================

     
#============================================================================
def Get_the_need_bandwidth_of_a_task_flow(WF_ID, taskA_ID, taskB_ID):
    global Info_of_WF
    needed_bandwidth = -1
    for val in Info_of_WF[WF_ID]:
        if val[0] == taskA_ID and val[1] == taskB_ID:
            needed_bandwidth = val[2]
            break
    return needed_bandwidth
#============================================================================


#============================================================================
def One_a_Path(pathID, WF_ID, taskA_ID, taskB_ID):
    global Path_database, Info_of_WF, Aggregated_TR_in_acrs
    path_content = Path_database[pathID]
    needed_bandwidth = Get_the_need_bandwidth_of_a_task_flow(WF_ID, taskA_ID, taskB_ID)
    # update the aggregated traffic rate in all segment
    for segment in path_content:
        Aggregated_TR_in_acrs[segment] += needed_bandwidth
        
    var_y_wpab[WF_ID, pathID, taskA_ID, taskB_ID] = 1
#     LogReplacement.write('set var_y_wpab to 1 --WF_ID:%d, pathID_new:%d, taskA_ID:%d, taskB_ID:%d\n' % (WF_ID, pathID, taskA_ID, taskB_ID))
#============================================================================



#============================================================================
def Check_whether_a_task_has_assignment(WF_ID, task_ID):
    for w, t, _ in var_x_wtk:
        if w == WF_ID and t == task_ID:
            # return 1 means the task has assigned to a UAV
            return 1
    # return 0 means the task has not assigned to a UAV
    return 0


#============================================================================
def Find_pathID_list_for_a_pair_of_UAVs(UAV_ID1, UAV_ID2):
    if (UAV_ID1, UAV_ID2) in CandPathIDSet_for_2_UAVs:
        return CandPathIDSet_for_2_UAVs[(UAV_ID1, UAV_ID2)]
    return []


#=====================================================================================
# == If all the task flow of a work flow can be assigned to the UAV swarm then that work flow is satisfied
def Get_list_of_satisfied_WF_ID():
    global var_y_wpab, Info_of_WF
    ret_satisfied_WF_ID = []
    flag_of_a_WF = 0  # denote whether a WF is satisfied or not
    for WF_ID, lst_of_a_flow in Info_of_WF.items():
        flag_of_a_WF = 1
        for a_flow in lst_of_a_flow:
            flag_of_a_flow = 0  # denote whether a task flow is assigned or not
            for w, _, a, b in var_y_wpab:
                if w == WF_ID and a == a_flow[0] and b == a_flow[1]:
                    # if a path can be found for the 2 tasks it means that task flow can is assigned
                    flag_of_a_flow = 1
                    break
            if flag_of_a_flow == 0:
                # if one of the task flow in the WF can not be assigned, then that WF is unsatisfied
                flag_of_a_WF = 0
                break
        if flag_of_a_WF == 1:
            ret_satisfied_WF_ID.append(WF_ID)
    return ret_satisfied_WF_ID
#=========================end of function Get_list_of_satisfied_WF_ID()===============


#============================================================================
# this function find out the ID and information of all unsatisfied workflow
def Get_the_set_of_unsatisfied_WF():
    global Info_of_WF
    result_dict = {}
    lst_satisfied_WF_ID = Get_list_of_satisfied_WF_ID()
    for key, val in Info_of_WF.items():
        if key not in lst_satisfied_WF_ID:
            result_dict[key] = val
    return result_dict
#============================================================================


def Move_unsatisfied_WF_from_UAVs():
    global var_x_wtk
    unsatisfied_WF_lst = Get_the_set_of_unsatisfied_WF()
    for WF_ID in unsatisfied_WF_lst:
        for (workflow_ID, task_ID, UAV_ID) in var_x_wtk.keys():
            if WF_ID == workflow_ID:
                del var_x_wtk[(workflow_ID, task_ID, UAV_ID)]


#=====================================================================================
def Update_system_metrics():
    global Info_of_WF, Path_database, Info_of_Node, Info_of_task
    global global_system_throughput, global_weighted_RoutingCost, global_weighted_computeCost
    global WEIGHT_OF_ROUTING_COST, WEIGHT_OF_COMPUTE_COST
    Move_unsatisfied_WF_from_UAVs()
    system_throughput = 0.0
    routingCost = 0.0
    computeCost = 0.0
    
    lst_of_satisfied_WF_ID = Get_list_of_satisfied_WF_ID()
    
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
                for (UAV_1, UAV_2) in Path_database[IU_PathID]:
#                     print '(%d, %d)'%(UAV1, UAV2)
                    UAV1 = int(UAV_1)
                    UAV2 = int(UAV_2)
                    if UAV2 in LstEdgeServer and UAV1 not in LstEdgeServer:
                        routingCost += 1 * EdgeServerLinkCoefficient
                    elif UAV2 in LstCloudServer and UAV1 not in LstCloudServer:
                        routingCost += 1 * CloudServerLinkCoefficient
                    else:
                        routingCost += 1
                
    # --3 calculate the computation cost
    for key, val in Info_of_Node.items():
        task_list_assigned_to_a_UAV = Get_the_task_list_assigned_to_a_UAV(key)
        total_Cap_of_a_UAV = 0
        for WF_ID, task_ID in task_list_assigned_to_a_UAV:
            if(WF_ID, task_ID) in Info_of_task:
                total_Cap_of_a_UAV += Info_of_task[(WF_ID, task_ID)]
        computeCost += total_Cap_of_a_UAV / val         
    
    # weight the cost
    weighted_routing_cost = WEIGHT_OF_ROUTING_COST * routingCost
    weighted_compute_cost = WEIGHT_OF_COMPUTE_COST * computeCost
    weighted_throughput = WEIGHT_OF_THROUGHPUT * system_throughput
    # # ---- update the current Objectives
    global_system_throughput = weighted_throughput
    global_weighted_RoutingCost = weighted_routing_cost
    global_weighted_computeCost = weighted_compute_cost         
#========end of function Update_system_metrics() ==============================


def Get_objVal_of_configurations_in_whole_system():
    global global_system_throughput
    global global_weighted_RoutingCost
    global global_weighted_computeCost
    return global_system_throughput - global_weighted_RoutingCost - global_weighted_computeCost


# get the in-use path id between 2 task in a task flow
def Get_the_IU_pathID_between_two_task(WF_ID, taskA_ID, taskB_ID):
    global var_y_wpab
    for w, p, a, b in var_y_wpab:
        if w == WF_ID and a == taskA_ID and b == taskB_ID:
            return p
    return -1



# get the tasks assigned to a UAV according to the UAV ID==
def Get_the_task_list_assigned_to_a_UAV(UAV_ID):
    global var_x_wtk
    ret_result_list = []
    for w, t, u in var_x_wtk:
        if u == UAV_ID:
            ret_result_list.append((w, t))
    return ret_result_list    
#==========end of function==================================

def Print_Current_Sys_Info():
    Sys_performance = global_system_throughput - global_weighted_RoutingCost - global_weighted_computeCost
    print "-step:%d  -performance\t%2.2f\t-thr\t%2.2f\t-RoutingCost\t%2.2f\t-computeCost\t%2.2f\t" % (step_times, Sys_performance, global_system_throughput, global_weighted_RoutingCost, global_weighted_computeCost)




def recordAssginmentInfo():
    global var_x_wtk
    final_assignment_info = 'final_assignment_info.txt'
    LogAssignment = open(final_assignment_info, 'w')
    for key, val in var_x_wtk.items():
        if val == 1:
            LogAssignment.write('WF_ID:%d\tTaskID:%d\tnodeID:%d\n'%(key[0], key[1], key[2]))
    LogAssignment.close()
    
    

def main():
    print "123 main() begin" 
    global step_times, Timers, Info_of_WF
    initializeReadData(CandPaths_file, Info_of_WF_file, CapLinks_file, Info_of_task_file, Info_of_UAVs_file)
    Assign_task_to_UAV_randomly(Info_of_WF)
    LogPerformanceRecord.write('running under setting:\n')
    settingStr = CandPaths_file + '\t' + Info_of_WF_file + '\t' + Info_of_task_file + '\t' + CapLinks_file + '\t' + Info_of_UAVs_file + "\n"
    LogPerformanceRecord.write(settingStr + '\n')
    Update_system_metrics()
    # calculate the performance
    performance = global_system_throughput - global_weighted_RoutingCost - global_weighted_computeCost
    # record the system performance information
    LogPerformanceRecord.write("-step:%d  -performance\t%2.2f\t-thr\t%2.2f\t-RoutingCost\t%2.2f\t-computeCost\t%2.3f\n" % (step_times, performance, global_system_throughput, global_weighted_RoutingCost, global_weighted_computeCost))
    Print_Current_Sys_Info()
    # print (global_system_throughput, global_weighted_RoutingCost, global_weighted_computeCost)
    
    #record the final assignment of all task 
    recordAssginmentInfo()
    LogPerformanceRecord.close()        
    print "finish"


###### =============================== Begin to run ============================== #######
if __name__ == '__main__':


    main()
