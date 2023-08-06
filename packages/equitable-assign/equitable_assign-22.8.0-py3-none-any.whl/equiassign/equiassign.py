import random
import argparse
import csv
import os.path

__all__ = ['assign']

# TODO (1) run through pep8 tool and maybe pyflakes

def assign(A: int, N: int, K: int, verbose=True, **kwargs):
    """ 
    Generates a random assignment of tasks to workers.
    
    Variables (all positive integers):
            - A total number of tasks
            - N workers
            - K number of worker assigned to each task

    Returns: 
        an array of arrays

    Algorithm:
    We are going to think of this in a manner of how we could assign workers to a comittee if we were all in a physical environment.

    First, we will make K slips for each task and label them. Thus, we will have A*K slips in total.

    Second, we will take all these slips, put them in a hat, and shake them up.

    Third, we will line up all the workers in a single file line and then go one by one giving them a single slip and then wrap back around once we have gone to the end of the line.
    If the worker already has one of the slips we assign them we will give them a new slip and put that one back in the hat.

    It is possible that towards the end some of the workers will already have all the slips that are in the remaining hat so they will be skipped and another worker could be given more. 
    Hence, an unoptimal assignments of tasks. We address this by having the worker with the most tasks give one of their assigments to the worker with the fewest. 

    >>> assign(5,4,3)
    >>> [[1, 2, 3, 5], [1, 2, 3, 4], [1, 3, 4, 5], [2, 4, 5]]

    """

# TODO (2) add code coverage checking.
    #if the user inputed a larger number of workers per task than there are workers 
    if(N<K):  
        raise ValueError("pertask needs to be smaller than workers")
    #if any are negative 
    if(A <= 0 or N<= 0 or K<= 0):
        raise ValueError("need postive integers for all arguments")
    
    #make the A*K slips in an array
    slips = []
    for i in range(1, A+1):
        for j in range(0, K): #we could probably do this with numpy to
            slips.append(i)

    #shake up the hat
    random.shuffle(slips)

    #line the people up i.e. make a dictionary with an array
    #to store many values 
    line_of_rev_dict = {}
    for i in range(1,N+1):
        line_of_rev_dict[_worker_key(i)] = []

    #go through each worker and give them something from the hat
    i = 1 
    while(i>-1): #we will run this until we break out of it
        i = i%N
        if(i==0):
            i = N
        #hand them the slip if they don't have it 
        for j in range(0,len(slips)):
            if slips[j] not in line_of_rev_dict[_worker_key(i)]:
                line_of_rev_dict = _add_values_in_dict(line_of_rev_dict, _worker_key(i), [slips[j]])
                slips.pop(j)
                break
        if not slips: #once we run out of slips break out of the function
            break
        i += 1

    #trade until they are at equatiably assigned 

    #if they can be perfectly assigned 
    if(((A*K)%N)==0):
         while(len({len(x) for x in line_of_rev_dict.values()}) > 1):
            _trade(line_of_rev_dict)
    else: #if they can't be perfectly assigned 
        while(len({len(x) for x in line_of_rev_dict.values()}) > 2):
            _trade(line_of_rev_dict)

    #put the dictionary into a list of lists 
    alpha = list(list(sub) for sub in line_of_rev_dict.values()) 
    
    #sort the list of lists
    for i in range(0,len(alpha)):
        alpha[i] = sorted(alpha[i])

    return alpha  


def _worker_key(i):
    """
    helper function for making worker key
    """
    return "worker{0}".format(i) 


def _trade(d):
    """
    take the person with the most slips and donate one to the person
    with the lowest slips
    """
    mx_key = max(d.items(), key = lambda x: len(x[1]))[0]
    mn_key = min(d.items(), key = lambda x: len(x[1]))[0]
    #take an element from the array of the key with the most 
    #tasks and give one of those tasks to the lowest 
    for i in range(0,len(d[mx_key])):
        if d[mx_key][i] not in d[mn_key]:
            t = d[mx_key].pop(i)
            d[mn_key].append(t)
            break      
    return list(d.values())


