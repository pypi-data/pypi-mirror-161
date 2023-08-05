import pytest

import numpy as np
import pandas as pd
import logging
import time

import scanpy as sc
import scallop as sl


from scallop.logg import logger
logger.setLevel(logging.INFO)


@pytest.fixture()
def import_scal_joost2016():
    adata = sl.datasets.joost2016()
    sc.pp.recipe_seurat(adata)

    scal = sl.Scallop(adata)

    return adata, scal



@pytest.mark.parallel_individual
def test_bootstrap_args_joost2016(import_scal_joost2016):
    adata, scal_not_parallel = import_scal_joost2016
    scal_parallel = sl.Scallop(adata)

    t_parall = time.time()
    bt_parallel = sl.tl.getScore(scal_parallel, res=1, n_trials=50, n_procs=8, do_return=True)
    t_parall = time.time() - t_parall

    t_not_parall = time.time()
    bt_not_parallel = sl.tl.getScore(scal_not_parallel, res=1, n_trials=50, n_procs=1, do_return=True)
    t_not_parall = time.time() - t_not_parall

    logger.debug("The parallel process time with {} processors is {}, "
                 "and the non parallel time is {}".format(10, t_parall, t_not_parall))

    assert (np.max(bt_not_parallel.values) <= 1) & (np.min(bt_not_parallel.values) >= 0)
    assert (np.max(bt_parallel.values) <= 1) & (np.min(bt_parallel.values) >= 0)
    assert abs(np.mean(bt_not_parallel.values) - np.mean(bt_parallel.values)) < 0.05
    assert abs(np.std(bt_not_parallel.values) - np.std(bt_parallel.values)) < 0.05


@pytest.mark.parallel_individual
def test_bootstrap_args_joost2016(import_scal_joost2016):
    """
    We will assert that parallel calculation of bootstrap matrix works correctly, and that if a seed is
    given, for frac_cells = 1, then the matrix has identical columns.
    """

    adata, scal_not_parallel = import_scal_joost2016
    scal_parallel = sl.Scallop(adata)

    sl.tl.getScore(scal_parallel, res=1, n_trials=5, n_procs=8, seed=10, frac_cells=1)
    sl.tl.getScore(scal_not_parallel, res=1, n_trials=5, n_procs=1, seed=10, frac_cells=1)

    logger.debug(scal_parallel.list_bootstraps[0].ident)
    logger.debug(scal_parallel.list_bootstraps[0].bt_matrix)
    logger.debug(scal_not_parallel.list_bootstraps[0].bt_matrix)

    assert np.all(scal_parallel.list_bootstraps[-1].bt_matrix == scal_not_parallel.list_bootstraps[-1].bt_matrix)
    assert np.all(scal_parallel.list_bootstraps[-1].bt_matrix[:, 0] == scal_parallel.list_bootstraps[-1].bt_matrix[:, 1])
    assert np.all(scal_parallel.list_bootstraps[-1].bt_matrix[:, 0] == scal_parallel.list_bootstraps[-1].bt_matrix[:, 2])


@pytest.mark.parallel_individual
def test_bootstrap_args_paul15():
    adata = sc.datasets.paul15()
    scal_not_parallel = sl.Scallop(adata)
    scal_parallel = sl.Scallop(adata)

    t_parall = time.time()
    bt_parallel = sl.tl.getScore(scal_parallel, res=1, n_trials=30, n_procs=8, do_return=True)
    t_parall = time.time() - t_parall

    t_not_parall = time.time()
    bt_not_parallel = sl.tl.getScore(scal_not_parallel, res=1, n_trials=30, n_procs=1, do_return=True)
    t_not_parall = time.time() - t_not_parall

    logger.debug("The parallel process time with {} processors is {}, "
                 "and the non parallel time is {}".format(10, t_parall, t_not_parall))

    assert (np.max(bt_not_parallel.values) <= 1) & (np.min(bt_not_parallel.values) >= 0)
    assert (np.max(bt_parallel.values) <= 1) & (np.min(bt_parallel.values) >= 0)
    assert abs(np.mean(bt_not_parallel.values) - np.mean(bt_parallel.values)) < 0.05
    assert abs(np.std(bt_not_parallel.values) - np.std(bt_parallel.values)) < 0.07


@pytest.mark.parallel_individual
def test_bootstrap_args_blobs():
    adata = sc.datasets.blobs(1000, 10, 1, 5000)
    scal_not_parallel = sl.Scallop(adata)
    scal_parallel = sl.Scallop(adata)

    t_parall = time.time()
    bt_parallel = sl.tl.getScore(scal_parallel, res=1, n_trials=30, n_procs=8, do_return=True)
    t_parall = time.time() - t_parall

    t_not_parall = time.time()
    bt_not_parallel = sl.tl.getScore(scal_not_parallel, res=1, n_trials=30, n_procs=1, do_return=True)
    t_not_parall = time.time() - t_not_parall

    logger.debug("The parallel process time with {} processors is {}, "
                 "and the non parallel time is {}".format(10, t_parall, t_not_parall))

    assert (np.max(bt_not_parallel.values) <= 1) & (np.min(bt_not_parallel.values) >= 0)
    assert (np.max(bt_parallel.values) <= 1) & (np.min(bt_parallel.values) >= 0)
    assert abs(np.mean(bt_not_parallel.values) - np.mean(bt_parallel.values)) < 0.05
    assert abs(np.std(bt_not_parallel.values) - np.std(bt_parallel.values)) < 0.07
