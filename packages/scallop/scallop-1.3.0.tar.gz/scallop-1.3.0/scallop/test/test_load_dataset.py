import pytest

import numpy as np
from scipy.sparse import find

import os
import time
import logging

import scallop as sl


from scallop.logg import logger
logger.setLevel(logging.INFO)

def allclose(A, B, atol=1e-8):  # from https://stackoverflow.com/questions/47770906

    # If you want to check matrix shapes as well
    assert np.array_equal(A.shape, B.shape), (A.shape, B.shape)

    r1, c1, v1 = find(A)
    r2, c2, v2 = find(B)

    assert np.array_equal(r1, r2) & np.array_equal(c1, c2), (r1, c1, r2, c2)
    assert np.allclose(v1, v2, atol=atol)


@pytest.mark.deletetest
def test_remove_datasets():
    sl.datasets.delete_datasets()

    current_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/datasets/data/'

    assert len([i for i in os.listdir(current_dir) if i[0] != '.']) == 0, os.listdir(current_dir)


@pytest.mark.loadtest
def test_import_joost2016():
    joost = sl.datasets.joost2016()
    logger.debug('Dataset size = {} cells x {} genes.'.format(joost.shape[0], joost.shape[1]))
    assert joost.shape[0] == 1422

    # Now we will load it again, but since it is downloaded, it will load the h5ad immediately
    joost2 = sl.datasets.joost2016()
    allclose(joost.X, joost2.X, atol=1e-8)


@pytest.mark.loadtest
def test_import_heart10k():
    adata = sl.datasets.heart10k(filter=False)
    logger.debug('Dataset size = {} cells x {} genes.'.format(adata.shape[0], adata.shape[1]))
    assert adata.shape[0] == 7713

    # Now we will load it again, but since it is downloaded, it will load the h5ad immediately
    adata2 = sl.datasets.heart10k(filter=False)
    allclose(adata.X, adata2.X, atol=1e-8)


@pytest.mark.loadtest
def test_import_neurons10k():
    adata = sl.datasets.neurons10k(filter=False)
    logger.debug('Dataset size = {} cells x {} genes.'.format(adata.shape[0], adata.shape[1]))
    assert adata.shape[0] == 11843

    # Now we will load it again, but since it is downloaded, it will load the h5ad immediately
    adata2 = sl.datasets.neurons10k(filter=False)
    allclose(adata.X, adata2.X, atol=1e-8)
