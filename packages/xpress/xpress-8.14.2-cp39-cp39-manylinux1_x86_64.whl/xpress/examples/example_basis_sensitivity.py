# Example using the Xpress Python interface
#
# Basis handling and sensitivity methods
#
# We solve a simple 2x2 LP problem to optimality,
# which serves as a showcase for basis handling methods and
# sensitivity analysis.
#
# (C) Fair Isaac Corp., 1983-2022


import xpress as xp

# create two variables
x1 = xp.var(name="x_1")
x2 = xp.var(name="x_2", vartype = xp.continuous, lb = 0, ub = xp.infinity)

# create two constraints
cons1 = 5* x1 + x2 >= 7
cons2 = x1 + 4 * x2 >= 9

# name the problem and add variables, objective function, constraints
p = xp.problem("firstexample")
p.addVariable(x1,x2)
p.setObjective(x1 + x2)
p.addConstraint(cons1, cons2)

# save the problem to a file
p.write("firstexample", "lp")

# load a basis by specifying row and column basis status
# below, the optimal basis status will be printed
p.loadbasis([2,2], [1,1])

# solve the problem and print the solution
p.solve()
print("The solution is x_1 = {}, x_2 = {}".format(p.getSolution(x1), p.getSolution(x2)))

# write the solution to a file
p.writeslxsol("firstexample.slx")


# print the row and column basis status
rowstat = []
colstat = []
p.getbasis(rowstat, colstat)
print("Rows basis status:", rowstat)
print("Column basis status:", colstat)

# write basis to a file
p.writebasis("basis")

print("sensitivity Analysis of the objective:")
l = []; u = []
p.objsa([x1,x2], l,u)
for i,x in enumerate([x1, x2]):
    print("The objective coefficient of {} can be varied between [{}, {}]".format(x, l[i], u[i]))
print()

print("Sensitivity Analysis of the lower and upper bounds:")
lblower = []; lbupper = []; ublower = []; ubupper = []
p.bndsa([x1,x2], lblower,lbupper,ublower,ubupper)
for i,x in enumerate([x1, x2]):
    print("The lower bounds of {} can be varied between [{}, {}]".format(x, lblower[i], lbupper[i]))
    print("The upper bounds of {} can be varied between [{}, {}]".format(x, lblower[i], lbupper[i]))
print()

print("Sensitivity Analysis of right-hand sides:")
rhslower = []; rhsupper = []
p.rhssa([cons1, cons2], rhslower, rhsupper)
for i,c in enumerate([cons1, cons2]):
    print("The right-hand side of constraint {} can be varied between [{}, {}]".format(c, rhslower[i], rhsupper[i]))
print()


