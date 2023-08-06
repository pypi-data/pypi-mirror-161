# pyeditdistance

<p>
<img alt="PyPI" src="https://img.shields.io/pypi/v/pyeditdistance">
<img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/pyeditdistance">
<img alt="PyPI - License" src="https://img.shields.io/pypi/l/pyeditdistance?label=license">
</p>

A pure, minimalist Python library of various edit distance metrics. MIT-licensed, zero dependencies.

Implemented methods:
  - [Levenshtein](https://en.wikipedia.org/wiki/Levenshtein_distance) (iterative and recursive implementations)
  - Normalized Levenshtein (using [Yujian-Bo](https://ieeexplore.ieee.org/document/4160958) [1])
  - [Damerau-Levenshtein](https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance)
  - [Hamming distance](https://en.wikipedia.org/wiki/Hamming_distance)
  - [Longest common subsequence (LCS)](https://en.wikipedia.org/wiki/Longest_common_subsequence_problem)

Levenshtein and Damerau-Levenshtein distances use the Wagner-Fischer dynamic programming algorithm [2].

Some basic unit tests can be executed using `pytest`

## Installation

```pip install pyeditdistance```

Optional (user-specific):
```pip install --user pyeditdistance```

## Usage

```python
from pyeditdistance import distance as d

s1 = "I am Joe Bloggs"
s2 = "I am John Galt"

# Levenshtein distance
res = d.levenshtein(s1, s2) # => 8

# Normalized Levenshtein
res = d.normalized_levenshtein(s1, s2) # => 0.4324...

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
1.  L. Yujian and L. Bo, "A normalized Levenshtein distance metric," 
    IEEE Transactions on Pattern Analysis and Machine Intelligence (2007).
    https://ieeexplore.ieee.org/document/4160958
2.  R. Wagner and M. Fisher, "The string to string correction problem," 
    Journal of the ACM, 21:168-178, 1974.
