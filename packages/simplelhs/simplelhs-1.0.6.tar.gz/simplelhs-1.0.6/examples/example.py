import simplelhs

lhs = simplelhs.LatinHypercubeSampling(3)
hc = lhs.maximin(5, 1000)


print(hc)