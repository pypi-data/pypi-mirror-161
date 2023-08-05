import scanpy as sc
import scanpy.external as sce
import matplotlib.pyplot as plt
import numpy as np

from ..logg import logger

class Scallop():
    """
    Scallop object will store all Bootstraps experiments.

    Parameters
    ----------
    annData: class:`scanpy.annData`
        `scanpy.annData` object

    seed: ``int``
        Random seed for community detection.

    """

    """
    In previous versions, the object could be initialized from a path+filename to
    the gene expression matrix file as well as from a previously initialized annData
    object. For simplicity, we decided Scallop objects to be initialized
    from an annData object.
    """
    def __init__(self, annData: sc.AnnData, seed: int = 10):

        # Relative to the annData
        self.annData = annData
        self.n_cells = self.annData.shape[0]
        self.n_genes = self.annData.shape[1]
        self.cell_names = self.annData.obs.index.values
        self.gene_names = self.annData.var.index.values

        if 'neighbors' not in self.annData.uns:
            logger.warning('Neighbors not in annData. Computing neighbors')
            sc.pp.neighbors(self.annData)

        # Relative to other properties
        self.seed = seed

        # Relative to generated objects
        self.list_bootstraps = []

        # self.memory_use = optional parameter
    def __str__(self):
        return 'Scallop object with {} cells and {} genes'.format(self.n_cells, self.n_genes)

    def _plotScore(self,
                score_type: str = '',
                # we should add score_type once we implement interScore
                  plt_type: str = 'umap',
                  bt_id: int = 0, ax = None,
                  show: bool = True):
        # 'freq' or 'intersection'
        """
        Parameters
        ----------

        plt_type: str
            Plot type ("umap", "tsne", "phate", "pca").

        bt_id: int
            Bootstrap id from scal.bootstrap_list. Run `scal.getAllBootstraps()` to see the
            id associated to certain conditions.

        ax: matplotlib.Figure.Axis
            Axis object in which store the plot.

        show: bool
            Shows the plot on window.

        Returns
        -------
        Plots the results.
        """
        title = ''
        if ax is not None:
            show = False

        if plt_type == 'umap':
            if 'X_umap' not in self.annData.obsm.keys():
                sc.tl.umap(self.annData, random_state=self.seed)
            dr = self.annData.obsm['X_umap']
        elif plt_type == 'tsne':
            if 'X_tsne' not in self.annData.obsm.keys():
                sc.tl.tsne(self.annData, random_state=self.seed)
            dr = self.annData.obsm['X_tsne']
        elif plt_type == 'phate':
            if 'X_phate' not in self.annData.obsm.keys():
                sce.tl.phate(self.annData, random_state=self.seed)
            dr = self.annData.obsm['X_phate']
        elif plt_type == 'pca':
            if 'X_pca' not in self.annData.obsm.keys():
                sc.tl.pca(self.annData)
            dr = self.annData.obsm['X_pca']
        else:
            print("Enter a valid plot type ('umap', 'tsne', 'phate', 'pca'). Plotting umap.")
            dr = self.annData.obsm['umap']
            # Otherwise dr is referenced before assignment

        if bt_id is None:
            logger.warning('Bootstrap ID not provided. Last bootstrap will be plotted.')
            bt_id = len(self.list_bootstraps) - 1  # always plots last bootstrap

        n_plots = 3
        fig, axs = plt.subplots(nrows=1, ncols=n_plots, figsize=(10, 4))
        ident = self.list_bootstraps[bt_id].ident

        for c in np.unique(ident):
            idx = np.argwhere(ident == c).ravel()
            axs[0].scatter(dr[idx, 0], dr[idx, 1], s=2)
        most_freq = self.list_bootstraps[bt_id].most_freq

        for c in np.unique(most_freq):
            idx = np.argwhere(most_freq == c).ravel()
            axs[1].scatter(dr[idx, 0], dr[idx, 1], s=2)
            axs[2].set_title('freqScore')

        axs[2].scatter(dr[:, 0], dr[:, 1], c=self.list_bootstraps[bt_id].freq_score, s=2, cmap='Blues')
        plt.suptitle(title)

        # Todo: add colorbar
        axs[0].set_title('Identities in reference clustering')
        axs[1].set_title('Most frequently assigned cluster')
        axs[2].set_title('Frequency of assignment')
        for i in range(n_plots):
            axs[i].set_xticks([])
            axs[i].set_yticks([])

        plt.tight_layout()
        if show:
            plt.show()

    def getAllBootstraps(self, do_return: bool = False):
        """
        Prints a summary of each bootstrap element from the :class:`scallop.Scallop` object.

        Parameters
        ----------
        do_return : ``bool``
            Returns the printed string.

        Returns
        -------
        bt_str : ``str``
            String summary of :class:`scallop.Boostrap` objects.
        """
        bt_str = ''
        if len(self.list_bootstraps) == 0:
            bt_str += "No bootstraps found."
        else:
            for bt in self.list_bootstraps:
                bt_str += str(bt) + "\n"

        logger.info(bt_str)
        if do_return:
            return bt_str


    def getClusterIdentities(self, i=None, res=None):
        if i is not None:
            return self.list_bootstraps[i].ident
        if res is not None:
            # The first bootstrap that uses that resolution is selected
            return [bt for bt in self.list_bootstraps if bt.res == res][0].ident
        else:
            print('Please provide either the id of the bootstrap (i) or the resolution used in the community \
                  detection method must be provided.')
