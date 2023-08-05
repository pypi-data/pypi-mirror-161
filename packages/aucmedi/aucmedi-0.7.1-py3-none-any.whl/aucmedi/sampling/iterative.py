#==============================================================================#
#  Author:       Dominik Müller                                                #
#  Copyright:    2022 IT-Infrastructure for Translational Medical Research,    #
#                University of Augsburg                                        #
#                                                                              #
#  This program is free software: you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by        #
#  the Free Software Foundation, either version 3 of the License, or           #
#  (at your option) any later version.                                         #
#                                                                              #
#  This program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#==============================================================================#
#-----------------------------------------------------#
#                    Documentation                    #
#-----------------------------------------------------#
""" Internal classes to allow iterative stratification in percentage-split and
    k-fold cross-validation for multi-label sampling.

Use the corresponding core functions from [aucmedi.sampling.split][] and [aucmedi.sampling.kfold][]
with the parameter `iterative=True`.

???+ info "Personal Note"
    This code originates from [https://github.com/trent-b](https://github.com/trent-b).

    If you are reading this, leave trent-b a star on his GitHub! :)  <br>
    His code is open-source, really well written and structured.

??? abstract "Reference - Implementation"
    Author: trend-b <br>
    GitHub Profile: https://github.com/trent-b <br>
    https://github.com/trent-b/iterative-stratification <br>

??? abstract "Reference - Publication"
    Sechidis K., Tsoumakas G., Vlahavas I. 2011.
    On the Stratification of Multi-Label Data.
    Machine Learning and Knowledge Discovery in Databases. ECML PKDD 2011.
    Lecture Notes in Computer Science, vol 6913. Springer, Berlin, Heidelberg.
    Aristotle University of Thessaloniki.
    <br>
    https://link.springer.com/chapter/10.1007/978-3-642-23808-6_10
"""
#-----------------------------------------------------#
#                   Library imports                   #
#-----------------------------------------------------#
# External libraries
import numpy as np
from sklearn.utils import check_random_state
from sklearn.utils.validation import _num_samples, check_array
from sklearn.utils.multiclass import type_of_target
from sklearn.model_selection._split import _BaseKFold, _RepeatedSplits, \
                                    BaseShuffleSplit, _validate_shuffle_split

#-----------------------------------------------------#
#       Subfunction for Iterative Stratification      #
#-----------------------------------------------------#
def IterativeStratification(labels, r, random_state):
    """This function implements the Iterative Stratification algorithm described
    in the following paper:

    ??? abstract "Reference - Publication"
        Sechidis K., Tsoumakas G., Vlahavas I. 2011.
        On the Stratification of Multi-Label Data.
        Machine Learning and Knowledge Discovery in Databases. ECML PKDD 2011.
        Lecture Notes in Computer Science, vol 6913. Springer, Berlin, Heidelberg.
        Aristotle University of Thessaloniki.
        <br>
        https://link.springer.com/chapter/10.1007/978-3-642-23808-6_10
    """

    n_samples = labels.shape[0]
    test_folds = np.zeros(n_samples, dtype=int)

    # Calculate the desired number of examples at each subset
    c_folds = r * n_samples

    # Calculate the desired number of examples of each label at each subset
    c_folds_labels = np.outer(r, labels.sum(axis=0))

    labels_not_processed_mask = np.ones(n_samples, dtype=bool)

    while np.any(labels_not_processed_mask):
        # Find the label with the fewest (but at least one) remaining examples,
        # breaking ties randomly
        num_labels = labels[labels_not_processed_mask].sum(axis=0)

        # Handle case where only all-zero labels are left by distributing
        # across all folds as evenly as possible (not in original algorithm but
        # mentioned in the text). (By handling this case separately, some
        # code redundancy is introduced; however, this approach allows for
        # decreased execution time when there are a relatively large number
        # of all-zero labels.)
        if num_labels.sum() == 0:
            sample_idxs = np.where(labels_not_processed_mask)[0]

            for sample_idx in sample_idxs:
                fold_idx = np.where(c_folds == c_folds.max())[0]

                if fold_idx.shape[0] > 1:
                    fold_idx = fold_idx[random_state.choice(fold_idx.shape[0])]

                test_folds[sample_idx] = fold_idx
                c_folds[fold_idx] -= 1

            break

        label_idx = np.where(num_labels == num_labels[np.nonzero(num_labels)].min())[0]
        if label_idx.shape[0] > 1:
            label_idx = label_idx[random_state.choice(label_idx.shape[0])]

        sample_idxs = np.where(np.logical_and(labels[:, label_idx].flatten(), labels_not_processed_mask))[0]

        for sample_idx in sample_idxs:
            # Find the subset(s) with the largest number of desired examples
            # for this label, breaking ties by considering the largest number
            # of desired examples, breaking further ties randomly
            label_folds = c_folds_labels[:, label_idx]
            fold_idx = np.where(label_folds == label_folds.max())[0]

            if fold_idx.shape[0] > 1:
                temp_fold_idx = np.where(c_folds[fold_idx] ==
                                         c_folds[fold_idx].max())[0]
                fold_idx = fold_idx[temp_fold_idx]

                if temp_fold_idx.shape[0] > 1:
                    fold_idx = fold_idx[random_state.choice(temp_fold_idx.shape[0])]

            test_folds[sample_idx] = fold_idx
            labels_not_processed_mask[sample_idx] = False

            # Update desired number of examples
            c_folds_labels[fold_idx, labels[sample_idx]] -= 1
            c_folds[fold_idx] -= 1

    return test_folds

