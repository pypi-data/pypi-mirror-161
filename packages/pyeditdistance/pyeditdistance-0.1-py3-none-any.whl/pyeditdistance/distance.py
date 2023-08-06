"""
Pure, single-file implementations of various edit distances, including
Hamming, Levenshtein, Levenshtein (normalized), Levenshtein (recursive),
and Damerau-Levenshtein distances.
"""
__author__ = "Carlton Shepherd"


def _wagner_fischer(a: str, b: str, method: list) -> int:
    """
    Implements the Wagner-Fischer dynamic programming algorithm [1,2].

    Counts insertions, deletions, transpositions and substitutions
    depending on the method.

    1. R. Wagner and M. Fisher, "The string to string correction problem," 
    Journal of the ACM, 21:168-178, 1974.
    2. https://en.wikipedia.org/wiki/Wagner%E2%80%93Fischer_algorithm

    Parameters:
        a: First string
        b: Second string
        method: Distance method ("lev", "dl"), i.e. Levenshtein or
        Damerau-Levenshtein respectively.
    Returns:
        Wagner-Fisher cost (integer).
    """
    a_len, b_len = len(a), len(b)

    if a_len == 0:
        return b_len
    elif b_len == 0:
        return a_len

    _a, _b  = " " + a, " " + b
    a_len, b_len = len(_a), len(_b)
    dist_matrix =  [[0] * a_len for _ in range(b_len)]

    for i in range(a_len):
        dist_matrix[0][i] = i

    for j in range(b_len):
        dist_matrix[j][0] = j

    for j in range(1, b_len):
        for i in range(1, a_len):
            if _a[i] == _b[j]:
                dist_matrix[j][i] = dist_matrix[j-1][i-1]
            else:
                dist_matrix[j][i]= min(dist_matrix[j][i-1], 
                                       dist_matrix[j-1][i],
                                       dist_matrix[j-1][i-1]) + 1
            if method == "dl":
                if i and j and _a[i] == _b[j-1] and _a[i-1] == _b[j]:
                    dist_matrix[j][i] = min(
                        dist_matrix[j][i],
                        dist_matrix[j-2][i-2]+1)
    return dist_matrix[-1][-1]
    

def _lcs_dp(a: str, b:str) -> int:
    """
    A somewhat simpler dynamic programming algorithm for LCS.

    Parameters:
        a: First string
        b: Second string
    Returns:
        LCS length (integer)
    """
    if len(a) == 0 or len(b) == 0:
        return 0

    a_len, b_len = len(a)+1, len(b)+1
    dist_matrix =  [[0] * (a_len) for _ in range(b_len)]

    for j in range(b_len):
        for i in range(a_len):
            if i == 0 or j == 0:
                dist_matrix[j][i] = 0
            elif a[i-1] == b[j-1]:
                dist_matrix[j][i] = dist_matrix[j-1][i-1]+1
            else:
                dist_matrix[j][i] = max(dist_matrix[j-1][i],
                                        dist_matrix[j][i-1])
    return dist_matrix[-1][-1]
    

def levenshtein(a: str, b: str) -> int:
    """
    Computes the Levenshtein distance: the number of
    insertions, deletions or substitutions required
    to transform a -> b.

    Uses the Wagner-Fischer dynamic programming algorithm.
    
    Parameters:
        a: First string
        b: Second string
    Returns:
        Levenshtein distance (integer)
    """
    return _wagner_fischer(a, b, "lev")


def levenshtein_recursive(a: str, b: str) -> int:
    """
    Computes the Levenshtein distance using the naive
    recursive implementation.

    See: https://en.wikipedia.org/wiki/Levenshtein_distance

    Parameters:
        a: First string
        b: Second string

    Returns:
        Levenshtein distance (integer)
    """
    if len(a) == 0:
        return len(b)
    elif len(b) == 0:
        return len(a)
    elif a[0] == b[0]:
        return levenshtein_recursive(a[1:], b[1:])
    else:
        return 1 + min(levenshtein_recursive(a[1:], b),
                       levenshtein_recursive(a, b[1:]),
                       levenshtein_recursive(a[1:], b[1:]))


def normalized_levenshtein(a: str, b: str) -> float:
    """
    Implements the normalized Levenshtein metric by Yujian & Bo [1].

    1. L. Yujian and L. Bo, "A normalized Levenshtein distance metric," 
    IEEE Transactions on Pattern Analysis and Machine Intelligence (2007).
    https://ieeexplore.ieee.org/document/4160958

    Parameters:
        a: First string
        b: Second string

    Returns:
        Normalized Levenshtein distance (float)
    """
    a_len, b_len = len(a), len(b)
    d = levenshtein(a, b)
    dem = ((a_len+b_len) + d)
    try:
        return (2 * d) / ((a_len+b_len) + d)
    except ZeroDivisionError:
        return 0.0


def damerau_levenshtein(a: str, b: str) -> int:
    """
    Computes the Damerau-Levenshtein distance: the number of
    insertions, deletions, substitutions, and transpositions needed
    to transform a -> b.

    Uses the Wagner-Fischer algorithm.

    Parameters:
        a: First string
        b: Second string
    Returns:
        Damerau-Levenshtein distance (integer)
    """
    return _wagner_fischer(a, b, "dl")


def hamming(a: str, b: str) -> int:
    """
    Finds the Hamming distance, the number of substitutions
    (only) to transform a -> b.

    Parameters:
        a: First string
        b: Second string

    Returns:
        Hamming distance (integer)
    """
    if len(a) != len(b):
        raise ValueError("Inputs must be of equal length!")
    return sum([1 for i, j in zip(a, b) if i != j ])


def longest_common_subsequence(a: str, b: str) -> int:
    """
    Finds the longest common subsequence (LCS) of two strings.
    
    Parameters:
        a: First string
        b: Second string

    Returns:
        Longest common subsequence (integer)
    """
    return _lcs_dp(a, b)


def distance(a: str, b: str, method: str):
    """
    Wrapper function for calculating the distance of two strings
    using a given method.

    Parameters:
        a: First string
        b: Second string
        c: Distance metric, one of: ['levenshtein',
           'normalized_levenshtein', 'levenshtein_recurisve',
           'damerau-levenshtein', 'hamming']

    Returns:
        Distance of a and b using the given method
    """
    if method == "levenshtein":
        return levenshtein(a, b)
    elif method == "levenshtein_recursive":
        return levenshtein_recursive(a, b)
    elif method == "normalized_levenshtein":
        return normalized_levenshtein(a, b)
    elif method == "damerau_levenshtein":
        return damerau_levenshtein(a, b)
    elif method == "hamming":
        return hamming(a, b)
    elif method == "lcs":
        return longest_common_subsequence(a, b)
    else:
        raise ValueError("Invalid method! Must be one of: " \
                         "['levenshtein', 'normalized_levenshtein', " \
                         "'levenshtein_recursive', 'damerau-levenshtein', " \
                         "'lcs', 'hamming']")
