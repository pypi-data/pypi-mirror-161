from chembee_actions.get_false_predictions import (
    get_multi_false_predictions,
    get_false_predictions,
)
import numpy as np


def compare_descriptiveness(bees, n=100) -> dict:
    """
    The compare_descriptiveness function takes in a list of Bees and returns the number of unique false positives and negatives for each ChemBee.
    Intended use is web and jupyter notebooks


    :param bees: Used to Pass a list of bee objects.
    :param n=100: Used to Specify the number of times a classifier is fitted on the data and tested on it.
    :return: The number of unique false positive and false negative predictions.

    :doc-author: Julian M. Kleber
    """

    unique_pos = []
    unique_neg = []
    pos = []
    neg = []
    for bee in bees:
        false_pos_indices = []
        false_neg_indices = []
        for i in range(n):
            clf = bee.clf.fit(bee.X_data, bee.y_data.astype(np.int32))
            false_pos, false_neg = get_false_predictions(
                fitted_clf=clf, X_data=bee.X_data, y_true=bee.y_data.astype(np.int32)
            )
            false_pos_indices += false_pos
            false_neg_indices += false_neg
        unique_pos.append(len(np.unique(false_pos_indices)))
        unique_neg.append(len(np.unique(false_neg_indices)))
        pos.append(len(false_pos_indices))
        neg.append(len(false_neg_indices))
    return unique_pos, unique_neg, pos, neg
