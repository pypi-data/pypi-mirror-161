import numpy as np
import ray

from ._clustering import do_clustering

@ray.remote
def obtain_btmatrix_col(adj, n_cells, sample_size, empty_value, clustering_options):
    rnd_idx = np.random.choice(n_cells, size=sample_size, replace=False)
    rnd_idx = np.sort(rnd_idx)  # THIS IS KEY: if the indices are in another order, leiden will yield
                                # different results even with the same seed!

    # We restrict the cells to the ones in rnd_idx
    adj_trial = adj[rnd_idx, :]
    adj_trial = adj_trial[:, rnd_idx]

    clustering_options['adj'] = adj_trial

    arr = np.full(n_cells, empty_value, dtype=int)
    arr[rnd_idx] = do_clustering(clustering_options)
    return arr