#-----------------------------------------------------#
#     KFold Sampling via Iterative Stratification     #
#-----------------------------------------------------#
class MultilabelStratifiedKFold(_BaseKFold):
    """Multilabel stratified K-Folds cross-validator.

    Provides train/test indices to split multilabel data into train/test sets.
    This cross-validation object is a variation of KFold that returns
    stratified folds for multilabel data. The folds are made by preserving
    the percentage of samples for each label.

    ??? example
        ```python
        >>> from iterstrat.ml_stratifiers import MultilabelStratifiedKFold
        >>> import numpy as np
        >>> X = np.array([[1,2], [3,4], [1,2], [3,4], [1,2], [3,4], [1,2], [3,4]])
        >>> y = np.array([[0,0], [0,0], [0,1], [0,1], [1,1], [1,1], [1,0], [1,0]])
        >>> mskf = MultilabelStratifiedKFold(n_splits=2, random_state=0)
        >>> mskf.get_n_splits(X, y)
        2
        >>> print(mskf)  # doctest: +NORMALIZE_WHITESPACE
        MultilabelStratifiedKFold(n_splits=2, random_state=0, shuffle=False)
        >>> for train_index, test_index in mskf.split(X, y):
        ...    print("TRAIN:", train_index, "TEST:", test_index)
        ...    X_train, X_test = X[train_index], X[test_index]
        ...    y_train, y_test = y[train_index], y[test_index]
        TRAIN: [0 3 4 6] TEST: [1 2 5 7]
        TRAIN: [1 2 5 7] TEST: [0 3 4 6]
        ```

    ???+ note
        Train and test sizes may be slightly different in each fold.

    ???+ note "See also"
        RepeatedMultilabelStratifiedKFold: Repeats Multilabel Stratified K-Fold
        n times.

    """

    def __init__(self, n_splits=3, shuffle=False, random_state=None):
        """
        Args:
            n_splits (int, default=3):      Number of folds. Must be at least 2.
            shuffle (boolean, optional):    Whether to shuffle each stratification of the data before splitting
                                            into batches.
            random_state (int, RandomState instance or None, optional, default=None): If int, random_state is the
                                            seed used by the random number generator;
                                            If RandomState instance, random_state is the random number generator;
                                            If None, the random number generator is the RandomState instance used
                                            by `np.random`. Unlike StratifiedKFold that only uses random_state
                                            when ``shuffle`` == True, this multilabel implementation
                                            always uses the random_state since the iterative stratification
                                            algorithm breaks ties randomly.
        """
        super(MultilabelStratifiedKFold, self).__init__(n_splits=n_splits, shuffle=shuffle, random_state=random_state)

    def _make_test_folds(self, X, y):
        y = np.asarray(y, dtype=bool)
        type_of_target_y = type_of_target(y)

        if type_of_target_y != 'multilabel-indicator':
            raise ValueError(
                'Supported target type is: multilabel-indicator. Got {!r} instead.'.format(type_of_target_y))

        num_samples = y.shape[0]

        rng = check_random_state(self.random_state)
        indices = np.arange(num_samples)

        if self.shuffle:
            rng.shuffle(indices)
            y = y[indices]

        r = np.asarray([1 / self.n_splits] * self.n_splits)

        test_folds = IterativeStratification(labels=y, r=r, random_state=rng)

        return test_folds[np.argsort(indices)]

    def _iter_test_masks(self, X=None, y=None, groups=None):
        test_folds = self._make_test_folds(X, y)
        for i in range(self.n_splits):
            yield test_folds == i

    def split(self, X, y, groups=None):
        """ Generate indices to split data into training and test set.

        ???+ note
            Randomized CV splitters may return different results for each call of
            split. You can make the results identical by setting ``random_state``
            to an integer.: train->     The training set indices for that split.

        Args:
            X (array-like, shape (n_samples, n_features) ): Training data, where n_samples is the number of samples
                                                            and n_features is the number of features.
                                                            Note that providing ``y`` is sufficient to generate the splits and
                                                            hence ``np.zeros(n_samples)`` may be used as a placeholder for
                                                            ``X`` instead of actual training data.
            y (array-like, shape (n_samples, n_labels) ):   The target variable for supervised learning problems.
                                                            Multilabel stratification is done based on the y labels.
            groups (object, optional):                      Always ignored, exists for compatibility.

        Returns:
          train (numpy.ndarray):        The training set indices for that split.
          test (numpy.ndarray):         The testing set indices for that split.
        """
        y = check_array(y, ensure_2d=False, dtype=None)
        return super(MultilabelStratifiedKFold, self).split(X, y, groups)

