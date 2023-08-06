# Introduction

This library is meant to supplement the presentation [_Phonotactic well-formedness is recombinant_](https://bit.ly/sle-recombinant), given at the [55th Annual Meeting of the SLE](https://societaslinguistica.eu/sle2022/).

It learns typologically diverse phonotactics from positive examples alone.

# Installation

```
pip install recombinant
```

# Example

Here, we generalize the set /miememei, oumumo, momomu, iememi/ and then elicit ratings for /meem, memo, mumo/.

```python
from recombinant import Learner

L = Learner([
    'miememei',
    'oumumo',
    'momomu',
    'iememi',
])

L.optimize()

print(L.rate('meem')) # => 0.4873949579831933 
print(L.rate('memo')) # => 0
print(L.rate('mumo')) # => 0.7899159663865546
print(L.basis)        # => ['momu', 'momo', 'oumo', 'memi', 'mi', 'emi', ...]
```

The actual learning takes place during the call to `L.optimize()`. Sometimes, running this optimization routine more than once gives better results.
