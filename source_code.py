#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np, random, operator, pandas as pd, matplotlib.pyplot as plt
import tsplib95,time,copy,datetime
import matplotlib as mpl
mpl.rc('figure', max_open_warning = 0)


# In[2]:


# Each node is being represented with a Node class. 
class Node:
    def __init__(self, node_id, x, y):
        self.x = x
        self.y = y
        self.node_id = node_id
    
    # The distance function calculates EUC_2D distance between the existing node to a given node. EUC_2D is the
    # 2D Euclidean distance. Round operation is used to round the float number to the nearest integer.(It has same
    # functionality with NINT() in C.)
    def distance(self, node):
        xDis = abs(self.x - node.x)
        yDis = abs(self.y - node.y)
        distance = round(np.sqrt((xDis ** 2) + (yDis ** 2)))
        return distance
    
    def __repr__(self):
        #return "(" + str(self.x) + "," + str(self.y) + ")"
        return str(self.node_id)


# In[3]:


# All nodes taken from the TSP dictionary is placed in a list. The type of the list is a Node list. All items are in the 
# Node class which represent Nodes in the tsp file.

def read_tsp(file_name,city_count):
    # With tsplib95 package the tsp file is assessed easly as dictionary.
    nodes = tsplib95.load(file_name)
    node_dict = nodes.node_coords

    nodeList = []

    for i in range(1,city_count+1):
        nodeList.append(Node(node_id = i, x=node_dict[i][0], y=node_dict[i][1]))
        
    return nodeList


# In[4]:


# Initialization: 80% of the population is initialized randomly. For the remaining part, we 
# consider nearest-neighbor strategy, a very simple and intuitive way for initialization. In 
# this strategy, first a city x is selected randomly. Then, it selects the city that is closest to 
# city x and that has not been selected yet; now the new city becomes the base and this 
# step is repeated until all cities are selected. Note that it will prevent duplicates of 
# selecting the first city “x”.

def createRandomRoute(nodeList):
    # Route is created with selecting random nodes from the list.
    route = random.sample(nodeList, len(nodeList))
    return route

def createNearestNeighborRoute(nodeList):
    node_list_copy = copy.copy(nodeList)
    route = []
    # First select a random node from the list. And append it to the route.
    init_node = random.sample(node_list_copy,1)[0]
    route.append(init_node)
    node_list_copy.remove(init_node)
    # Find the nearest neigbor to the last appended node in the route. And append the nearest node to the route.
    # Iterate this until all nodes exhausted.
    while(len(node_list_copy) != 0):
        nearest_node = findNearestNeighbor(node_list_copy,route[-1])
        route.append(nearest_node)
        node_list_copy.remove(nearest_node)
    return route

def findNearestNeighbor(nodeList,init_node):
    # Find the nearest neighbour in the list to the selected init_node.
    min_distance = 10000000000
    nearest_node = None
    for i in range(len(nodeList)):
        calculated_dist = init_node.distance(nodeList[i])
        if calculated_dist < min_distance:
            min_distance = calculated_dist
            nearest_node = nodeList[i]
    return nearest_node

def initiatePopulation(nearest_neighbor_routes_rate,population_size,nodeList):
    # Poplution is initialized with random selected routes and with the routes created with nearest neighbor nodes.
    # The rate between these two types of routes is determined by nearest_neighbor_routes_rate parameter.
    population = []
    population_distances = []
    # First initiate the individuals that is created with nearest neighbor nodes. A temporary list is used and 
    # all selected first nodes is saved in this list in order to memorize for further selections. If the newly
    # selected node exists in the temp list then the random selection process will repeat. 
    tmp_list = []
    for i in range(int(nearest_neighbor_routes_rate*population_size)):
        individual = createNearestNeighborRoute(nodeList)
        while (individual[0] in tmp_list) and (len(tmp_list) < len(individual)):
            individual = createNearestNeighborRoute(nodeList)
        tmp_list.append(individual[0])
        if len(tmp_list) == len(individual)+1:
            break
        population.append(individual)
        
    # Second initiate the individuals that is created with randomly selected nodes.
    for i in range(population_size - int(nearest_neighbor_routes_rate*population_size)):
        individual = createRandomRoute(nodeList)
        population.append(individual)
    
    # Calculate all distances of all routes in the population for later use.
    for i in range(len(population)):
        population_distances.append(calculateFitness(population[i]))
        
    return population,population_distances


