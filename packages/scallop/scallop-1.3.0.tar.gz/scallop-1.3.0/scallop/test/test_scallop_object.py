import pytest

import numpy as np

import scanpy as sc
import scallop as sl

import logging
from scallop import logg as lg
lg.logger.setLevel(logging.INFO)


@pytest.fixture() #saves the function to be called in another function, and thus gets all the variables as attrs
def import_scal():
    adata = sl.datasets.joost2016()
    sc.pp.recipe_seurat(adata)
    scal = sl.Scallop(adata)

    return adata, scal


@pytest.mark.parallel
def test_basic_load():
    # Basic load assertions of attributes

    adata = sl.datasets.joost2016()
    scal = sl.Scallop(adata)

    assert np.all(adata.X == scal.annData.X), 'scal.annData: {scal} // adata: {adata}'.format(scal=scal.annData, adata=adata)
    assert scal.seed == 10, 'scal.seed: {scal} // seed: {seed}'.format(scal=scal.seed, seed=10)
    assert scal.n_cells == adata.shape[0]

    assert scal.n_cells == adata.shape[0]
    assert scal.n_genes == adata.shape[1]

    assert np.all(scal.cell_names == adata.obs.index.values)
    assert np.all(scal.gene_names == adata.var.index.values)

    assert len(scal.list_bootstraps) == 0

    print(scal)


@pytest.mark.parallel
def test_load_w_neighbors():
    adata = sl.datasets.joost2016()
    sc.pp.neighbors(adata)

    scal = sl.Scallop(adata)
    assert 'neighbors' in scal.annData.uns.keys()


@pytest.mark.parallel
def test_load_wo_neighbors():
    adata = sl.datasets.joost2016()

    assert 'neighbors' not in adata.uns.keys()
    scal = sl.Scallop(adata)  # Should warn about pp.neighbors being created.
    assert 'neighbors' in adata.uns.keys()  # The original adata object should now have the neighbors
    assert 'neighbors' in scal.annData.uns.keys()


@pytest.mark.parallel
def test_get_all_bt(import_scal):
    adata, scal = import_scal

    assert scal.getAllBootstraps(do_return=True) == 'No bootstraps found.'

    sl.tl.getScore(scal, res=1, n_trials=3, seed=0)
    sl.tl.getScore(scal, res=1.5, n_trials=3)
    sl.tl.getScore(scal, res=1, n_trials=3, seed=0)
    sl.tl.getScore(scal, res=1, n_trials=3, seed=1)

    return_all_bt = scal.getAllBootstraps(do_return=True)
    assert len(scal.list_bootstraps) == 3
    assert 'res: 1.0' in return_all_bt and 'res: 1.5' in return_all_bt


@pytest.mark.parallel
def test_plot_score(import_scal):
    adata, scal = import_scal

    sl.tl.getScore(scal=scal, res=1, n_trials=3)
    for type_plot in ['pca', 'tsne', 'umap', 'phate']:
        scal._plotScore(plt_type=type_plot, show=False)

        assert 'X_{name}'.format(name=type_plot) in scal.annData.obsm

    bt_id = None
    scal._plotScore(bt_id=bt_id, show=False)

