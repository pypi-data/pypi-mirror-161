from simplelhs import LatinHypercubeSampling

lhs = LatinHypercubeSampling(3)
hc = lhs.random(5)

print(hc)