def calculateFitness(route):
    # Calculates total distance of the route. The distance between the last element and the first element is also added because
    # of the route is cyclic.
    route_distance = 0
    for i in range(len(route)):
        node = route[i]     
        # If the node is the last element then calculate the distance of the node and the first node.
        if route[i] == route[-1]:
            next_node = route[0]
        else:
            next_node = route[i+1]
        route_distance = route_distance + node.distance(next_node)
        #print("node: ",node," Next node: ",next_node," Distance: ",node.distance(next_node))
    return route_distance
        
def find_node(route,n_id):
    for i in range(len(route)):
        if route[i].node_id == n_id:
            return i
        
        
def calculateBestFitness(population_distances):
    return min(population_distances)

def calculateAverageFitness(population_distances):
    return sum(population_distances) / len(population_distances)
    


# In[5]:


# Crossover Operator: Two different crossover operators will be implemented:  
# Order Crossover (OX) and Sequential Constructive Crossover (SCX).

def orderedCrossover(parent1,parent2):
    # This function performs ordered crossover for given two parents. The output is a tuple of two children. 
    child1 =[None for i in range(len(parent1))]
    child2=[None for i in range(len(parent2))]
    
    # First and the second cut orders are selected randomly.
    orderA = int(random.random() * len(parent1))
    orderB = int(random.random() * len(parent1))
    start_order = min(orderA, orderB)
    end_order = max(orderA, orderB)
    
    # The nodes between the start_order and end_order of parent1 are copied to child1 in same order. Also perform this
    # operation with parent2 and child2.
    for i in range(start_order, end_order):
        child1[i] = parent1[i]
        child2[i] = parent2[i]

    # After copying the first parent1's cut part to Child1, the remainder None places of child1 is filled with parent2's
    # nodes. If the selected node of parent2 is already exist in child1 then order passes to next node of parent2. With
    # repeating this operation all None nodes of child1 is filled with parent2's nodes in same order.
    child1_indice = end_order
    parent2_indice = end_order
    while None in child1:
        if parent2[parent2_indice] not in child1:
            child1[child1_indice] = parent2[parent2_indice]
            child1_indice = child1_indice+1
            parent2_indice = parent2_indice+1
        else:
            parent2_indice = parent2_indice+1

        if parent2_indice == len(parent2):
            parent2_indice = 0
        if child1_indice == len(child1):
            child1_indice = 0
            
    # After copying the first parent2's cut part to Child2, the remainder None places of child2 is filled with parent1's
    # nodes. If the selected node of parent1 is already exist in child2 then order passes to next node of parent1. With
    # repeating this operation all None nodes of child1 is filled with parent1's nodes in same order.
    child2_indice = end_order
    parent1_indice = end_order
    while None in child2:
        if parent1[parent1_indice] not in child2:
            child2[child2_indice] = parent1[parent1_indice]
            child2_indice = child2_indice+1
            parent1_indice = parent1_indice+1
        else:
            parent1_indice = parent1_indice+1

        if parent1_indice == len(parent1):
            parent1_indice = 0
        if child2_indice == len(child2):
            child2_indice = 0        
            
    return (child1,child2)

