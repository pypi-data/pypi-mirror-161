import numpy as np
import pandas as pd
from scipy import stats
# import networkx as nx # this is for conductance
import ray
from tqdm import tqdm

from . import Scallop
from ..tools._clustering import do_clustering, run_leiden
from ..tools._utils_bt import find_mapping
from ..tools._intersection_functions import return_intersection_function
from ..logg import logger
from ..tools._parallel_clustering import obtain_btmatrix_col
from ..tools._get_object_size import get_size

class Bootstrap():
    """
    Scallop object will store all Bootstraps experiments.

    Parameters
    ----------
    bt_id: ``int``
        ID of `Boostrap` object. This id is useful to retrieve the `Boostrap` object from
        `Scallop.list_bootstraps`.

    scal: :class:`scallop.Scallop`
        `scallop.Scallop` object

    res: ``float``
        Leiden resolution parameter.

    frac_cells: ``float``
        Proportion of cells that will be mapped. It can be in range [0-1].

    n_trials: ``int``
        Number of times bootstrapping will be repeated.
    """

    def __init__(self, bt_id: int,
                 scal: Scallop,
                 res: float,
                 frac_cells: float,
                 n_trials: int,
                 clustering: str,
                 seed: int):

        logger.debug('Bootstrap object created with parameters:\nid={}'
                     '\nres={}\nfrac_cells={}\nn_trials={}\nclustering={}'.format(
            bt_id, res, frac_cells, n_trials, clustering))

        self.scal = scal
        self.res = res
        self.frac_cells = frac_cells
        self.n_trials = n_trials
        self.sample_size = int(frac_cells * self.scal.n_cells)
        self.overlap_thresh = 0.1
        self.id = bt_id
        self.clustering = clustering
        self.seed = np.random.randint(1000000) if seed is None else seed
        self.empty_value = -1
        self.bt_matrix = np.full((self.scal.n_cells, self.n_trials), self.empty_value, dtype=int)
        self.mapped_matrix = None
        self.freq_score = None
        self.entropy_score = None
        self.KL_score = None
        self.most_freq = None
        self.inter_score = None
        self.ident = None
        self.ident_clusters = None
        self.conductance = None
        self.bt_seeds = None

    def _strRepr(self):
        def IDformat(bt_id):
            """
            :param bt_id: Bootstrap ID
            :return: foratted Boostrap ID
            """
            id_str = str(bt_id)
            if len(id_str) == 1:
                id_str = ' ' + id_str
            return id_str

        line = '-' * 90 + '\n'
        string = 'Bootstrap ID: {} | res: {} | frac_cells: {} | n_trials: {} | clustering: {} | seed: {}'.format(
            IDformat(self.id), round(float(self.res), 1), self.frac_cells, self.n_trials, self.clustering, self.seed)
        return line + string

    def __repr__(self):
        return self._strRepr()

    def __str__(self):
        return self._strRepr()

    def _getBtmatrix(self, n_procs, seed_in_bt):
        """
        Obtain the bootstrap matrix (self.bt_matrix), that is, a n_cells x n_trials matrix where, in each column, the
        cluster identities with the selected cells are shown. The cells that have not been selected will be filled with
        and exclusion value (self.empty_value) that by default is -1.
        """

        # --------------------------------------------------------------------------------------------------------------
        # Reference clustering (Leiden/Louvain clustering using all cells)
        adj = self.scal.annData.obsp['connectivities']

        # We are going to add a dictionary of keywords, since passing do_clustering or obtain_btmatrix_col with
        # args through ray yields an error (ray does not currently support kwargs). With the dictionary, we will
        # pass all arguments as pseudo-kwargs, and thus we can pass all arguments to the clustering algorithm
        # as "kwargs".
        clustering_options = {'alg_name': self.clustering,
                              'adj': adj,
                              'resolution': self.res,
                              'random_state': self.seed,
                              'use_weights': True}

        self.ident = do_clustering(clustering_options)
        self.ident_clusters = np.unique(self.ident)

        logger.info("Obtaining bootstrap matrix. {} processes are used at once.".format(n_procs))
        # --------------------------------------------------------------------------------------------------------------

        # Here we set the seed for the calculation of bt_matrix. We will set the seed as the value of clustering_options
        if (seed_in_bt is None) or (not seed_in_bt):
            self.bt_seeds = np.random.randint(1, 1000000, self.n_trials)
        else:
            self.bt_seeds = [self.seed] * self.n_trials

        # Bootstrap iterations:
        if n_procs == 1:  # We keep this option because if the matrices are small or the n_trials is low, the
            # computation can be faster.

            for trial in tqdm(range(self.n_trials)):
                rnd_idx = np.random.choice(self.scal.n_cells, size=self.sample_size, replace=False)
                rnd_idx = np.sort(rnd_idx)  # THIS IS KEY: if the indices are in another order, leiden will yield
                # different results even with the same seed!

                # We restrict the cells to the ones in rnd_idx
                adj_trial = adj[rnd_idx, :]
                adj_trial = adj_trial[:, rnd_idx]

                clustering_options['adj'] = adj_trial
                clustering_options['random_state'] = self.bt_seeds[trial]

                self.bt_matrix[rnd_idx, trial] = do_clustering(clustering_options)
        else:
            if ray.is_initialized():  # In case it remained opened from another process.
                ray.shutdown()

            ray.init(num_cpus=n_procs)

            list_clustering_arrs_ids = []

            adj_id = ray.put(adj)  # In this part we store the adjacency matrix in ray memory, so that all processes
            # use the same memory direction.

            '''
            In this part we apply ray. Ray requires the function to be called as function.remote(args), and the
            function calls are stored in a list (list_clustering_arrs_ids), as futures. Those futures are then executed
            with the method ray.get(list)
            '''
            for trial in range(self.n_trials):
                clustering_options['random_state'] = self.bt_seeds[trial]
                list_clustering_arrs_ids.append(obtain_btmatrix_col.remote(adj=adj_id, n_cells=self.scal.n_cells,
                                                                           sample_size=self.sample_size,
                                                                           empty_value=self.empty_value,
                                                                           clustering_options=clustering_options))


            list_clustering_arrs = ray.get(list_clustering_arrs_ids)
            ray.shutdown()

            self.bt_matrix = np.column_stack(list_clustering_arrs)

    def _cluster_mapping_mat(self, bt_col, method='overlap'):
        """
        Given two arrays with the labels of the original clustering, and the bootstrap clustering, returns the matrix
        where each (i,j) element is the similarity score between the cells that were
        assigned to cluster i in the reference clustering (Leiden clustering using all cells) and the cells that were
        assigned to cluster j in one of the bootstrap iterations. There are different similarity scores: 'overlap',
        'jaccard', etc.
        """

        bt_ident = self.bt_matrix[:, bt_col]
        clusters_bt = np.unique(bt_ident[bt_ident != self.empty_value])
        # If the number of clusters the two solutions (ident or bootstrap) are different, the matrix is filled with zeros
        # because munkres requires a square matrix
        n = max(len(self.ident_clusters), len(clusters_bt))
        mapping_matrix = np.zeros((n, n))
        for i in range(len(self.ident_clusters)):
            for j in range(len(clusters_bt)):
                cells_A = set(np.where(self.ident == self.ident_clusters[i])[0])
                cells_B = set(np.where(bt_ident == clusters_bt[j])[0])
                intersection_f = return_intersection_function(method)
                score = intersection_f(cells_A, cells_B)
                mapping_matrix[i][j] = score

        return mapping_matrix, clusters_bt

    def _renameIdent(self, method='overlap'):
        """
        Parameters
        ----------
        method: str
            Method of intersection score between two sets ('bool', 'overlap', 'jaccard', 'max', 'min').
        Returns
        -------
        None
        """
        # Todo: solve issue when freq(most freq) == freq(second most freq)
        # Initialize mapped_matrix with empty values. This matrix will contained the renamed cluster identities
        # (renamed: new cluster names that match those in reference solution)
        self.mapped_matrix = np.full((self.scal.n_cells, self.n_trials), self.empty_value)

        unk_count = len(self.ident_clusters)  # Name of the first unknown cluster (we start from the next integer after
        # known clusters

        for bt_trial in range(self.n_trials):

            # mapping_matrix: element (i, j) corresponds to the similarity score between cluster i from ident and
            # cluster j from bt_trial
            # clusters_bt_trial: list of unique cluster names in bootstrap solution
            mapping_matrix, clusters_bt_trial = self._cluster_mapping_mat(bt_col=bt_trial, method=method)

            # perm: permutation of the columns that maximizes the trace, in the form of a list of tuples
            # (a, b), where:
            #  a:  tuple index = original cluster name in in ident = position to which the column should be moved
            #  b: cluster name in bt trial = original position of the column that will be moved to a
            perm = find_mapping(mapping_matrix)

            # mapped_diag: diagonal of the permuted matrix
            mapped_diag = mapping_matrix[:, [item[1] for item in perm]].diagonal()

            # nonzero: positions of diag with value greater than overla_thresh. Why? Because we want to classify
            # mappings in 'good'/fixed clusters vs 'bad'/unknown clusters. Unknown mappings arise from
            # clusters that are more subdivided in a bootstrapping solution than in the original leiden solution.
            # Therefore, one of the parts 'takes' the cluster name (is renamed to the original cluster name) and the
            # other one is left as an unknown. If it matches an unknown from another trial, then they will both be
            # renamed to the same cluster number.
            nonzero = np.argwhere(mapped_diag > self.overlap_thresh).ravel()

            # nonzero_perm: permutation to be applied to non-zero positions
            nonzero_perm = [perm[i] for i in nonzero]

            # zero_perm: permutation to be applied to zero positions
            zero_perm = [perm[i] for i in np.argwhere(mapped_diag <= self.overlap_thresh).ravel()]

            # cluster_perm: dictionary with original cluster names in bt trial as keys and new names (corresponding name
            # from reference ident) as values
            clusters_perm = {clusters_bt_trial[tup[1]]: self.ident_clusters[tup[0]] for tup in nonzero_perm}

            # Deal with unknowns: clusters that were matched in the mapping matrix forcefully but that did not have a
            # decent overlap score will be 'tagged' by giving them names greater than len(unique(ident_clusters))
            for tup in zero_perm:
                if tup[1] in clusters_bt_trial:
                    clusters_perm[clusters_bt_trial[tup[1]]] = unk_count
                    unk_count += 1

            for c in list(clusters_perm.keys()):
                self.mapped_matrix[np.argwhere(self.bt_matrix[:, bt_trial] == c).ravel(), bt_trial] = clusters_perm[c]

    def _create_dict_unks(self):
        """
        :return: dictionary with keys: c cluster name, value: (col, idx) tuple where:
        col: column index of mapped_matrix where cluster c was found (integer)
        idx: list of row indices where c cluster was found within column col
        """
        dict_unks = {}
        unk_clus = len(self.ident_clusters)

        col = 0
        while unk_clus <= np.max(self.mapped_matrix):
            idx = np.argwhere(self.mapped_matrix[:, col] == unk_clus).ravel()
            if len(idx) > 0:
                dict_unks[unk_clus] = (col, idx)
                unk_clus += 1
            else:
                col += 1

        logger.debug('dict_unks: {}'.format(dict_unks))
        return dict_unks

    def _merge_equivalent_unks(self, dict_unks, threshold):
        """
        :param dict_unks: dictionary with {clus: (col, idx)} where:
        col: column index where clus is found within mapped_matrix
        idx: list of row indices where clus is found within col
        :param threshold: minimum similarity score two unknown clusters must have in order to be considered the same
        :return: dictionary with final cluster name: list of old cluster names that are considered to be the same
        """
        logger.info('Applying mapping of equivalent unknowns with threshold {}.'.format(threshold))
        unk_clus = len(self.ident_clusters)
        list_unk_clusters = np.sort(np.array(list(dict_unks.keys())))
        dict_merged_clusters = {}
        overlap_func = return_intersection_function('overlap')

        while len(list_unk_clusters) > 0:
            logger.debug('The list of clusters is {}'.format(list_unk_clusters))
            logger.debug('The list of columns is {}'.format([dict_unks[clust_i][0] for clust_i in list_unk_clusters]))

            clust_i = list_unk_clusters[0]
            list_overlap_vals = []

            for clust_j in list_unk_clusters:
                overlap_score = overlap_func(set(dict_unks[clust_i][1]), set(dict_unks[clust_j][1]))
                list_overlap_vals.append(overlap_score)
                logger.debug('Overlap threshold between {} (col {}, len {}) and {} (col {}, len {}) is {}.'.format(
                    clust_i, dict_unks[clust_i][0], clust_j, len(set(dict_unks[clust_i][1])),
                    dict_unks[clust_j][0], len(set(dict_unks[clust_j][1])), overlap_score))

            list_overlap_vals = np.array(list_overlap_vals)

            overlap_clus_idx = list_overlap_vals > threshold

            logger.debug('\n clust_i: {}\n list_overlap_vals: {} \n overlap_clus_idx: {}\n'
                         ''.format(clust_i, list_overlap_vals, overlap_clus_idx))

            for overlap_clus in list_unk_clusters[np.argwhere(overlap_clus_idx).ravel()]:
                dict_merged_clusters[overlap_clus] = unk_clus

            list_unk_clusters = list_unk_clusters[~ overlap_clus_idx]  # Select remaining positions
            unk_clus += 1

        logger.debug('dict_merged_clusters: {}'.format(dict_merged_clusters))
        return dict_merged_clusters

    def _remap_unks(self, threshold=0.5):
        """
        :param threshold: defined in method self._merge_equivalent_unks
        :return: updated mapped_matrix with remapped unknown clusters
        """
        dict_unks = self._create_dict_unks()
        dict_merged_clusters = self._merge_equivalent_unks(dict_unks=dict_unks, threshold=threshold)
        for original_clus, remapped_clus in dict_merged_clusters.items():
            col, idx = dict_unks[original_clus][0], dict_unks[original_clus][1]

            self.mapped_matrix[idx, col] = remapped_clus

    def _freqScore(self, do_return=False):
        """
        Obtains the frequency score for the sample, that is, the frequency of the most frequently assigned cluster
        identity per cell is stored in annData.obs['freq'].

        Parameters
        ----------
        do_return: bool
        If True, returns the freqScore pandas series.

        Returns
        -------
        return: pandas.Series
        Series object with freq score for each cell.
        """

        # Since, for each trial, a percentage of cells is empty, there is a probability that
        # in some cells the amount of empty values for all its trials is more than half of the
        # trials, or even all trials are empty. In the first case we create a nanMatrix in which
        # empty values are replaced by NaNs, so that the mode is not affected by empty values.
        # Then, the counts of the most frequent values are divided by the number of nonempty
        # trials for each cell. For the second case, since we have no information about the
        # clustering for that cell (all trials are empty values) we assign it a score of 0.
        # There might be other approaches, but this is not important right now, since we can
        # (and should) increase the number of trials in that case.
        nanmatrix = self.mapped_matrix.copy().astype(float)
        nanmatrix[nanmatrix == self.empty_value] = np.nan

        mode, count = stats.mode(nanmatrix, axis=1, nan_policy='omit')

        del [nanmatrix]

        non_empty_values_count = np.sum((self.mapped_matrix != self.empty_value), axis=1)

        self.most_freq = mode.ravel()
        self.freq_score = count.ravel() / non_empty_values_count
        self.freq_score[self.freq_score == np.inf] = 0

        if do_return:
            return pd.DataFrame(self.freq_score,
                                index=self.scal.annData.obs_names, columns=['freqScore'])

    def _entropyScore(self, do_return=False):
        entropies = []
        for i in range(self.scal.n_cells):
            unique_elements, counts_elements = np.unique(self.mapped_matrix[i, :], return_counts=True)
            entropies.append(stats.entropy(counts_elements))
        self.entropy_score = [(max(entropies) - ent) / max(entropies) for ent in entropies]
        if do_return:
            return pd.DataFrame(self.entropy_score,
                                index=self.scal.annData.obs_names, columns=['entropyScore'])

    def _KLScore(self, do_return=False):
        kl = []
        for i in range(self.scal.n_cells):
            unique_elements, counts_elements = np.unique(self.mapped_matrix[i, :], return_counts=True)
            null_distr = [1 for i in range(len(counts_elements))]
            null_distr[np.argmax(counts_elements)] = np.sum(counts_elements) - len(counts_elements) + 1
            # null_distr = [sum(counts_elements)/len(counts_elements) for i in range(len(counts_elements))]
            kl.append(stats.entropy(counts_elements, null_distr))
        self.KL_score = [1-k for k in kl]
        if do_return:
            return pd.DataFrame(self.KL_score,
                                index=self.scal.annData.obs_names, columns=['KLScore'])
