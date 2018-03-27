import random
from sys import stdin
from idlelib.ReplaceDialog import replace

rangeOfBandwidth = 100
rangeOfCap = 1000

input_Info_of_workflow = '_input_Info_of_workflow1.txt'
input_Info_of_task = '_input_Info_of_task1.txt' 

output_file_workflow = '_input_Info_of_workflow5.txt'
output_file_task = '_input_Info_of_task5.txt'

new_workflow_file = open(output_file_workflow, 'w')
new_task_file = open(output_file_task, 'w')

print output_file_workflow
print output_file_task

with open(input_Info_of_workflow, "rU") as f:
    for lines in f:
            line = lines.strip()
            if len(line) > 0:
                lineContent = line.split('\t')
                new_rdm_bandwidth = random.randint(10, rangeOfBandwidth)
                lineContent[len(lineContent)-1] = str(new_rdm_bandwidth)
                new_str = ''
                for strContent in lineContent:
                    new_str += strContent + '\t'
                new_str += '\n'
                new_workflow_file.write(new_str)
new_workflow_file.close()
                
                
with open(input_Info_of_task, 'rU') as f:
    for lines in f:
        line = lines.strip()
        if len(line) > 0:
            lineContent = line.split('\t')
            new_rdm_cap = random.randint(50, rangeOfCap)
            lineContent[len(lineContent)-1] = str(new_rdm_cap)
            new_str = ''
            for strContent in lineContent:
                new_str += strContent + '\t'
            new_str += '\n'
            new_task_file.write(new_str)
new_task_file.close()

print 'finish processing'