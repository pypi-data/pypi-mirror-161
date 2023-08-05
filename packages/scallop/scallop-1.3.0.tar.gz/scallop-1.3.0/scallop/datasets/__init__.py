from .joost2016 import joost2016
from .heart10k import heart10k
from .neurons10k import neurons10k

from ..logg import logger

import os

def delete_datasets(name = None):
    """
    Deletes all downloaded datasets.

    Parameters
    ----------
    name: ``str``
        Substring or string of dataset to remove ('joost2016').
    """
    dir_path = os.path.dirname(os.path.realpath(__file__)) + '/data'
    del_formats = ['h5ad', 'txt', 'mtx', 'csv', 'zip', 'tar', 'gz', 'rar', 'h5']

    for file in os.listdir(dir_path):
        for del_fmt in del_formats:
            if file.endswith(del_fmt):
                if name is None:
                    logger.info('Deleting {file}'.format(file=file))
                    os.remove(dir_path + '/' + file)
                else:
                    if file.__contains__(name):
                        logger.info('Deleting {file}'.format(file=file))
                        os.remove(dir_path + '/' + file)