import pytest

import os, sys

dirpath = os.path.dirname(os.path.realpath(os.path.dirname(__file__)))
sys.path.append(dirpath+'/tools')
print(sys.path)

from _intersection_functions import *

@pytest.fixture()
def import_vals():
    n = set()
    a = set([1, 2])
    b = set([3, 4])
    c = set([1, 2, 4])

    return n, a, b, c


@pytest.mark.parallel
def test_jaccard(import_vals):
    n, a, b, c = import_vals

    assert jaccard(n, a) == 0
    assert jaccard(a, b) == 0
    assert jaccard(a, c) == 2/3
    assert jaccard(b, c) == 0.25
    assert jaccard(a, c) == return_intersection_function('jaccard')(a, c)


@pytest.mark.parallel
def test_wave_hedges(import_vals):
    n, a, b, c = import_vals

    assert wave_hedges(n, a) == 1
    assert wave_hedges(a, b) == 1
    assert wave_hedges(a, c) == 1/3
    assert wave_hedges(b, c) == 0.75
    assert wave_hedges(a, c) == return_intersection_function('wave_hedges')(a, c)


@pytest.mark.parallel
def test_tanimoto(import_vals):
    n, a, b, c = import_vals

    assert tanimoto(n, a) == 1
    assert tanimoto(a, b) == 1
    assert tanimoto(a, c) == 1 / 3
    assert tanimoto(b, c) == 0.75
    assert tanimoto(a, c) == return_intersection_function('tanimoto')(a, c)


@pytest.mark.parallel
def test_min_coefficient(import_vals):
    n, a, b, c = import_vals

    assert min_coefficient(n, a) == 0
    assert min_coefficient(a, b) == 0
    assert min_coefficient(a, c) == 1
    assert min_coefficient(b, c) == 1 / 2
    assert min_coefficient(a, c) == return_intersection_function('min')(a, c)


@pytest.mark.parallel
def test_max_coefficient(import_vals):
    n, a, b, c = import_vals

    assert max_coefficient(n, a) == 0
    assert max_coefficient(a, b) == 0
    assert max_coefficient(a, c) == 2 / 3
    assert max_coefficient(b, c) == 1 / 3
    assert max_coefficient(a, c) == return_intersection_function('max')(a, c)


@pytest.mark.parallel
def test_overlap_score(import_vals):
    n, a, b, c = import_vals

    assert overlap_score(n, a) == 0
    assert overlap_score(a, b) == 0
    assert overlap_score(a, c) == 5 / 6
    assert overlap_score(b, c) == 5 / 12
    assert overlap_score(a, c) == return_intersection_function('overlap')(a, c)


@pytest.mark.parallel
def test_boolean(import_vals):
    n, a, b, c = import_vals

    assert boolean(n, a, 0.5) == 0
    assert boolean(a, b, 0.5) == 0
    assert boolean(a, c, 0.5) == 1
    assert boolean(b, c, 0.5) == 0
    assert boolean(a, c, 0.5) == return_intersection_function('bool')(a, c, 0.5)