def sequentialConstructiveCrossover(parent1,parent2):
    # Literature reference: "Genetic Algorithm for the Traveling Salesman Problem using Sequential Constructive Crossover 
    # Operator." (Zakir H. Ahmed)
    
    # This function performs Sequential Constructive Crossover operation with the given two parents. And produces
    # one child. 
    
    child = []
    
    # First, the first node of parent1 is taken to child as first node.
    child.append(parent1[0])
    child_indice = 0
    
    # Finds the next node of the last selected node of child in both parents. Then calculate the distences between the last
    # node of the child and the next nodes in both parents. Keep the nearest node as the next node in child. Iterate this
    # operation until the child is completed.
    
    while child_indice < len(parent1)-1:
        # Find the legitimate node for parent1 which comes after childs last node.
        for node_indice in range(len(parent1)):
            if parent1[node_indice] == child[child_indice]:
                parent1_candidate_indice = node_indice+1
                if parent1_candidate_indice == len(parent1):
                    parent1_candidate_indice = 0
                if parent1[parent1_candidate_indice] in child:
                    # There is no legitimate node in parent1 so the candidate will be selected sequentially from parent1.
                    #for indice in range(len(parent1)):
                    #    if parent1[indice] not in child:
                    #        parent1_candidate_indice = indice
                    #        break
                    # There is no legitimate node in parent1 so the candidate will be selected sequentially from parent1.
                    parent1_nodes = range(1,len(parent1)+1)
                    for node in parent1_nodes:
                        indice = find_node(parent1,node)
                        if parent1[indice] not in child:
                            parent1_candidate_indice = indice
                            break
                    
                        
        # Find the legitimate node for parent2 which comes after childs last node.
        for node_indice in range(len(parent2)):
            if parent2[node_indice] == child[child_indice]:
                parent2_candidate_indice = node_indice+1
                if parent2_candidate_indice == len(parent2):
                    parent2_candidate_indice = 0
                if parent2[parent2_candidate_indice] in child:
                    # There is no legitimate node in parent2 so the candidate will be selected sequentially from parent2.
                    #for indice in range(len(parent2)):
                    #    if parent2[indice] not in child:
                    #        parent2_candidate_indice = indice
                    #        break
                    parent2_nodes = range(1,len(parent2)+1)
                    for node in parent2_nodes:
                        indice = find_node(parent2,node)
                        if parent2[indice] not in child:
                            parent2_candidate_indice = indice
                            break
                            
        # Calculate the distances between the last node of child and the legitimate nodes selected in both parent1 and parent2.
        dist1 = child[child_indice].distance(parent1[parent1_candidate_indice])
        dist2 = child[child_indice].distance(parent2[parent2_candidate_indice])
        
        # If distance between child last node and parent1's candidate is less than child's last node and parent2's candidate
        # then choose parent1's candidate.And choose parent2's candidate in reverse condition.
        if dist1 < dist2:
            child.append(parent1[parent1_candidate_indice])
        else:
            child.append(parent2[parent2_candidate_indice])
        child_indice = child_indice + 1
    
    
    return child


# In[6]:


# Literature reference: "Combined Mutation Operators of Genetic Algorithm for the Travelling Salesman problem"
# (Kusum Deep, Hadush Mebrahtu) 

# There will be four types of mutation operators which are the insertion mutation (ISM), 
# the inversion mutation (IVM) and the swap mutation (SM), and the random mutation (RM).

def insertionMutation(route, mutation_probability):
    # The insertion mutation is applied based on insertion mutation probability with first if check. 
    if(random.random() < mutation_probability):
        # Both the node that is to be inserted and its place indice to be inserted is selected randomly(insertion_indice,
        # insert_node_indice).
        insertion_indice = int(random.random() * len(route))
        new_route = [None for i in range(len(route))]
        insert_node_indice = int(random.random() * len(route))
        new_route[insertion_indice] = route[insert_node_indice]
        new_route_indice=0
        # The insertion operation is performed based on the randomly selected values and the indexes shifted accordingly.
        while None in new_route:
            for route_indice in range(len(route)):
                if route[route_indice] not in new_route:
                    new_route[new_route_indice] = route[route_indice]
                    new_route_indice = new_route_indice + 1
                    if new_route_indice == len(route):
                        new_route_indice = 0
                    while (new_route[new_route_indice] != None) and (None in new_route):
                        new_route_indice = new_route_indice + 1
        return new_route
    return route
                    

