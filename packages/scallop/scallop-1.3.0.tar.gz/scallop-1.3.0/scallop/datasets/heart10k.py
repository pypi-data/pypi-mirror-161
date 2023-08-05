import os
import scanpy as sc

from ..logg import logger

dir_path = os.path.dirname(os.path.realpath(__file__)) + '/data/'
if not os.path.exists(dir_path): os.mkdir(dir_path)


def download_file(dir_download, web):
    if not os.path.exists(dir_download + '/heart_10k_v3_filtered_feature_bc_matrix.h5'):
        logger.info('Downloading file with wget')
        os.system("wget -P {dir_download} {web}".format(dir_download=dir_download, web=web))


def preprocess_file(dir_download, filter):
    import numpy as np
    import scipy as sp

    input_file = "{dir_download}/heart_10k_v3_filtered_feature_bc_matrix.h5".format(dir_download=dir_download)
    logger.info("Preprocessing dataset using scanpy ({inf})".format(inf=input_file))

    adata = sc.read_10x_h5(input_file)

    adata.var_names_make_unique()
    adata.var_names = [name.upper() for name in adata.var_names.tolist()]
    sc.pp.filter_cells(adata, min_genes=20)
    sc.pp.filter_genes(adata, min_cells=10)

    if filter:
        X = np.asarray(adata.copy().X.astype(float).todense())
        X[X > 100000] = 0  # Does not allow using np.isfinite()
        mean = np.mean(X, axis=0)
        X[X != 0] = 1
        per_zeros = np.sum(X, axis=0) / X.shape[1]

        # We will filter by mean, variance and percentage of zeros
        adata = adata[:, np.argwhere((mean > np.percentile(mean, 35)) |
                                     (per_zeros > np.percentile(per_zeros, 35))).ravel()]

    adata.write_h5ad("{dir_download}/heart10k.h5ad".format(dir_download=dir_download))


def heart10k(filter=True):
    """
    Downloads 10x heart dataset from E18 mouse.

    Parameters
    ----------

    Returns
    -------
    adata: :class:`scanpy.annData`
        AnnData object with with shape (7713 x 24478).
    """

    # Check final file
    heart10kh5ad = dir_path + "/heart10k.h5ad"

    try:
        adata = sc.read_h5ad(heart10kh5ad, filter)

    except OSError:
        logger.info(
            '10x heart 10k anndata file not found ({h5ad}). Downloading and processing file.'.format(h5ad=heart10kh5ad))
        download_file(dir_path,
                      "http://cf.10xgenomics.com/samples/cell-exp/3.0.0/heart_10k_v3/"
                      "heart_10k_v3_filtered_feature_bc_matrix.h5")

        preprocess_file(dir_path, filter)

        logger.info("Reading {} file".format(heart10kh5ad))
        adata = sc.read_h5ad(heart10kh5ad)

    return adata
