from munkres import Munkres
import numpy as np

def find_mapping(mapping_mat):
    """
    Applies Munkres algorithm for scoreMat to obtain the permutation that maximizes the trace.

    Parameters
    ----------
    scoreMat: numpy.ndarray
        Matrix where each (i,j) element is the score ('overlap', 'jaccard', etc.) between the cells in
        original bootstrap with cluster i, and cells in secondary bootstrap with cluster j.

    Returns
    -------
    perm: numpy.1darray
        Array with column permutation of scoreMat that maximizes the trace.
    """
    m = Munkres()
    perm = m.compute(1 - mapping_mat)
    # perm is a list of tuples (new_col, old_col)

    return perm

