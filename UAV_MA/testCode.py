dict = {}
worlflowID = 1
taskID = 2
UAVID = 3
dict[(worlflowID, taskID, UAVID)] = 1
dict[(worlflowID, taskID, UAVID)] = 3
for val in dict.values():
    print val
    
dict[(2,3,4)] = 7
dict[(3,4,5)] = 8
for i, j, k in dict:
    print (i, j, k)