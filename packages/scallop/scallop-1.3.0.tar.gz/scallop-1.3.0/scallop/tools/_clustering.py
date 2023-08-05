import leidenalg
import louvain
from scanpy._utils import get_igraph_from_adjacency
import numpy as np
from scallop.logg import logger

def do_clustering(clustering_options):
    alg_name = clustering_options['alg_name']

    supported_algnames = ['leiden', 'louvain']
    assert alg_name in supported_algnames, 'Supported algorithms are {}'.format(supported_algnames)

    if alg_name == 'leiden':
        return run_leiden(clustering_options)
    elif alg_name == 'louvain':
        return run_louvain(clustering_options)


def run_leiden(clustering_options):
    # Remember that use_weights should be True to obtain a more realistic graph from the adjacency matrix.
    adj, resolution, random_state, use_weights = clustering_options['adj'], clustering_options['resolution'], \
                                                 clustering_options['random_state'], clustering_options['use_weights']

    logger.debug("Running leiden with resolution {}, random state {} and use weights {}".format(resolution,
                                                                                                random_state,
                                                                                                use_weights))

    g = get_igraph_from_adjacency(adj, directed=True)

    weights = np.array(g.es['weight']).astype(np.float64) if use_weights else None
    part = leidenalg.find_partition(g, leidenalg.RBConfigurationVertexPartition, resolution_parameter=resolution,
                                    weights=weights, seed=random_state)
    groups = np.array(part.membership)
    return groups


def run_louvain(clustering_options):
    adj, resolution, random_state, use_weights = clustering_options['adj'], clustering_options['resolution'], \
                                                 clustering_options['random_state'], clustering_options['use_weights']

    g = get_igraph_from_adjacency(adj, directed=True)

    weights = np.array(g.es['weight']).astype(np.float64) if use_weights else None
    part = louvain.find_partition(g, louvain.RBConfigurationVertexPartition, resolution_parameter=resolution,
                                  weights=weights) # Todo: look if the update includes seed
    groups = np.array(part.membership)
    return groups

