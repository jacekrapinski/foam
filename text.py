from itertools import product
parameter_combinations=[list(p) for p in product([5,10,20], [-10,0,10], [5,7.5,10])]

p1={5:1,10:2,20:3}
p2={-10:1,0:2,10:3}
p3={5:1,7.5:2,10:3}

for par in parameter_combinations:
    print(p1[par[0]]+p2[par[1]]*10+p3[par[2]]*100)
print(parameter_combinations)