import sklearn.linear_model
import numpy as np


class ConQur(sklearn.base.TransformerMixin):
    """
    Parameters
    ----------
    batch_columns : A list of batch columns.

    covariates_columns : A list of covariates columns, which contains the key variable of interest and other
    covariates for each feature.

    reference_values : A dict of reference values of batches, the size of the dict must be equal to the number
    of batch columns.

    integer_columns : A list of columns whose elements are integers. Such columns are understood as a
    discrete distribution, and they need to be shifted by uniform distribution to make the
    underlying distribution continuous. Must not intersect with covariates_columns and batch_columns. [], if all features
    do not need to be shifted. If None, then all columns of features are shifted; default is None.

    penalty : See sklearn.linear_model.LogisticRegression; penalty parameter.

    dual : See sklearn.linear_model.LogisticRegression; dual parameter.

    tol : See sklearn.linear_model.LogisticRegression; tol parameter.

    C_for_logit : A list of L1-regularization constants for logistic regression or just float for it, the size of the
    list must be equal to the number of feature columns. If a float is passed, then the regularization constants will
    be the same for all features and equal to the passed float. The default value is equal to None, but the code will be
    executed on the list np.array(1.0, ..., 1.0).

    fit_intercept_logit : The same as fit_intercept parameter, see sklearn.linear_model.LogisticRegression.

    intercept_scaling : See sklearn.linear_model.LogisticRegression; intercept_scaling parameter.

    class_weight : See sklearn.linear_model.LogisticRegression; class_weight parameter.

    random_state : See sklearn.linear_model.LogisticRegression; random_state parameter.

    solver_logit : The same as solver parameter, see sklearn.linear_model.LogisticRegression.

    max_iter : See sklearn.linear_model.LogisticRegression; max_iter parameter.

    multi_class : See sklearn.linear_model.LogisticRegression; multi_class parameter.

    verbose : See sklearn.linear_model.LogisticRegression; verbose parameter.

    warm_start : See sklearn.linear_model.LogisticRegression; warm_start parameter.

    n_jobs : See sklearn.linear_model.LogisticRegression; n_jobs parameter.

    l1_ratio : See sklearn.linear_model.LogisticRegression; l1_ratio parameter.

    alphas : A list of L1-regularization constants for quantile regression or just float for it, the size of the list
    must be equal to the number of feature columns. If a float is passed, then the regularization constants will be the
    same for all features and equal to the passed float. The default value is equal to None, but the code will be
    executed on the list np.array(1.0, ..., 1.0).

    fit_intercept_quantile : The same as fit_intercept parameter, see sklearn.linear_model.QuantileRegressor.

    solver_quantile : The same as solver, see sklearn.linear_model.QuantileRegressor; penalty parameter. But in this
    class, the default value is 'highs-ds'.

    solver_options : See sklearn.linear_model.QuantileRegressor; solver_options parameter.

    quantiles : A sequence of quantile levels, determing the “precision” of estimating conditional quantile functions;
    the default value is equal to None, but the code will be executed on the list
    np.linspace(0.05, 1, 199, endpoint=False).

    interplt_delta : A float constant in (0, 0.5), determing the size of the interpolation window
    for using the data-driven linear interpolation between zero and non-zero quantiles to stabilize border estimates.
    None, if you don't use data-driven linear interpolation; default is None.

    random_state_distribution : A positive integer constant that fix random bits to generate a uniform distributions.
    If None, then the uniform distributions will be generated randomly; default is None.


    """

    def __init__(
        self,
        batch_columns,
        covariates_columns,
        reference_values,
        *,
        integer_columns=None,
        penalty="l2",
        dual=False,
        tol=1e-4,
        C_for_logit=None,
        fit_intercept_logit=True,
        intercept_scaling=1,
        class_weight=None,
        random_state=None,
        solver_logit="lbfgs",
        max_iter=100,
        multi_class="auto",
        verbose=0,
        warm_start=False,
        n_jobs=None,
        l1_ratio=None,
        alphas=None,
        fit_intercept_quantile=True,
        solver_quantile="highs-ds",
        solver_options=None,
        quantiles=None,
        interplt_delta=None,
        random_state_distribution=None
    ):
        self.batch_columns = batch_columns
        self.covariates_columns = covariates_columns
        self.reference_values = reference_values
        self.integer_columns = integer_columns
        self.penalty = penalty
        self.dual = dual
        self.tol = tol
        self.C_for_logit = C_for_logit
        self.fit_intercept_logit = fit_intercept_logit
        self.intercept_scaling = intercept_scaling
        self.class_weight = class_weight
        self.random_state = random_state
        self.solver_logit = solver_logit
        self.max_iter = max_iter
        self.multi_class = multi_class
        self.verbose = verbose
        self.warm_start = warm_start
        self.n_jobs = n_jobs
        self.l1_ratio = l1_ratio
        self.alphas = alphas
        self.fit_intercept_quantile = fit_intercept_quantile
        self.solver_quantile = solver_quantile
        self.solver_options = solver_options
        if quantiles is None:
            self.quantiles = np.linspace(0.05, 1, 199, endpoint=False)
        else:
            self.quantiles = quantiles
        self.interplt_delta = interplt_delta
        self.random_state_distribution = random_state_distribution

    def fit(self, X):
        """
        Parameters
        ----------
        X : Array-like of shape (n_samples, j_features)
            Training matrix, where `n_samples` is the number of samples for some i-th feature
            and `j_features` is the number of feature of this sample.

        Returns
        -------
        self
            Fitted scaler.


        """
        batch_and_covariates_indexes = np.hstack(
            (self.batch_columns, self.covariates_columns)
        )
        X_batch_and_covariates = X[:, batch_and_covariates_indexes]
        columns_indexes_set = set(np.arange(0, len(X[0])))
        batch_and_covariates_indexes_set = set(batch_and_covariates_indexes)
        feature_indexes = list(columns_indexes_set - batch_and_covariates_indexes_set)
        feature_indexes = np.array(feature_indexes)
        feature_indexes.sort()
        if self.integer_columns is None:
            integer_columns_indexes = feature_indexes
        else:
            integer_columns_indexes = self.integer_columns
        if self.alphas is None:
            alphas_list = np.ones(len(feature_indexes))
        elif type(self.alphas) == float:
            alphas_list = np.array([self.alphas] * len(feature_indexes))
        else:
            alphas_list = self.alphas
        if self.C_for_logit is None:
            C_list = np.ones(len(feature_indexes))
        elif type(self.C_for_logit) == float:
            C_list = np.array([self.C_for_logit] * len(feature_indexes))
        else:
            C_list = self.C_for_logit
        self.dict_logit_with_batch = dict()
        self.dict_quantile_with_batch = dict()
        for feature in feature_indexes:
            y_initial = X[:, feature]
            y_for_logit = y_initial.copy()
            y_for_logit[y_for_logit != 0] = 1
            if all(y_for_logit == np.ones(len(y_for_logit))):
                self.dict_logit_with_batch[feature] = (1.0, "all_positive")
            elif all(y_for_logit == np.zeros(len(y_for_logit))):
                self.dict_logit_with_batch[feature] = (0.0, "all_equal_to_zero")
                continue
            else:
                logistic_regression = sklearn.linear_model.LogisticRegression(
                    self.penalty,
                    dual=self.dual,
                    tol=self.tol,
                    C=C_list[feature],
                    fit_intercept=self.fit_intercept_logit,
                    intercept_scaling=self.intercept_scaling,
                    class_weight=self.class_weight,
                    random_state=self.random_state,
                    solver=self.solver_logit,
                    max_iter=self.max_iter,
                    multi_class=self.multi_class,
                    verbose=self.verbose,
                    warm_start=self.warm_start,
                    n_jobs=self.n_jobs,
                    l1_ratio=self.l1_ratio,
                )
                self.dict_logit_with_batch[feature] = (
                    logistic_regression.fit(X_batch_and_covariates, y_for_logit),
                    "model",
                )
            y_nonzero = y_initial[y_initial != 0]
            y_nonzero_shifted = y_nonzero
            if feature in integer_columns_indexes:
                if not (self.random_state_distribution is None):
                    np.random.seed(self.random_state_distribution)
                    y_nonzero_shifted = y_nonzero + np.random.uniform(
                        0, 1, len(y_nonzero)
                    )
                else:
                    y_nonzero_shifted = y_nonzero + np.random.uniform(
                        0, 1, len(y_nonzero)
                    )
            X_and_y = np.hstack(
                (X_batch_and_covariates, y_initial.reshape(len(y_initial), 1))
            )
            X_and_y_nonzero = X_and_y[X_and_y[:, -1] != 0]
            X_batch_and_covariates_nonzero = X_and_y_nonzero[:, :-1]
            self.dict_quantile_with_batch[feature] = []
            for quantile in self.quantiles:
                quantile_regression = sklearn.linear_model.QuantileRegressor(
                    quantile=quantile,
                    alpha=alphas_list[feature],
                    fit_intercept=self.fit_intercept_quantile,
                    solver=self.solver_quantile,
                    solver_options=self.solver_options,
                )
                self.dict_quantile_with_batch[feature].append(
                    quantile_regression.fit(
                        X_batch_and_covariates_nonzero, y_nonzero_shifted
                    )
                )
        return self

    def transform(self, X):
        """
        Parameters
        ----------
        X : Array-like of shape  (n_samples, j_features)
            Input data that will be transformed.

        Returns
        -------
        Xt : Ndarray of shape (n_samples, j_features)
            Transformed data.


        """
        Xt = X.copy()
        X_reference = X.copy()
        for i in self.batch_columns:
            X_reference[:, i] = self.reference_values[i]
        batch_and_covariates_indexes = np.hstack(
            (self.batch_columns, self.covariates_columns)
        )
        X_batch_and_covariates = X[:, batch_and_covariates_indexes]
        X_reference = X_reference[:, batch_and_covariates_indexes]
        columns_indexes_set = set(np.arange(0, len(X[0])))
        batch_and_covariates_indexes_set = set(batch_and_covariates_indexes)
        feature_indexes = list(columns_indexes_set - batch_and_covariates_indexes_set)
        feature_indexes = np.array(feature_indexes)
        feature_indexes.sort()
        if self.integer_columns is None:
            integer_columns_indexes = feature_indexes
        else:
            integer_columns_indexes = self.integer_columns
        for feature in feature_indexes:
            y_initial = X[:, feature]
            if self.dict_logit_with_batch[feature][1] == "all_positive":
                y_zero_predicted = np.zeros(len(X_batch_and_covariates))
                y_zero_predicted_nobatch = np.zeros(len(X_batch_and_covariates))
            elif self.dict_logit_with_batch[feature][1] == "all_equal_to_zero":
                Xt[:, feature] = 0
                continue
            else:
                Y_predicted = self.dict_logit_with_batch[feature][0].predict_proba(
                    X_batch_and_covariates
                )
                y_zero_predicted = Y_predicted[:, 0]
                Y_predicted_nobatch = self.dict_logit_with_batch[feature][
                    0
                ].predict_proba(X_reference)
                y_zero_predicted_nobatch = Y_predicted_nobatch[:, 0]
            predictions = dict()
            predictions_nobatch = dict()
            counter_quantile = 0
            for quantile in self.quantiles:
                predictions[quantile] = self.dict_quantile_with_batch[feature][
                    counter_quantile
                ].predict(X_batch_and_covariates)
                if feature in integer_columns_indexes:
                    predictions[quantile] = np.floor(predictions[quantile])
                predictions_nobatch[quantile] = self.dict_quantile_with_batch[feature][
                    counter_quantile
                ].predict(X_reference)
                if feature in integer_columns_indexes:
                    predictions_nobatch[quantile] = np.floor(
                        predictions_nobatch[quantile]
                    )
                counter_quantile += 1
            number_of_samples = len(y_initial)
            for sample in range(number_of_samples):
                zero_path, transition_path, positive_path = [], [], []
                zero_path_nobatch, transition_path_nobatch, positive_path_nobatch = (
                    [],
                    [],
                    [],
                )
                if not (self.interplt_delta is None):
                    zero_path = self.quantiles[
                        self.quantiles < y_zero_predicted[sample]
                    ]
                    zero_path_nobatch = self.quantiles[
                        self.quantiles < y_zero_predicted_nobatch[sample]
                    ]
                    transition_path = (
                        self.quantiles[
                            (y_zero_predicted[sample] <= self.quantiles)
                            * (
                                self.quantiles
                                <= y_zero_predicted[sample]
                                + number_of_samples ** (-self.interplt_delta)
                            )
                        ]
                        - y_zero_predicted[sample]
                    ) * (number_of_samples**self.interplt_delta)
                    transition_path_nobatch = (
                        self.quantiles[
                            (y_zero_predicted_nobatch[sample] <= self.quantiles)
                            * (
                                self.quantiles
                                <= y_zero_predicted_nobatch[sample]
                                + number_of_samples ** (-self.interplt_delta)
                            )
                        ]
                        - y_zero_predicted_nobatch[sample]
                    ) * (number_of_samples**self.interplt_delta)
                    positive_path = (
                        self.quantiles[
                            self.quantiles
                            > y_zero_predicted[sample]
                            + number_of_samples ** (-self.interplt_delta)
                        ]
                        - y_zero_predicted[sample]
                    ) / (1 - y_zero_predicted[sample])
                    positive_path_nobatch = (
                        self.quantiles[
                            self.quantiles
                            > y_zero_predicted_nobatch[sample]
                            + number_of_samples ** (-self.interplt_delta)
                        ]
                        - y_zero_predicted_nobatch[sample]
                    ) / (1 - y_zero_predicted_nobatch[sample])
                    taus_nonzero = np.hstack(
                        (
                            np.array([number_of_samples / (-self.interplt_delta)]),
                            positive_path,
                        )
                    )
                    taus_nonzero_nobatch = np.hstack(
                        (
                            np.array([number_of_samples / (-self.interplt_delta)]),
                            positive_path_nobatch,
                        )
                    )
                else:
                    zero_path = self.quantiles[
                        self.quantiles <= y_zero_predicted[sample]
                    ]
                    zero_path_nobatch = self.quantiles[
                        self.quantiles <= y_zero_predicted_nobatch[sample]
                    ]
                    taus_nonzero = (
                        self.quantiles[self.quantiles > y_zero_predicted[sample]]
                        - y_zero_predicted[sample]
                    ) / (1 - y_zero_predicted[sample])
                    taus_nonzero_nobatch = (
                        self.quantiles[
                            self.quantiles > y_zero_predicted_nobatch[sample]
                        ]
                        - y_zero_predicted_nobatch[sample]
                    ) / (1 - y_zero_predicted_nobatch[sample])
                if len(taus_nonzero) > 0 and taus_nonzero[0] < 1:
                    location = []
                    for tau in taus_nonzero:
                        loc = self.quantiles[
                            abs(self.quantiles - tau) == min(abs(self.quantiles - tau))
                        ]
                        location.append(loc[0])
                    fit = [predictions[i][sample] for i in location]
                    if not (self.interplt_delta is None):
                        predictions_initial_quantiles_correct = (
                            [0 for i in zero_path]
                            + list(fit[0] * transition_path)
                            + fit[1:]
                        )
                    else:
                        predictions_initial_quantiles_correct = [
                            0 for i in zero_path
                        ] + fit
                else:
                    predictions_initial_quantiles_correct = [0 for i in self.quantiles]
                if len(taus_nonzero_nobatch) > 0 and taus_nonzero_nobatch[0] < 1:
                    location = []
                    for tau in taus_nonzero_nobatch:
                        loc = self.quantiles[
                            abs(self.quantiles - tau) == min(abs(self.quantiles - tau))
                        ]
                        location.append(loc[0])
                    fit = [predictions_nobatch[i][sample] for i in location]
                    if not (self.interplt_delta is None):
                        predictions_initial_quantiles_correct_nobatch = (
                            [0 for i in zero_path_nobatch]
                            + list(fit[0] * transition_path_nobatch)
                            + fit[1:]
                        )
                    else:
                        predictions_initial_quantiles_correct_nobatch = [
                            0 for i in zero_path_nobatch
                        ] + fit
                else:
                    predictions_initial_quantiles_correct_nobatch = [
                        0 for i in self.quantiles
                    ]
                y_initial_sample = y_initial[sample]
                y_nobatch = 0
                quantile_for_y_nobatch = []
                for i in range(len(predictions_initial_quantiles_correct)):
                    if y_initial_sample == predictions_initial_quantiles_correct[i]:
                        quantile_for_y_nobatch.append(i)
                if len(quantile_for_y_nobatch) != 0:
                    for index in quantile_for_y_nobatch:
                        y_nobatch += predictions_initial_quantiles_correct_nobatch[
                            index
                        ]
                    if feature in integer_columns_indexes:
                        y_nobatch = round(y_nobatch / len(quantile_for_y_nobatch), 0)
                    else:
                        y_nobatch = y_nobatch / len(quantile_for_y_nobatch)
                else:
                    for i in range(len(predictions_initial_quantiles_correct)):
                        if predictions_initial_quantiles_correct[i] < y_initial_sample:
                            y_nobatch = predictions_initial_quantiles_correct_nobatch[i]
                Xt[sample, feature] = y_nobatch
        return Xt