def swapMutation(route, mutation_probability):
    # The swap mutation operator simply select two nodes randomly and swaps them in place.
    if(random.random() < mutation_probability):
        #new_route = [None for i in range(len(route))]
        new_route = copy.copy(route)
        first_node_indice = int(random.random() * len(route))
        second_node_indice = int(random.random() * len(route))
            
        node1 = route[first_node_indice]
        node2 = route[second_node_indice]

        new_route[first_node_indice] = node2
        new_route[second_node_indice] = node1

        return new_route
    return route

def inversionMutation(route, mutation_probability):
    # The inversion operator randomly selects two nodes and replace the all nodes in between two random nodes in inverse 
    # order. All remainder nodes stays as input order.
    if(random.random() < mutation_probability):
        first_node_indice = int(random.random() * len(route))
        second_node_indice = int(random.random() * len(route))
        new_route = [None for i in range(len(route))]
        if first_node_indice < second_node_indice:
            for (old_indice,new_indice) in zip(range(first_node_indice,second_node_indice),range(second_node_indice,first_node_indice, -1)):
                new_route[old_indice+1] = route[new_indice]
        else:
            for (new_indice,old_indice) in zip(range(second_node_indice,first_node_indice),range(first_node_indice,second_node_indice, -1)):
                new_route[new_indice+1] = route[old_indice]

        # After selected nodes and the nodes in between them are placed in newly created route, all remained nodes(which are
        # None) will be replaced with the existing nodes of inpute route in the same order.
        new_route_indice=0                
        while None in new_route:
            for route_indice in range(len(route)):
                if route[route_indice] not in new_route:
                    new_route[new_route_indice] = route[route_indice]
                    new_route_indice = new_route_indice + 1
                    if new_route_indice == len(route):
                        new_route_indice = 0
                    while (new_route[new_route_indice] != None) and (None in new_route):
                        new_route_indice = new_route_indice + 1
        return new_route
    return route

def randomMutation(route, mutation_probability):
    # Random mutation operator selects a random mutation operator among Inversion, Swap and Insertion Mutation.
    selection = int(random.random() * 3)
    if selection == 0:
        new_route = insertionMutation(route, mutation_probability)
    elif selection == 1:
        new_route = swapMutation(route, mutation_probability)
    else:
        new_route = inversionMutation(route, mutation_probability)
    return new_route


# In[7]:


def parentSelection(population,population_distances,mating_pool_individuals_count):
    # This function create a mating pool with 5 individuals selected randomly from the population.
    mating_pool = []
    for individual in range(mating_pool_individuals_count):
        mating_pool.append(int(random.random() * len(population)))
    
    # After the mating pool which includes parent indices taken randomly from population is created, the two parents that have
    # minimum total distance will be elected as mating parents.
    # Selection of first parent:
    minimum_distance = 1000000000
    elected_parent1 = None
    for route_indice in mating_pool:
        total_distance = population_distances[route_indice]
        if total_distance < minimum_distance:
            minimum_distance = total_distance
            elected_parent1 = route_indice
    mating_pool.remove(elected_parent1)
    # Selection of second parent:
    minimum_distance = 1000000000
    elected_parent2 = None
    for route_indice in mating_pool:
        total_distance = population_distances[route_indice]
        if total_distance < minimum_distance:
            minimum_distance = total_distance
            elected_parent2 = route_indice        
    
    return (population[elected_parent1],population[elected_parent2])

def survivorSelection(child,population,population_distances):
    # Since the algorithm is a steady-state GA in each iteration, only a part of the population is replaced by the offsprings.
    # The offsprings will be written in place of two worst individuals of the population
    
    #Get worst individual from the population for replacing with the child.
    worst_individual_indice = population_distances.index(max(population_distances))
    
    # Replace the given child with the least performing individual in the population.
    population[worst_individual_indice] = child
    population_distances[worst_individual_indice] = calculateFitness(child)    
    return population,population_distances
    
    


# In[8]:


