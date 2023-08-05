import pytest

import numpy as np
import pandas as pd
import logging

import scanpy as sc
import scallop as sl

from scallop.logg import logger
from scallop.tools._intersection_functions import overlap_score
logger.setLevel(logging.INFO)


@pytest.fixture()  # saves the function to be called in another function, and thus gets all the variables as attrs
def import_scal():
    adata = sl.datasets.joost2016()
    sc.pp.recipe_seurat(adata)
    scal = sl.Scallop(adata)
    return adata, scal

@pytest.fixture()
def create_bts(import_scal):
    adata, scal = import_scal

    sl.tl.getScore(scal=scal, res=1, frac_cells=0.9, n_trials=10)
    sl.tl.getScore(scal=scal, res=2, frac_cells=0.8, n_trials=10)

    return scal


@pytest.mark.parallel
def test_bootstrap_args(import_scal):
    adata, scal = import_scal
    frac_cells, n_trials = 0.9, 10
    res = 1

    bt_1 = sl.Bootstrap(scal=scal, bt_id=0, res=res, frac_cells=frac_cells, n_trials=n_trials, clustering='leiden',
                        seed=0)

    # User-defined attrs
    assert bt_1.scal == scal
    assert bt_1.res == res
    assert bt_1.frac_cells == frac_cells
    assert bt_1.n_trials == n_trials
    assert scal.n_cells * frac_cells - bt_1.sample_size < 1
    assert bt_1.id == 0
    assert bt_1.clustering == 'leiden'

    # Code-defined attrs
    assert bt_1.empty_value == -1
    assert type(bt_1.bt_matrix) == np.ndarray
    assert np.shape(bt_1.bt_matrix) == (scal.n_cells, n_trials)
    for el in [bt_1.freq_score, bt_1.mapped_matrix, bt_1.most_freq, bt_1.inter_score, bt_1.ident, bt_1.conductance]:
        assert el is None

    print('\n_srtRepr\n', bt_1._strRepr())

    print('\nSTR / REPR OUTPUT: \n', bt_1)


@pytest.mark.parallel
def test_Btmatrix(create_bts):
    scal = create_bts
    bt = sl.Bootstrap(bt_id=-1, scal=scal, res=1, frac_cells=0.7, n_trials=10, clustering='leiden', seed=0)

    assert bt.bt_matrix.shape == (scal.n_cells, bt.n_trials)
    bt._getBtmatrix(n_procs=1, seed_in_bt=True)
    assert np.all(np.isfinite(bt.bt_matrix)) # It MUST be int or float

    ravel_mat = bt.bt_matrix.ravel() # test percentage of empty values

    assert pytest.approx(len(ravel_mat[ravel_mat != bt.empty_value])/len(ravel_mat),
                         10/len(bt.bt_matrix)) == bt.frac_cells


@pytest.mark.parallel
def test_cluster_mapping_mat(create_bts):
    scal = create_bts
    bt = sl.Bootstrap(bt_id=-1, scal=scal, res=1, frac_cells=0.7, n_trials=3, clustering='leiden', seed=0)

    bt._getBtmatrix(n_procs=1, seed_in_bt=True)
    cluster_map, bt_ids = bt._cluster_mapping_mat(bt_col=1, method='overlap')

    assert cluster_map.shape[0] >= len(set(list(bt.ident)))
    assert np.max(cluster_map) <= 1 and np.min(cluster_map) >= 0


@pytest.mark.parallel
def test_rename_ident(import_scal):
    adata, scal = import_scal

    bt = sl.Bootstrap(bt_id=-1, scal=scal, res=1, frac_cells=0.7, n_trials=5, clustering='leiden', seed=0)
    bt._getBtmatrix(n_procs=1, seed_in_bt=True)
    bt._renameIdent()

    assert len(np.unique(bt.mapped_matrix)) >= len(np.unique(bt.ident))


@pytest.mark.parallel
def test_freq_score(import_scal):
    adata, scal = import_scal

    bt = sl.Bootstrap(bt_id=-1, scal=scal, res=1, frac_cells=0.7, n_trials=30, clustering='leiden', seed=0)
    bt._getBtmatrix(n_procs=1, seed_in_bt=True)
    bt._renameIdent()

    fS_return = bt._freqScore(do_return=True)
    fs_notreturn = bt._freqScore(do_return=False)

    assert fS_return is not None
    assert fs_notreturn is None

    assert isinstance(fS_return, (pd.Series, pd.DataFrame))
    assert np.all(fS_return.values.ravel() == bt.freq_score)

    assert np.nanmax(fS_return.values) <= 1.0, np.max(fS_return.values)
    assert np.nanmin(fS_return.values) >= 0.0, np.min(fS_return.values)

@pytest.mark.parallel
def test_assert_clusters(import_scal):
    adata, scal = import_scal

    sc.tl.leiden(adata, resolution=0.8)
    clusters_adata = sorted(list(set(adata.obs['leiden'])))

    bt = sl.Bootstrap(bt_id=-1, scal=scal, res=0.8, frac_cells=1, n_trials=5, clustering='leiden', seed=0)
    bt._getBtmatrix(n_procs=1, seed_in_bt=True)

    assert abs(len(clusters_adata) - len(sorted(list(set(bt.ident))))) <= 2, (len(clusters_adata), len(sorted(list(set(bt.ident)))))

@pytest.mark.parallel
def test_assert_unknown_toy_matrix(import_scal):
    adata, scal = import_scal

    bt = sl.Bootstrap(bt_id=-1, scal=scal, res=0.8, frac_cells=1, n_trials=25, clustering='leiden', seed=0)
    bt._getBtmatrix(n_procs=1, seed_in_bt=True)
    bt._renameIdent()
    bt.mapped_matrix = np.array([[1,5,1,1],[0,5,0,0],[1,1,1,1],[0,4,0,0],[1,4,1,1],[3,4,1,1],
                                 [3,4,2,2],[3,0,2,2],[1,0,1,1],[1,0,6,7],[2,1,6,7],[1,0,6,7]])
    bt.ident_clusters = np.array([0,1,2])

    bt._remap_unks(threshold=0.5)
    bt_matrix_after = np.array([[1,4,1,1],[0,4,0,0],[1,1,1,1],[0,3,0,0],[1,3,1,1],[3,3,1,1],
                                [3,3,2,2],[3,0,2,2],[1,0,1,1],[1,0,5,5],[2,1,5,5],[1,0,5,5]])

    assert np.all(bt.mapped_matrix == bt_matrix_after)


@pytest.mark.parallel
def test_assert_unknown_remapping(import_scal):
    adata, scal = import_scal

    sl.tl.getScore(scal, n_trials=30)

    arange_init = len(scal.list_bootstraps[0].ident_clusters)
    arange_end = len(np.unique(scal.list_bootstraps[0].mapped_matrix))
    clust_unk = np.arange(arange_init, arange_end)

    for clus in clust_unk:
        res = np.argwhere(scal.list_bootstraps[0].mapped_matrix == clus)
        list_cols = list(set(res[:, 1]))
        import itertools
        if len(list_cols) > 1:
            list_pairs = list(itertools.combinations(list_cols, 2))
            for tup in list_pairs:
                idx_a = set(list(res[res[:, 1] == tup[0]][:, 0]))
                idx_b = set(list(res[res[:, 1] == tup[1]][:, 0]))

                intersection_f = overlap_score(idx_a, idx_b)

                if intersection_f < 0.7:
                    logger.warning('OVERLAP {} {}'.format(tup, intersection_f))