import pytest

import logging
import numpy as np
import time

import scanpy as sc
import scallop as sl

from scallop.logg import logger
logger.setLevel(logging.INFO)


@pytest.fixture() #saves the function to be called in another function, and thus gets all the variables as attrs
def import_scal():
    adata = sl.datasets.joost2016()
    sc.pp.recipe_seurat(adata)
    scal = sl.Scallop(adata)

    return adata, scal


@pytest.mark.parallel
def test_bootstrap_args(import_scal):
    adata, scal = import_scal
    frac_cells, n_trials = 0.9, 15
    res = 2

    t = time.time()
    freq_score_ret = sl.tl.getScore(scal=scal, res=res, frac_cells=frac_cells, n_trials=n_trials,
                                    do_return=True, seed=0)
    time_first = time.time() - t

    # We should get the return directly
    t = time.time()
    freq_score_ret_2 = sl.tl.getScore(scal=scal, res=res, frac_cells=frac_cells, n_trials=n_trials,
                                      do_return=True, seed=0)
    time_second = time.time() - t

    assert 1000 * time_second < time_first, (time_first, time_second)
    assert np.all(freq_score_ret.values.ravel() == freq_score_ret_2.values.ravel())

    logger.debug("The process time with initial processing is {}, "
                 "and the time for file retrieval is  {}".format(freq_score_ret, freq_score_ret_2))


@pytest.mark.parallel
def test_getscore_force(import_scal):
    adata, scal = import_scal
    frac_cells, n_trials = 0.9, 5
    res = 2

    sl.tl.getScore(scal=scal, res=res, frac_cells=frac_cells, n_trials=n_trials, seed=0)
    sl.tl.getScore(scal=scal, res=res, frac_cells=frac_cells, n_trials=n_trials, seed=0)
    assert len(scal.list_bootstraps) == 1

    sl.tl.getScore(scal=scal, res=res, frac_cells=frac_cells, n_trials=n_trials, force=True, seed=0)
    assert len(scal.list_bootstraps) == 2

    sl.tl.getScore(scal=scal, res=res, frac_cells=frac_cells, n_trials=n_trials, seed=0)
    assert len(scal.list_bootstraps) == 2

    sl.tl.getScore(scal=scal, res=res, frac_cells=frac_cells, n_trials=n_trials, force=True, seed=0)
    assert len(scal.list_bootstraps) == 3

    logger.debug(scal.getAllBootstraps())

@pytest.mark.parallel
def test_cluster_types(import_scal):
    adata, scal = import_scal
    frac_cells, n_trials = 0.9, 15
    res = 2

    t = time.time()
    freq_score_leiden = sl.tl.getScore(scal=scal, res=res, frac_cells=frac_cells, n_trials=n_trials,
                                       clustering='leiden', do_return=True)
    time_first = time.time() - t

    # We should get the return directly
    t = time.time()
    freq_score_louvain = sl.tl.getScore(scal=scal, res=res, frac_cells=frac_cells, n_trials=n_trials,
                                        clustering='louvain', do_return=True)
    time_second = time.time() - t

    assert 0.3 < time_second / time_first < 2, (time_first, time_second)
    assert (np.max(freq_score_leiden.values) <= 1) & (np.min(freq_score_leiden.values) >= 0)
    assert (np.max(freq_score_louvain.values) <= 1) & (np.min(freq_score_louvain.values) >= 0)
    assert abs(np.mean(freq_score_leiden.values) - np.mean(freq_score_louvain.values)) < 0.2
    assert abs(np.std(freq_score_leiden.values) - np.std(freq_score_louvain.values)) < 0.15

    logger.debug("The process time with processing with leiden is {}, "
                 "and the time with processing with louvain is  {}".format(freq_score_leiden, freq_score_louvain))