def twoOptOperator(individual,n):
    # This function applies 2-opt on the given individual n times. 2
    # n : 2-opt operator is applied on the selected individual n times. 
    
    for i in range(n):
        individual_distance = calculateFitness(individual)
        indice1 = int(random.random() * len(individual))
        indice2 = int(random.random() * len(individual))
        first_node_indice = min(indice1,indice2)
        second_node_indice = max(indice1,indice2)
        new_route = [None for i in range(len(individual))]
        path_to_be_reversed = individual[first_node_indice:second_node_indice]
        new_route[first_node_indice:second_node_indice] = path_to_be_reversed[::-1]
        new_route[:first_node_indice] = individual[:first_node_indice]
        new_route[second_node_indice:] = individual[second_node_indice:]

        new_route_distance = calculateFitness(new_route)
        if individual_distance > new_route_distance:
            individual = new_route
    return individual


# In[9]:


# A final function to perform a single iteration based on given inputs.
def generate_GA(population,population_distances,crossover_operator,mutation_operator,generation_count,m=0,n=0,k=0):
    iteration = []
    best_solution = []
    average_solution = []
    df_best_rank_for_all_iterations = pd.DataFrame()
    df = pd.DataFrame(columns=["Generation","Best Solution"])
    for i in range(generation_count+1):
        # The following control is to check if 2-opt operator will be applied to the population.
        if k != 0:
            if i % k == 0:
                # Apply 2-Opt operator to the randomly selected m individuals from the population.
                for j in range(m):
                    individual_indice = int(random.random() * len(population))
                    # twoOptOperator performs 2-opt operation n times to the given individual.
                    individual = twoOptOperator(population[individual_indice],n)
                    population[individual_indice] = individual
                    population_distances[individual_indice] = calculateFitness(individual)
                    
        parent1,parent2 = parentSelection(population,population_distances,mating_pool_individuals_count)
        if crossover_operator == "OX":
            child1,child2 = orderedCrossover(parent1,parent2)
            if mutation_operator == "ISM":
                mutated_child1 = insertionMutation(child1, mutation_probability)
                mutated_child2 = insertionMutation(child2, mutation_probability)
                population,population_distances = survivorSelection(mutated_child1,population,population_distances)
                population,population_distances = survivorSelection(mutated_child2,population,population_distances)
            elif mutation_operator == "IVM":
                mutated_child1 = inversionMutation(child1, mutation_probability)
                mutated_child2 = inversionMutation(child2, mutation_probability)
                population,population_distances = survivorSelection(mutated_child1,population,population_distances)
                population,population_distances = survivorSelection(mutated_child2,population,population_distances)
            elif mutation_operator == "SM":
                mutated_child1 = swapMutation(child1, mutation_probability)
                mutated_child2 = swapMutation(child2, mutation_probability)
                population,population_distances = survivorSelection(mutated_child1,population,population_distances)
                population,population_distances = survivorSelection(mutated_child2,population,population_distances)
            #elif mutation_operator == "RM":
            else:
                mutated_child1 = randomMutation(child1, mutation_probability)
                mutated_child2 = randomMutation(child2, mutation_probability)
                population,population_distances = survivorSelection(mutated_child1,population,population_distances)
                population,population_distances = survivorSelection(mutated_child2,population,population_distances)  
        else:
            child1 = sequentialConstructiveCrossover(parent1,parent2)
            if mutation_operator == "ISM":
                mutated_child1 = insertionMutation(child1, mutation_probability)
                population,population_distances = survivorSelection(mutated_child1,population,population_distances)
            elif mutation_operator == "IVM":
                mutated_child1 = inversionMutation(child1, mutation_probability)
                population,population_distances = survivorSelection(mutated_child1,population,population_distances)
            elif mutation_operator == "SM":
                mutated_child1 = swapMutation(child1, mutation_probability)
                population,population_distances = survivorSelection(mutated_child1,population,population_distances)
            #elif mutation_operator == "RM":
            else:
                mutated_child1 = randomMutation(child1, mutation_probability)
                population,population_distances = survivorSelection(mutated_child1,population,population_distances)
        iteration.append(i)
        best_solution.append(calculateBestFitness(population_distances))
        average_solution.append(calculateAverageFitness(population_distances))
        if i == 1000:
            best_rank = calculateBestFitness(population_distances)
            #average_rank = calculateAverageFitness(population_distances)
            df.loc[-1] = [i, best_rank]
            df.index = df.index + 1        
        elif i == 10000:
            best_rank = calculateBestFitness(population_distances)
            #average_rank = calculateAverageFitness(population_distances)
            df.loc[-1] = [i, best_rank]
            df.index = df.index + 1 
        elif i == 20000:
            best_rank = calculateBestFitness(population_distances)
            #average_rank = calculateAverageFitness(population_distances)
            df.loc[-1] = [i, best_rank]
            df.index = df.index + 1 
    df_best_rank_for_all_iterations["iteration"] = iteration
    df_best_rank_for_all_iterations["best_solution"] = best_solution
    df_best_rank_for_all_iterations["average_solution"] = average_solution
    return df,df_best_rank_for_all_iterations


