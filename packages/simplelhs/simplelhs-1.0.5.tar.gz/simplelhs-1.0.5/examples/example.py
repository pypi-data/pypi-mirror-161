from re import A
from simplelhs import lhs
a = lhs.LatinHypercubeSampling(3)
hc = a.maximin(5, 1000)


print(hc)