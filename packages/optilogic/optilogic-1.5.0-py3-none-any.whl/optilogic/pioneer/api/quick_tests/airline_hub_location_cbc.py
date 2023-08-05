import sys
from datetime import datetime
from optilogic import pioneer

pioneer.Job.print_add_record_calls = True

print('airline hub location pyomo module')
sys.stderr.write('stderr is now True\n')
pioneer.Job.add_record(key='started', message=datetime.now())

# An airline which specializes in freight transports links cities in France with cities in USA. 
# The average quantities in tonnes transported every day by this company between these cities 
# are given. It is assumed that the transport cost between two cities is proportional to the 
# distance that separates them. The distances in miles are also given. The airline is planning 
# to use two cities as connection platforms (hubs) to reduce the transport costs. Every city is 
# then assigned to a single hub. The problem is to determine the two cities to be chosen as hubs in order 
# to minimize the transport cost.

from pyomo.environ import *

model = AbstractModel("Airline hub location")

#Sets and parameters

#set of cities that a transportation company operates
model.cities = Set()

#number of hubs
model.hubs = Param(within = NonNegativeReals)

#set of arcs
def arcs(model):
    return ((i,j) for i in model.cities for j in model.cities)
model.arcs = Set(dimen = 2, initialize = arcs)

#distances between every two cities
model.distances = Param(model.arcs, within = NonNegativeReals)

#average quantity transported between each two cities
model.quantity = Param(model.arcs, within = NonNegativeReals)

#factor indicating the percentage of the normal cost between hubs
model.factor = Param(within = NonNegativeReals)

def cost(model, i, j, k, l):
    return model.distances[i,k] + model.factor*model.distances[k,l] + model.distances[l,j]
model.cost = Param(model.cities, model.cities, model.cities, model.cities, initialize = cost)

#Variables

#binary variable indicating whether a city is a hub
model.hub_city = Var(model.cities, within = Binary)

#binary variable indicating whether a freight is transported from city i to city j through hubs k and l in this order
model.transp = Var(model.cities, model.cities, model.cities, model.cities, within = Binary)

#Objective

#minimizing the total transport cost
def min_cost(model):
    return sum(sum(sum(sum(model.cost[i,j,k,l]*model.quantity[i,j]*model.transp[i,j,k,l] for i in model.cities)for j in model.cities)for k in model.cities)for l in model.cities)
model.min_cost = Objective(rule = min_cost)

#Constraints

#number of hubs
def numb_hubs(model):
    return sum(model.hub_city[i] for i in model.cities) == model.hubs
model.numb_hubs = Constraint(rule = numb_hubs)

#every pair of cities (i, j) is assigned to a single pair of hubs
def ij_2_kl(model, i, j):
    return sum(sum(model.transp[i,j,k,l] for k in model.cities) for l in model.cities) == 1
model.ij_2_kl = Constraint(model.cities, model.cities, rule = ij_2_kl)

#if a variable transp[i,j,k,l] is at 1, then the variable hub k is 1
def hub_k_implied(model, i, j, k, l):
    return model.transp[i,j,k,l] <= model.hub_city[k]
model.hub_k_implied = Constraint(model.cities, model.cities, model.cities, model.cities, rule = hub_k_implied)

#if a variable transp[i,j,k,l] is at 1, then the variable hub l is 1
def hub_l_implied(model, i, j, k, l):
    return model.transp[i,j,k,l] <= model.hub_city[l]
model.hub_l_implied = Constraint(model.cities, model.cities, model.cities, model.cities, rule = hub_l_implied)


solver = SolverFactory('cbc')
instance = model.create_instance("airline_hub_location.dat")
results = solver.solve(instance)

#Python Script for printing the solution in the terminal
for i in instance.cities:
    if value(instance.hub_city[i]) > 0:
        print(f'City {i} is a hub')
for i in instance.cities:
    for j in instance.cities:
        for k in instance.cities:
            for l in instance.cities:
                if value(instance.transp[i,j,k,l]) > 0:
                    print(f'A freight is transported from city {i} to city {j} through hubs {k} and {l} in this order')
print(f'The minimum total transportation cost is {value(instance.min_cost)}')

#Python Script for writing the solution while checking the termination condition of the solver
if results.solver.termination_condition == TerminationCondition.infeasible:
    print('The model is infeasible: No solution available')
elif results.solver.termination_condition == TerminationCondition.unbounded:
    print('The model has an unbounded solution')
elif results.solver.termination_condition == TerminationCondition.optimal:
    output = open('results.txt', 'w')
    for i in instance.cities:
        if value(instance.hub_city[i]) > 0:
            output.write(f'City {i} is a hub\n\n')
    for i in instance.cities:
        for j in instance.cities:
            for k in instance.cities:
                for l in instance.cities:
                    if value(instance.transp[i,j,k,l]) > 0:
                        output.write(f'A freight is transported from city {i} to city {j} through hubs {k} and {l} in this order\n\n')
    output.write(f'The minimum total transportation cost is {value(instance.min_cost)}')
    output.close()