# In[10]:


def generate_neighbor(route):
    return swapMutation(route, mutation_probability = 1)

def calculate_acceptance_probability(delta_E,temperature):
    return 2.71828 ** (-delta_E/temperature) # e^(-delta_E / temperature)

def generate_SA(node_list,Tmax,Tmin,moves_per_temperature,cooling_rate):
    best_result = 100000000
    total_num_of_generations = 0
    t1 = datetime.datetime.now()
    individual = createRandomRoute(node_list)   # Random initiation.
    T = Tmax
    while T > Tmin:
        for i in range(moves_per_temperature):
            neighbor = generate_neighbor(individual) # Generate a random neighbor.
            total_num_of_generations = total_num_of_generations + 1
            individual_fitness = calculateFitness(individual)
            neighbor_fitness = calculateFitness(neighbor)
            delta_E = neighbor_fitness - individual_fitness
            if delta_E < 0:               # Accept the neighbor solution. 
                individual = neighbor
                if individual_fitness < best_result: best_result = individual_fitness
            else:
                probability = calculate_acceptance_probability(delta_E,temperature = T)
                if random.random() < probability: # Accept if the calculated probability.
                    individual = neighbor
                    if individual_fitness < best_result: best_result = individual_fitness
            #print("Temp: ",T,"Move: ",i,"Fitness: ",individual_fitness)
        T = T * cooling_rate                        # For Cooling Schedule.(Geometric)
    t2 = datetime.datetime.now()
    running_time = (t2-t1).seconds
    return best_result,total_num_of_generations,running_time


# ## Experiment 1

# In[106]:


# Experiment 1: Performance of SA with Respect to different cooling schedules.

file_name = 'kroA100.tsp'             # Num of cities:100, Best ratig: 21282
city_count = 100                      # Number of city.
seed_counter = 1 
node_list = read_tsp(file_name,city_count)

# SA CASE 1:

# SA Parameters
Tmax = 10000                          # Initial Temperature.
Tmin = 0.01                           # For the stopping condition. 
moves_per_temperature = 10            # For the equilibrium state.
cooling_rate = 0.95                   # For the cooling schedule.

best_res_1 = 1000000
total_best_1 = 0
total_run_time_1 = 0
random.seed(seed_counter)

for i in range(100):
    best_result_1,total_num_of_generations_1,running_time_1 = generate_SA(node_list,Tmax,Tmin,moves_per_temperature,cooling_rate)
    if best_result_1 < best_res_1: best_res_1 = best_result_1
    total_best_1 = total_best_1 + best_result_1
    total_run_time_1 = total_run_time_1 + running_time_1
average_result_1 = total_best_1/100

# SA CASE 2:

# SA Parameters
Tmax = 10000                         # Initial Temperature.
Tmin = 0.01                          # For the stopping condition. 
moves_per_temperature = 2            # For the equilibrium state.
cooling_rate = 0.995                 # For the cooling schedule.

best_res_2 = 1000000
total_best_2 = 0
total_run_time_2 = 0
random.seed(seed_counter)

