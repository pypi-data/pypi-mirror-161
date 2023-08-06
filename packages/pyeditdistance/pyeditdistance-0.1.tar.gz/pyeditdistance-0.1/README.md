# pyeditdistance

[![PyPI version](https://badge.fury.io/py/pyeditdistance.svg)](https://badge.fury.io/py/pyeditdistance)

A pure, minimalist, no-dependency Python library of various edit distance metrics.

Implemented methods:
  - Levenshtein (iterative and recursive implementations)
  - Normalized Levenshtein (using Yujian-Bo [1])
  - Damerau-Levenshtein
  - Hamming distance
  - Longest common subsequence (LCS)

Levenshtein and Damerau-Levenshtein distances use the Wagner-Fischer
dynamic programming algorithm [2].

Some basic unit tests can be executed using `pytest`

## Installation

```pip install pyeditdistance```

Optional (user-specific):
```pip install --user pyeditdistance```

## Usage

```python
from pyeditdistance import distance as d

s1 = "I am Joe Bloggs"
s2 = "I am John Gault"

# Levenshtein distance
res = d.levenshtein(s1, s2) # => 8

# Levenshtein distance (recursive)
res = d.levenshtein_recursive(s1, s2) # => 8

# Normalized Levenshtein
res = d.normalized_levenshtein(s1, s2) # => 0.4210 (approx)

# Damerau-Levenshtein
s3 = "abc"
s4 = "cb"
res = d.damerau_levenshtein(s3, s4) # => 2

# Hamming distance
s5 = "abcccdeeffghh zz"
s6 = "bacccdeeffhghz z"
res = d.hamming(s5, s6) # => 6

# Longest common subsequence (LCS)
s7 = "AAGGQQERqer"
s8 = "AaQERqer"
res = d.longest_common_subsequence(s7, s8) # => 7
```

## References
1. L. Yujian and L. Bo, "A normalized Levenshtein distance metric," 
    IEEE Transactions on Pattern Analysis and Machine Intelligence (2007).
    https://ieeexplore.ieee.org/document/4160958
2.  R. Wagner and M. Fisher, "The string to string correction problem," 
    Journal of the ACM, 21:168-178, 1974.
