import pytest

from pyeditdistance import distance as d

a1 = "hello"
a2 = ""
a3 = "123"
a4 = "I am Joe Bloggs"
a5 = "Good morning, Vietnam!"
a6 = "abc"
a7 = "abcccdeeffghh zz"
a8 = "AAGGQQERqer"

b1 = "hello"
b2 = ""
b3 = "0"
b4 = "I am John Gault"
b5 = "Good evening, Paris!"
b6 = "cb"
b7 = "bacccdeeffhghz z"
b8 = "AaQERqer"


def test_levenshtein():
    assert d.levenshtein(a1, b1) == 0
    assert d.levenshtein(b1, a1) == 0
    assert d.levenshtein(a2, a2) == 0
    assert d.levenshtein(b2, a2) == 0
    assert d.levenshtein(a3, b3) == 3
    assert d.levenshtein(b3, a3) == 3
    assert d.levenshtein(a4, b4) == 8
    assert d.levenshtein(b4, a4) == 8
    assert d.levenshtein(b4, a1) == 13
    assert d.levenshtein(a7, b7) == 5
    assert d.levenshtein(a8, b8) == 4


def test_levenshtein_recursive():
    assert d.levenshtein_recursive(a1, b1) == 0
    assert d.levenshtein_recursive(b1, a1) == 0
    assert d.levenshtein_recursive(a2, a2) == 0
    assert d.levenshtein_recursive(b2, a2) == 0
    assert d.levenshtein_recursive(a3, b3) == 3
    assert d.levenshtein_recursive(b3, a3) == 3
    assert d.levenshtein_recursive(a4, b4) == 8
    assert d.levenshtein_recursive(b4, a4) == 8
    assert d.levenshtein_recursive(b4, a1) == 13


def test_normalized_levenshtein():
    assert d.normalized_levenshtein(a1, b1) == 0.0
    assert d.normalized_levenshtein(a1, b2) == 1.0
    assert d.normalized_levenshtein(a2, b2) == 0.0
    assert pytest.approx(d.normalized_levenshtein(a3, b3), 1e-3) == 0.8571
    assert pytest.approx(d.normalized_levenshtein(a4, b4), 1e-3) == 0.4210
    assert pytest.approx(d.normalized_levenshtein(a5, b5), 1e-3) == 0.3846


def test_damerau_levenshtein():
    assert d.damerau_levenshtein(a2, b2) == 0
    assert d.damerau_levenshtein(a4, b4) == 8
    assert d.damerau_levenshtein(a6, b6) == 2
    assert d.damerau_levenshtein(a7, b7) == 3


def test_hamming_distance():
    assert d.hamming(a1, b1) == 0
    assert d.hamming(a2, b2) == 0
    assert d.hamming(a4, b4) == 8
    assert d.hamming(a7, b7) == 6


def test_lcs():
    assert d.longest_common_subsequence(a1, b1) == 5
    assert d.longest_common_subsequence(a2, b2) == 0
    assert d.longest_common_subsequence(a3, b3) == 0
    assert d.longest_common_subsequence(a4, b4) == 9
    assert d.longest_common_subsequence(a5, b5) == 13
    assert d.longest_common_subsequence(a6, b6) == 1
    assert d.longest_common_subsequence(a7, b7) == 13
    assert d.longest_common_subsequence(a8, b8) == 7
