import numpy as np
from simplelhs import LatinHypercubeSampling, unnormalise

# create object
lhs = LatinHypercubeSampling(3)

# sample random Latin Hypercube design
hc_rand = lhs.random(5)

print("Random Latin Hypercube design:")
print(hc_rand)

# sample Maximin Latin Hypercube design
hc_maximin = lhs.maximin(5, 1000)

print("Maximin Latin Hypercube design:")
print(hc_maximin)

# scale to specific bounds
lower = np.array([0., -1., 5., 1., 100.])
upper = np.array([1., 1., 20., 3., 1000.])
hc_maximin_scaled = unnormalise(hc_maximin, lower, upper)

print("Scaled Maximin Latin Hypercube design:")
print(hc_maximin_scaled)
