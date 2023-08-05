# simplelhs
Simple implementation of Latin Hypercube Sampling.

# Example

The example below shows how to sample a random Latin Hypercube design with five points for three inputs.

```python
from simplelhs import LatinHypercubeSampling

lhs = LatinHypercubeSampling(3)
hc = lhs.random(5)

print(hc)
```

The example below shows how to sample a Maximin Latin Hypercube design with five points for three inputs. Out of 1000 randomly sampled Latin Hypercube designs the design with the maximal minimal distance between points is selected.

```python
from simplelhs import LatinHypercubeSampling

lhs = LatinHypercubeSampling(3)
hc = lhs.maximin(3, 1000)

print(hc)
```