for i in range(100):
    best_result_2,total_num_of_generations_2,running_time_2 = generate_SA(node_list,Tmax,Tmin,moves_per_temperature,cooling_rate)
    if best_result_2 < best_res_2: best_res_2 = best_result_2
    total_best_2 = total_best_2 + best_result_2
    total_run_time_2 = total_run_time_2 + running_time_2
average_result_2 = total_best_2/100

print("Case 1, Total Run Time: ",total_run_time_1,", Best Result: ",best_res_1,", Average Result: ",average_result_1)
print("Case 2, Total Run Time: ",total_run_time_2,", Best Result: ",best_res_2,", Average Result: ",average_result_2)


# In[172]:


file_name = 'a280.tsp'             # Num of cities:280, Best ratig: 2579
city_count = 280                      # Number of city.
seed_counter = 1 
node_list = read_tsp(file_name,city_count)

# SA CASE 1:

# SA Parameters
Tmax = 10000                          # Initial Temperature.
Tmin = 0.01                           # For the stopping condition. 
moves_per_temperature = 10            # For the equilibrium state.
cooling_rate = 0.95                   # For the cooling schedule.

best_res_1 = 1000000
total_best_1 = 0
total_run_time_1 = 0
random.seed(seed_counter)

for i in range(100):
    best_result_1,total_num_of_generations_1,running_time_1 = generate_SA(node_list,Tmax,Tmin,moves_per_temperature,cooling_rate)
    if best_result_1 < best_res_1: best_res_1 = best_result_1
    total_best_1 = total_best_1 + best_result_1
    total_run_time_1 = total_run_time_1 + running_time_1
average_result_1 = total_best_1/100

# SA CASE 2:

# SA Parameters
Tmax = 10000                         # Initial Temperature.
Tmin = 0.01                          # For the stopping condition. 
moves_per_temperature = 2            # For the equilibrium state.
cooling_rate = 0.995                 # For the cooling schedule.

best_res_2 = 1000000
total_best_2 = 0
total_run_time_2 = 0
random.seed(seed_counter)

for i in range(100):
    best_result_2,total_num_of_generations_2,running_time_2 = generate_SA(node_list,Tmax,Tmin,moves_per_temperature,cooling_rate)
    if best_result_2 < best_res_2: best_res_2 = best_result_2
    total_best_2 = total_best_2 + best_result_2
    total_run_time_2 = total_run_time_2 + running_time_2
average_result_2 = total_best_2/100

print("Case 1, Total Run Time: ",total_run_time_1,", Best Result: ",best_res_1,", Average Result: ",average_result_1)
print("Case 2, Total Run Time: ",total_run_time_2,", Best Result: ",best_res_2,", Average Result: ",average_result_2)


# ## Experiment 2

# In[13]:


file_name = 'kroA100.tsp'             # Num of cities:100, Best ratig: 21282
city_count = 100                      # Number of city.
seed_counter = 1 

# GA Case:

# GA Parameters:
mutation_probability = 0.1            # The rate of mutation applied to a route.
nearest_neighbor_routes_rate = 0    # The rate of routes that created with the nearest neighbors within the population.
population_size = 50                  # Number of individuals in the population.
mating_pool_individuals_count = 5     # Number of individuals in a single mating pool
crossover_operator = "OX"          # "OX" for Ordered Crossover Operator, "SCX" Sequential Constructive Crossover.
mutation_operator = "IVM"           # "ISM":Insertion Mutation, "IVM":Inversion Mutation, "SM":Swap Mutation, 
                                      # "RM":Random mutation
generation_count = 2970            # Number of iterations(generations)
node_list = read_tsp(file_name,city_count)
random.seed(seed_counter)

best_solution_GA = 1000000
total_solution_GA = 0
t1 = datetime.datetime.now()
for i in range(100): 
    population,population_distances = initiatePopulation(nearest_neighbor_routes_rate,population_size,node_list)    
    df,df_best_rank_for_all_iterations = generate_GA(population,population_distances,crossover_operator,mutation_operator,generation_count)
    best_solution = df_best_rank_for_all_iterations["best_solution"].min()
    if best_solution < best_solution_GA: best_solution_GA = best_solution
    total_solution_GA = total_solution_GA + best_solution
