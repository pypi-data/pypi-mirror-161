import logging

from ..classes.scallop import Scallop
from ..classes.bootstrap import Bootstrap
from ..logg import logger

import pandas as pd
import matplotlib.axes as ax
import ray


def getScore(scal: Scallop,
             res: [float, int] = 0.3,
             frac_cells: float = 0.95,
             n_trials: int = 25,
             score_type: str = "freq",
             clustering: str = "leiden",
             do_return: bool = False,
             n_procs: int = 1,
             force: bool = False,
             seed: int = None,
             seed_in_bt: bool = True):
    """
    Obtains the score for each cell given resolution, clustering and the rest of parameters.

    Parameters
    ----------
    scal : :class:`Scallop`
        Scallop object

    res : ``int``,  ``float``
        Leiden resolution parameter.

    frac_cells : ``float``
        Proportion of cells that will be mapped. It can be in range [0-1].

    n_trials : ``int``
        Number of times bootstrapping will be repeated.

    score_type : ``str``
        Score type. Currently, only 'freq' is supported.

    clustering : ``str``
        Clustering performed in the dataset. Currently [``louvain``, ``leiden``] are allowed.

    do_return : ``bool``
        Return score as a ``pandas.Series`` object.

    n_procs : ``int``
        Number of processors for parallel execution.

    force: ``bool``
        If ``True``, forces recalculating score, and appends the new bootstrap object at ``Scallop.list_bootstraps``.

    seed: ``int``
        Seed of leiden identity clustering.

    seed_in_bt: ``bool``
        If ``True``, during calculation of the bootstrap matrix, runs leiden with the same seed as the the identity.
        Else, sets the seed to ``None``.

    Returns
    -------
    score : :class:`pandas.Series`
        Object with score per cell, and the names of cells as index.
    """
    assert isinstance(scal, Scallop), 'The object you have added as argument is of type {}, ' \
                                      'not an Scallop object'.format(type(scal))

    # We will first check if a Bootstrap object with the required parameters already exists.
    # If so, it will not generate a new Bootstrap object. Else, it appends a new Bootstrap
    # object to the Scallop object
    logger.info('Obtaining score with following parameters: \n '
                'Resolution: {res}\n Fraction of cells: {fc}\n Number of trials: {nt}\n Score type: {st}\n'
                'Clustering type: {ct}, seed: {seed}'.format(
                res=res, fc=frac_cells, nt=n_trials, st=score_type, ct=clustering, seed=seed))

    assert res > 0, "Resolution values must be positive"
    assert 0 <= frac_cells <= 1, "The fraction of cells must be a number between 0 and 1"
    assert n_trials > 0, "Number of trials values must be positive"

    exists_bootstrap = False

    if not force:
        for idx in range(len(scal.list_bootstraps)):
            # Check whether a BT object exists with the same parameter values:
            if (scal.list_bootstraps[idx].res == res) and \
                    (scal.list_bootstraps[idx].frac_cells == frac_cells) and \
                    (scal.list_bootstraps[idx].n_trials == n_trials) and \
                    (scal.list_bootstraps[idx].clustering == clustering) and \
                    (scal.list_bootstraps[idx].seed == seed):

                exists_bootstrap = True
                logger.info('A Bootstrap object with these parameter values already exists. '
                            'The score matrix will be returned directly. If you want to create a new object, '
                            'use call getScore() with force=True.')
                bootstrap_obj = scal.list_bootstraps[idx]
                if do_return:
                    if score_type == 'freq':
                        return pd.DataFrame(scal.list_bootstraps[idx].freq_score,
                                        index=scal.annData.obs_names, columns=['freqScore'])
                    elif score_type == 'entropy':
                        return pd.DataFrame(scal.list_bootstraps[idx].entropy_score,
                                        index=scal.annData.obs_names, columns=['entropyScore'])
                    elif score_type == 'KL':
                        return pd.DataFrame(scal.list_bootstraps[idx].KL_score,
                                            index=scal.annData.obs_names, columns=['KLScore'])
                break
    else:
        logger.info('force argument is True. A new object will be created.')

    if not exists_bootstrap:
        idx = len(scal.list_bootstraps)
        # Because if the bootstrap does not exist, its ID will be equal to the length of list_bootstraps, as
        # the new bootstrap will be added to the queue

        # Get seed from adata.uns['leiden']['params']['random_state'] if it exists, otherwise take

        bootstrap_obj = Bootstrap(bt_id=len(scal.list_bootstraps),
                                  scal=scal,
                                  res=res,
                                  frac_cells=frac_cells,
                                  n_trials=n_trials,
                                  clustering=clustering,
                                  seed=seed,
                                )
        scal.list_bootstraps.append(bootstrap_obj)
        logger.info('The Bootstrap object did not exist and will been created.')

        logger.info('Calculating the bootstrap matrix.')
        bootstrap_obj._getBtmatrix(n_procs=n_procs, seed_in_bt=seed_in_bt)

    if score_type in ['freq', 'entropy', 'KL']:
        if bootstrap_obj.mapped_matrix is None:
            logger.info('Renaming identities.')
            bootstrap_obj._renameIdent()
            bootstrap_obj._remap_unks()

        if score_type == 'freq':
            if bootstrap_obj.freq_score is None:
                logger.info('Calculating freqScore.')
                bootstrap_obj._freqScore()
                if do_return:
                    return pd.DataFrame(scal.list_bootstraps[idx].freq_score, index=scal.annData.obs_names,
                                        columns=['freqScore'])
        elif score_type == 'entropy':
            if bootstrap_obj.entropy_score is None:
                logger.info('Calculating freqScore.')
                bootstrap_obj._entropyScore()
                if do_return:
                    return pd.DataFrame(scal.list_bootstraps[idx].entropy_score, index=scal.annData.obs_names,
                                        columns=['entropyScore'])
        elif score_type == 'KL':
            if bootstrap_obj.KL_score is None:
                bootstrap_obj._KLScore()
                if do_return:
                    return pd.DataFrame(scal.list_bootstraps[idx].KL_score, index=scal.annData.obs_names,
                                        columns=['KLScore'])

    elif score_type == 'inter':
        if bootstrap_obj.inter_score is None:
            bootstrap_obj._interScore()
    else:
        raise AttributeError('The score type can be one of the following: "freq", "entropy" or "KL".')




def plotScore(scal: Scallop,
              score_type: str = "freq",
              plt_type: str = 'umap',
              bt_id: int = None,
              ax: ax.Axes = None,
              show: bool = True):
    """
    Plots the score from ``sl.tl.getScore()``

    Parameters
    ----------
    scal : :class:`Scallop`
        Scallop object

    score_type : ``str``
        Score type. Currently, only 'freq' is supported.

    plt_type : ``str``
        Plot type ("umap", "tsne", "phate", "pca").

    bt_id : ``int``
        Bootstrap id from scal.bootstrap_list. Run ``scal.getAllBootstraps()`` to see the
        id associated to certain conditions.

    ax : :class:`matplotlib.axes.Axes`
        Axis object in which store the plot.

    show : ``bool``
        Shows the plot on window.

    Returns
    -------
    ax : :class:`matplotlib.axes.Axes`
        Stores the score axes into ``ax``.
    """

    scal._plotScore(score_type=score_type, plt_type=plt_type, bt_id=bt_id, ax=ax, show=show)