def _add_values_in_dict(sample_dict, key, list_of_values):
    ''' Append multiple values to a key in 
        the given dictionary '''
    if key not in sample_dict:
        sample_dict[key] = list()
    sample_dict[key].extend(list_of_values)
    return sample_dict


def _worker_view(data):
    #add a None to all the lists that are less than the longest one 
    dataMaxLen = max([len(x) for x in data])
    for i in data:
        if(len(i) < dataMaxLen):
            i.append(None)  

    #I would add a worker to each list so we can identify them
    for i in range(0,len(data)):
        data[i].insert(0,i+1)


    #make a fields label which will first have worker then the max of how many tasks there will be per worker    
    fields = ["worker"]
    for i in range(1,max([len(x) for x in data])):
        fields.append("task{0}".format(i))

    #put them in a csv file
    with open(args.allworkers,'w') as out:
        file_writer=csv.writer(out)
        file_writer.writerow(fields)
        file_writer.writerows(data) 


def _task_view(data,A):
     #tranform data from being lists of tasks and the task they need to do to lists of tasks and their corresponding worker 
    tasksArr = [[] for x in range(A)]

     #loop through data and see which workers have the tasks and then assign them to that array in tasksArr
    for i in range(1,A+1):
        for j in range(0,len(data)):
            if(i in data[j]):
                tasksArr[i-1].append(j+1) 

    for i in range(0,len(tasksArr)):
        tasksArr[i].insert(0,i+1)

    #make a fields label which will first have worker then the max of how many tasks there will be per worker    
    fields = ["task"]
    for i in range(1,K+1):
        fields.append(_worker_key(i))

    with open(args.allworkers,'w') as out:
        file_writer=csv.writer(out)
        file_writer.writerow(fields)
        file_writer.writerows(tasksArr) 


def _dir_view(dirname,data):
    #error if the directory already exists
     if not ( os.path.isdir(dirname)):
        #make the directory
        os.mkdir(dirname)
        #loop through each list in data and generate a file for that list
        for i in range(0,len(data)):
            file_name = dirname + "/" + _worker_key(i+1)
            for j in range(0,len(data[i])):
                with open(file_name, 'a') as out:
                    file_writer=csv.writer(out)
                    file_writer.writerow([data[i][j]])
     else:
         print("directory already exists")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a random equitable assignment of tasks to workers.')

# TODO (1) add documentation for these, and main documentation
    parser.add_argument('--tasks',type=int,required=True, help='number of tasks')
    parser.add_argument('--workers',type=int,default=2,help='total number of workers, default to 2')
    parser.add_argument('--pertask',type=int,default=1,help='number of workers required per task')
    parser.add_argument('--viewtype',type=int,default=0,help='whether you want the default worker view (0), task view (1), or directory (2)')
    parser.add_argument('--seed',type=int,default=None,help='ensure the same random assignment, useful for reproducing assignments')
    parser.add_argument('--allworkers',type=str,default=True,help='csv file where ouput will be printed')
    parser.add_argument('--dirname',type=str,default=True,help='this will make a directory with a file for each individual worker containing all of their task assignments')

    args = parser.parse_args()

    A = args.tasks
    N = args.workers
    K = args.pertask
    random.seed(args.seed)
    
    #put an error if tasks.csv already exists and no dirname
    file_exists = os.path.exists(args.allworkers)
    if(file_exists and args.viewtype != 2):
        print("The csv file already exists so please delete or rename it") 

    #make the assignments 
    data = assign(A,N,K)

    #worker view
    if(not file_exists and args.viewtype == 0):
        _worker_view(data)
        
     #task view
    if(not file_exists and args.viewtype == 1):
        _task_view(data, A)
    
    #directory view
    if(args.viewtype == 2):
        _dir_view(args.dirname,data)
