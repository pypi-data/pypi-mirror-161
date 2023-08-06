class BayesSearchCV:
    """
    Temporary fix for BayesSearchCV. There was compatibility issues between scikit-optimize and scikit-learn 0.2.
    Unfortunately, scikit-optimize is no longer actively maintained and looking for takeover.

    More robust fix should come soon, and this fix should be deprecated.

    Issues to follow:
        - https://github.com/scikit-optimize/scikit-optimize/pull/777
    """
    def __init__(self, *args, **kwargs):
        raise Exception('Use `from skopt import BayesSearchCV`.\n'
                        '\nWhy did this happen?\n'
                        'Scikit-optimize >=0.7 has fixed their incompatibility with scikit-learn so that you can '
                        'use BayesSearchCV from skopt instead of jcopml.')
