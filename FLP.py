import pandas as pd
import numpy as np
import time


def duplicated(listn):
    new_list = []
    for element in listn:
        if element not in new_list:
            new_list.append(element)
    return new_list


def selectwh(df, m):
    cost = []
    for j in range(1, (df.shape[0])):
        if df.loc[j, 'State'] == 0:
            total = (df.loc[j, m] * df.loc[0, m]) + df.loc[j, 'Fixed Cost']
            cost.append(total)
        if df.loc[j, 'State'] == 1:
            total = df.loc[j, m] * df.loc[0, m]
            cost.append(total)
    empty = [0]
    cempty = pd.DataFrame(data=empty)
    cst = pd.DataFrame(data=cost)
    cst = pd.concat([cempty, cst], ignore_index=True)
    xt = df.loc[1:, m]
    cst = pd.concat([xt, cst], axis=1, ignore_index=True)
    cst = pd.concat([cst, df.loc[0:, 'Capacity']], axis=1)
    cst.rename(columns={0: 'Wh', 1: 'Cost'}, inplace=True)
    min = cst[cst['Cost'] == cst[(cst['Capacity'] != 0) & (cst['Cost'] != 0)]['Cost'].min()]['Wh'].item()
    return min


def calculate(cust, dv):
    cord = []
    op = []
    hedges = []
    yi = []
    tfc = 0
    for i in range(cust):
        while True:
            nummin = selectwh(dv, i)
            edges = dv.set_index(i).index.get_loc(nummin)
            hedges.append(edges)
            dv.loc[edges, 'State'] = 1
            g = np.where(dv.loc[edges, 'Capacity'] >= dv.loc[0, i], True, False)
            c = np.where(dv.loc[edges, 'Capacity'] <= dv.loc[0, i], True, False)
            a = dv.loc[edges, 'Capacity']
            e = dv.loc[0, i]
            minus = a - e
            mine = e - a
            if g:
                dv.loc[edges, 'Capacity'] = minus
                dv.loc[0, i] = 0
                dv.loc[edges, i] = 0
                op.append(nummin * e)
                yi.append(i)
                cord.append(('[' + str(edges) + ',' + str(i) + ']'))
            if c:
                dv.loc[0, i] = mine
                dv.loc[edges, i] = 0
                op.append(nummin * dv.loc[edges, 'Capacity'])
                dv.loc[edges, 'Capacity'] = 0
                yi.append(i)
                cord.append(('[' + str(edges) + ',' + str(i) + ']'))
            if dv.loc[0, i] == 0:
                break
    t = duplicated(hedges)
    for i in t:
        tfc += dv.loc[i, 'Fixed Cost']
    o = sum(op)
    total = o + tfc
    return cord, op, hedges, total, t, yi,


d = []
e = []
b = []
csv = input("Do yo want me to export the initial and  final table to current directory? y/n:")
time_start = time.perf_counter()
with open('OR-Library_Instances/example', "r") as file:
    first_line = file.readline()
    list1 = list(first_line.split())
    list2 = list(map(int, list1))
    facilities = list2[0]
    cust = list2[1]
    lines = file.readlines()
    warehouses = lines[0:facilities]
    customers = lines[facilities:]

# store the facilities capacities and fixed cost
for i in warehouses:
    d.append(i.split())
wh = pd.DataFrame(data=d)
wh.rename(columns={0: 'Capacity', 1: 'Fixed Cost'}, inplace=True)

# store the customers demand
for i in customers:
    e.append(i.split())
for f in e:
    for i in f:
        i = float(i)
        b.append(i)
x = np.array(b[:cust]).reshape(-1, cust)
customdemand = pd.DataFrame(data=x)

# store the customers demand
y = np.array(b[cust:]).reshape(-1, cust)
allocatingcost = pd.DataFrame(data=y)
df = pd.concat([allocatingcost, wh], axis=1, sort=False)
dv = pd.concat([customdemand, df], ignore_index=True, sort=False)

# converts 2 problematic columns into floats
dv['Capacity'] = pd.to_numeric(dv['Capacity'], errors='coerce')
dv['Fixed Cost'] = pd.to_numeric(dv['Fixed Cost'], errors='coerce')

# starting the heuristic
dv['State'] = 0
dv['State'] = pd.to_numeric(dv['State'], errors='coerce')

# stores a copy of the original state of the dataframe
inicial = dv.copy(deep=True)

# print the original dataframe
print('\nthe original dataframe is:\n\n', dv)
if csv.lower() == 'y':
    dv.to_csv('original.csv', index=True)


# the main function
cord, op, hedges, total, t, yi = calculate(cust, dv)
heuristic = total
if csv.lower() == 'y':
    dv.to_csv('final.csv', index=True)
# print the whole result for heuristic
print('\nthe final dataframe is:\n\n', dv)
print('\nthere are ' + str(len(t)) + ' open warehouses from ' + str(facilities) + ' available ' + '\n')
print('\nthe open warehouses are:\n' + str(t) + '\n')
print('edges:\n\n' + str(cord) + '\n')
print('the total cost before local search was: ' + str(heuristic) + '\n\n')
time_elapsed = (time.perf_counter() - time_start)
print(f"Runtime of the program is {time_elapsed}")

# Local search
time_local = time.perf_counter()

# previus variables stored in localsearch new ones
contador = 1
currentdv = dv
currenx = []
curreny = []
#  in order to apply a switch between the excluded warehouses
localw = list(range(1, facilities + 1))
excluded = [i for i in localw if i not in t]
print(yi)
print(hedges)
print(op)
print(inicial)
while contador <= len(excluded):
    for j in range(1, facilities + 1):
        if j not in excluded:
            for i in range(len(hedges)):
                if hedges[i] != j:
                    currenx.append(hedges[i])
                    curreny.append(yi[i])
            currentdv = dv.drop(j)
            for i in range(len(hedges)):
                if hedges[i] == j:
                    currentcost = op[i] / inicial.iloc[hedges[i], yi[i]]
                    currentdv.loc[0, yi[i]] = currentcost
            print('\n', currentdv)
            print('\n', currenx)
            print('\n', curreny)
            currenx = []
            curreny = []
    contador += 1

time_elapsed_local = (time.perf_counter() - time_local)

