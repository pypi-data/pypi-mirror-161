import os
import scanpy as sc
import numpy as np

from ..logg import logger

dir_path = os.path.dirname(os.path.realpath(__file__)) + '/data/'
if not os.path.exists(dir_path): os.mkdir(dir_path)


def download_file(dir_download, web):
    if not os.path.exists(dir_download + 'GSE67602_Joost_et_al_expression.txt.gz'):
        logger.info('Downloading file with wget')
        os.system("wget -P {dir_download} {web}".format(dir_download=dir_download, web=web))

    if not os.path.exists(dir_download + 'GSE67602_Joost_et_al_expression.txt'):
        logger.info('Extracting file')
        os.system("gunzip {dir_download}/GSE67602_Joost_et_al_expression.txt".format(dir_download=dir_download))


def preprocess_file(dir_download, filter):
    import numpy as np
    import scipy as sp

    logger.info("Preprocessing dataset using scanpy")

    adata = sc.read_csv("{dir_download}/GSE67602_Joost_et_al_expression.txt".format(dir_download=dir_download),
                        delimiter='\t')
    adata = adata.transpose()

    adata.var_names_make_unique()
    adata.var_names = [name.upper() for name in adata.var_names.tolist()]
    sc.pp.filter_cells(adata, min_genes=200)
    sc.pp.filter_genes(adata, min_cells=10)

    if filter:
        X = adata.copy().X
        mean = np.nanmean(np.where(np.isclose(adata.X, 0), np.nan, adata.X), axis=0)
        std = np.nanstd(np.where(np.isclose(adata.X, 0), np.nan, adata.X), axis=0)
        per_zeros = np.sum((X > 0), axis=0) / X.shape[1]

        # We will filter by mean, variance and percentage of zeros
        adata = adata[:, (mean > np.percentile(mean, 70)) |
                                     (std > np.percentile(std, 70)) |
                                     (per_zeros > np.percentile(per_zeros, 70))]
        adata_filter = sc.AnnData(X=adata.X.astype(int))

        adata_filter.var_names = adata.var_names
        adata_filter.write_h5ad("{dir_download}/joost2016.h5ad".format(dir_download=dir_download))
    else:
        adata.write_h5ad("{dir_download}/joost2016.h5ad".format(dir_download=dir_download))


def joost2016(filter=False):
    """
    Downloads joost2016 dataset and preprocesses it to a scanpy annData object.

    Parameters
    ----------

    Returns
    -------
    adata: :class:`scanpy.annData`
        AnnData object with with shape (1422 x 6410).
    """

    # Check final file
    joosth5ad = dir_path + "joost2016.h5ad"

    try:
        adata = sc.read_h5ad(joosth5ad, filter)

    except OSError:
        logger.info('Joost anndata file not found ({h5ad}). Downloading and processing file.'.format(h5ad=joosth5ad))
        download_file(dir_path,
                      "ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE67nnn/GSE67602/suppl/"
                      "GSE67602%5FJoost%5Fet%5Fal%5Fexpression%2Etxt%2Egz")
        preprocess_file(dir_path, filter)

        adata = sc.read_h5ad(joosth5ad)

    return adata