average_solution_GA = total_solution_GA / 100
t2 = datetime.datetime.now()
running_time_GA = (t2-t1).seconds

# SA CASE:

# SA Parameters
Tmax = 10000                         # Initial Temperature.
Tmin = 0.01                          # For the stopping condition. 
moves_per_temperature = 2            # For the equilibrium state.
cooling_rate = 0.995                 # For the cooling schedule.

best_res_2 = 1000000
total_best_2 = 0
total_run_time_2 = 0
random.seed(seed_counter)

for i in range(100):
    best_result_2,total_num_of_generations_2,running_time_2 = generate_SA(node_list,Tmax,Tmin,moves_per_temperature,cooling_rate)
    if best_result_2 < best_res_2: best_res_2 = best_result_2
    total_best_2 = total_best_2 + best_result_2
    total_run_time_2 = total_run_time_2 + running_time_2
average_result_2 = total_best_2/100

print("Case GA, Total Run Time: ",running_time_GA,", Best Result: ",best_solution_GA,", Average Result: ",average_solution_GA)
print("Case SA, Total Run Time: ",total_run_time_2,", Best Result: ",best_res_2,", Average Result: ",average_result_2)


# In[15]:


file_name = 'a280.tsp'             # Num of cities:100, Best ratig: 21282
city_count = 280                      # Number of city.
seed_counter = 1 

# GA Case:

# GA Parameters:
mutation_probability = 0.1            # The rate of mutation applied to a route.
nearest_neighbor_routes_rate = 0    # The rate of routes that created with the nearest neighbors within the population.
population_size = 50                  # Number of individuals in the population.
mating_pool_individuals_count = 5     # Number of individuals in a single mating pool
crossover_operator = "OX"          # "OX" for Ordered Crossover Operator, "SCX" Sequential Constructive Crossover.
mutation_operator = "IVM"           # "ISM":Insertion Mutation, "IVM":Inversion Mutation, "SM":Swap Mutation, 
                                      # "RM":Random mutation
generation_count = 2274            # Number of iterations(generations)
node_list = read_tsp(file_name,city_count)
random.seed(seed_counter)

best_solution_GA = 1000000
total_solution_GA = 0
t1 = datetime.datetime.now()
for i in range(100): 
    population,population_distances = initiatePopulation(nearest_neighbor_routes_rate,population_size,node_list)    
    df,df_best_rank_for_all_iterations = generate_GA(population,population_distances,crossover_operator,mutation_operator,generation_count)
    best_solution = df_best_rank_for_all_iterations["best_solution"].min()
    if best_solution < best_solution_GA: best_solution_GA = best_solution
    total_solution_GA = total_solution_GA + best_solution
average_solution_GA = total_solution_GA / 100
t2 = datetime.datetime.now()
running_time_GA = (t2-t1).seconds

# SA CASE:

# SA Parameters
Tmax = 10000                         # Initial Temperature.
Tmin = 0.01                          # For the stopping condition. 
moves_per_temperature = 2            # For the equilibrium state.
cooling_rate = 0.995                 # For the cooling schedule.

best_res_2 = 1000000
total_best_2 = 0
total_run_time_2 = 0
random.seed(seed_counter)

for i in range(100):
    best_result_2,total_num_of_generations_2,running_time_2 = generate_SA(node_list,Tmax,Tmin,moves_per_temperature,cooling_rate)
    if best_result_2 < best_res_2: best_res_2 = best_result_2
    total_best_2 = total_best_2 + best_result_2
    total_run_time_2 = total_run_time_2 + running_time_2
average_result_2 = total_best_2/100

print("Case GA, Total Run Time: ",running_time_GA,", Best Result: ",best_solution_GA,", Average Result: ",average_solution_GA)
print("Case SA, Total Run Time: ",total_run_time_2,", Best Result: ",best_res_2,", Average Result: ",average_result_2)

