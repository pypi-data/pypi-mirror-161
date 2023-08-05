from simplelhs import LatinHypercubeSampling

# create object
lhs = LatinHypercubeSampling(3)

# sample random Latin Hypercube design
hc_rand = lhs.random(5)
print(hc_rand)

# sample Maximin Latin Hypercube design
hc_maximin = lhs.maximin(5, 1000)
print(hc_maximin)
