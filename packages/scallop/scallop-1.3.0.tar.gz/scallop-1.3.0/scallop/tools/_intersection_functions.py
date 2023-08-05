############################################# UNITARY SCORE FUNCTIONS ##################################################

# Some of those functions may not be optimized with numba because they already work with sets.
# There are many similarity measures, some of the obtained from here
# http://users.uom.gr/~kouiruki/sung.pdf


def jaccard(A, B):
    return len(A & B)/len(A | B)


def wave_hedges(A, B):
    return (len(A - B) + len(B - A))/len(A | B)


def tanimoto(A, B):
    union = len(A | B)
    return (union - len(A & B))/union


def max_coefficient(A, B):
    if (len(A) == 0) | (len(B) == 0):
        return 0
    else:
        return len(A & B) / max(len(A), len(B))


def min_coefficient(A, B):
    if (len(A) == 0) | (len(B) == 0):
        return 0
    else:
        return len(A & B) / min(len(A), len(B))


def overlap_score(A, B):
    if (len(A) == 0) | (len(B) == 0):
        return 0
    else:
        return (len(A) + len(B)) / (2*len(A)*len(B)) * len(A & B)


def boolean(A, B, p):
    return 0 if len(A & B) / max(len(A), len(B)) < p else 1


def return_intersection_function(name='jaccard'):
    dict_funcs = {'JACCARD':jaccard, 'WAVE_HEDGES': wave_hedges, 'TANIMOTO': tanimoto,
                  'MAX': max_coefficient, 'MIN': min_coefficient, 'OVERLAP': overlap_score,
                  'BOOL': boolean}

    return dict_funcs[name.upper()]