#-----------------------------------------------------#
#     Split Sampling via Iterative Stratification     #
#-----------------------------------------------------#
class MultilabelStratifiedShuffleSplit(BaseShuffleSplit):
    """Multilabel Stratified ShuffleSplit cross-validator.

    Provides train/test indices to split data into train/test sets.
    This cross-validation object is a merge of MultilabelStratifiedKFold and
    ShuffleSplit, which returns stratified randomized folds for multilabel
    data. The folds are made by preserving the percentage of each label.
    Note: like the ShuffleSplit strategy, multilabel stratified random splits
    do not guarantee that all folds will be different, although this is
    still very likely for sizeable datasets.

    ??? example
        ```python
        >>> from iterstrat.ml_stratifiers import MultilabelStratifiedShuffleSplit
        >>> import numpy as np
        >>> X = np.array([[1,2], [3,4], [1,2], [3,4], [1,2], [3,4], [1,2], [3,4]])
        >>> y = np.array([[0,0], [0,0], [0,1], [0,1], [1,1], [1,1], [1,0], [1,0]])
        >>> msss = MultilabelStratifiedShuffleSplit(n_splits=3, test_size=0.5,
        ...    random_state=0)
        >>> msss.get_n_splits(X, y)
        3
        >>> print(mss)       # doctest: +ELLIPSIS
        MultilabelStratifiedShuffleSplit(n_splits=3, random_state=0, test_size=0.5,
                                         train_size=None)
        >>> for train_index, test_index in msss.split(X, y):
        ...    print("TRAIN:", train_index, "TEST:", test_index)
        ...    X_train, X_test = X[train_index], X[test_index]
        ...    y_train, y_test = y[train_index], y[test_index]
        TRAIN: [1 2 5 7] TEST: [0 3 4 6]
        TRAIN: [2 3 6 7] TEST: [0 1 4 5]
        TRAIN: [1 2 5 6] TEST: [0 3 4 7]
        ```

    ???+ note
        Train and test sizes may be slightly different from desired due to the
        preference of stratification over perfectly sized folds.
    """

    def __init__(self, n_splits=10, test_size="default", train_size=None,
                 random_state=None):
        """
        Args:
            n_splits (int):                         Number of re-shuffling & splitting iterations.
            test_size (float, int, None, optional): If float, should be between 0.0 and 1.0 and represent the proportion
                                                    of the dataset to include in the test split. If int, represents the
                                                    absolute number of test samples. If None, the value is set to the
                                                    complement of the train size. By default, the value is set to 0.1.
                                                    The default will change in version 0.21. It will remain 0.1 only
                                                    if ``train_size`` is unspecified, otherwise it will complement
                                                    the specified ``train_size``.
            train_size (float, int, or None, default is None):  If float, should be between 0.0 and 1.0 and represent the
                                                    proportion of the dataset to include in the train split. If
                                                    int, represents the absolute number of train samples. If None,
                                                    the value is automatically set to the complement of the test size.
            random_state (int, RandomState instance or None, optional): If int, random_state is the seed used by the random number generator;
                                                    If RandomState instance, random_state is the random number generator;
                                                    If None, the random number generator is the RandomState instance used
                                                    by `np.random`. Unlike StratifiedShuffleSplit that only uses
                                                    random_state when ``shuffle`` == True, this multilabel implementation
                                                    always uses the random_state since the iterative stratification
                                                    algorithm breaks ties randomly.
        """
        super(MultilabelStratifiedShuffleSplit, self).__init__(
            n_splits=n_splits, test_size=test_size, train_size=train_size, random_state=random_state)

    def _iter_indices(self, X, y, groups=None):
        n_samples = _num_samples(X)
        y = check_array(y, ensure_2d=False, dtype=None)
        y = np.asarray(y, dtype=bool)
        type_of_target_y = type_of_target(y)

        if type_of_target_y != 'multilabel-indicator':
            raise ValueError(
                'Supported target type is: multilabel-indicator. Got {!r} instead.'.format(
                    type_of_target_y))

        n_train, n_test = _validate_shuffle_split(n_samples, self.test_size,
                                                  self.train_size)

        n_samples = y.shape[0]
        rng = check_random_state(self.random_state)
        y_orig = y.copy()

        r = np.array([n_train, n_test]) / (n_train + n_test)

        for _ in range(self.n_splits):
            indices = np.arange(n_samples)
            rng.shuffle(indices)
            y = y_orig[indices]

            test_folds = IterativeStratification(labels=y, r=r, random_state=rng)

            test_idx = test_folds[np.argsort(indices)] == 1
            test = np.where(test_idx)[0]
            train = np.where(~test_idx)[0]

            yield train, test

    def split(self, X, y, groups=None):
        """Generate indices to split data into training and test set.

        ???+ note
            Randomized CV splitters may return different results for each call of
            split. You can make the results identical by setting ``random_state``
            to an integer.

        Args:
            X (array-like, shape (n_samples, n_features) ): Training data, where n_samples is the number of samples
                                                            and n_features is the number of features.
                                                            Note that providing ``y`` is sufficient to generate the splits and
                                                            hence ``np.zeros(n_samples)`` may be used as a placeholder for
                                                            ``X`` instead of actual training data.
            y (array-like, shape (n_samples, n_labels) ):   The target variable for supervised learning problems.
                                                            Multilabel stratification is done based on the y labels.
            groups (object, optional):                      Always ignored, exists for compatibility.


        Returns:
            train (numpy.ndarray):        The training set indices for that split.
            test (numpy.ndarray):         The testing set indices for that split.
        """
        y = check_array(y, ensure_2d=False, dtype=None)
        return super(MultilabelStratifiedShuffleSplit, self).split(X, y, groups)
