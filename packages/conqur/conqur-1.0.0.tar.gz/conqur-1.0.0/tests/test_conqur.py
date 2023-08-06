#!/usr/bin/env python

"""Tests for `conqur` package."""

import unittest
import numpy as np
import pandas as pd

from conqur import scaler


def r_initial_matrix():
    with open("resources/initial_matrix_for_test.txt") as file:
        X_batchid = np.array(pd.read_csv(file, sep=" "))
        X_with_batch_columns = np.zeros((273, 107))
        X_with_batch_columns[:, range(100)] = X_batchid[:, range(100)]
        X_with_batch_columns[:, range(103, 107)] = X_batchid[:, range(101, 105)]
        for j in range(273):
            if X_batchid[j][100] == 0:
                X_with_batch_columns[j][100] = 1
            elif X_batchid[j][100] == 1:
                X_with_batch_columns[j][101] = 1
            else:
                X_with_batch_columns[j][102] = 1
        indexes = np.array([2] + list(range(100, 107)))
        X_with_batch_columns = X_with_batch_columns[:, indexes]
        return X_with_batch_columns


def r_corrected_matrix_1():
    with open("resources/matrix_corrected_for_test_1.txt") as file:
        return np.array(pd.read_csv(file, sep=" "))


def r_corrected_matrix_2():
    with open("resources/matrix_corrected_for_test_2.txt") as file:
        return np.array(pd.read_csv(file, sep=" "))


class TestConqur(unittest.TestCase):
    """Tests for `conqur` package."""

    def test_from_R_data_1(self):
        ConQur_class = scaler.ConQur(
            np.array([1, 2, 3]),
            np.array([4, 5, 6, 7]),
            {1: 1, 2: 0, 3: 0},
            penalty="none",
            alphas=0.0,
            C_for_logit=1.0,
            random_state_distribution=10,
        )
        Xt = ConQur_class.fit_transform(r_initial_matrix())
        res = r_corrected_matrix_1()[:, 2] - Xt[:, 0]
        res[abs(res) <= 1] = 0.0
        assert np.array_equal(res, np.zeros(len(res)))

    def test_from_R_data_2(self):
        X = r_initial_matrix()
        p = 7
        alphas = np.array([(2 * p) / len(X[:, 0][X[:, 0] != 0])])
        ConQur_class = scaler.ConQur(
            np.array([1, 2, 3]),
            np.array([4, 5, 6, 7]),
            {1: 1, 2: 0, 3: 0},
            penalty="l1",
            solver_logit="liblinear",
            C_for_logit=np.array([0.3]),
            alphas=alphas,
            interplt_delta=0.4999,
            random_state_distribution=10,
        )
        Xt = ConQur_class.fit_transform(r_initial_matrix())
        res = r_corrected_matrix_2()[:, 2] - Xt[:, 0]
        res[abs(res) <= 1] = 0.0
        assert np.array_equal(res, np.zeros(len(res)))

    def test_synthetic_data_1(self):
        len = 150
        np.random.seed(15)
        covariate = np.random.normal(loc=2.0, scale=1.0, size=len)
        covariate[covariate < 0] = 2.0
        np.random.seed(12)
        batch_help = np.random.uniform(-1, 1, len)
        batch = np.zeros(len)
        batch[batch_help > 0] = 1
        np.random.seed(16)
        a = np.random.uniform(2.0, 20.0)
        np.random.seed(11)
        b = np.random.uniform(6.0, 100.0)
        feature = a * batch + b * covariate
        feature_reference = b * covariate
        X = np.dstack((feature, batch, covariate))[0]
        ConQur_class = scaler.ConQur(
            np.array([1]),
            np.array([2]),
            {1: 0},
            integer_columns=[],
            penalty="none",
            alphas=0.0,
        )
        Xt = ConQur_class.fit_transform(X)
        res = feature_reference - Xt[:, 0]
        res[res < 1 / 100000000] = 0.0
        assert np.array_equal(res, np.zeros(len))

    def test_synthetic_data_2(self):
        len = 150
        np.random.seed(15)
        covariate = np.random.normal(loc=2.0, scale=1.0, size=len)
        covariate[covariate < 0] = 2.0
        np.random.seed(12)
        batch_help = np.random.uniform(-1, 1, len)
        batch = np.zeros(len)
        batch[batch_help > 0] = 1
        np.random.seed(16)
        a = np.random.uniform(2.0, 20.0)
        np.random.seed(11)
        b = np.random.uniform(6.0, 100.0)
        np.random.seed(20)
        feature_help = np.random.uniform(0, 1, len)
        feature = np.zeros(len)
        feature[feature_help > 0.2] = (
            a * batch[feature_help > 0.2] + b * covariate[feature_help > 0.2]
        )
        feature_reference = np.zeros(len)
        feature_reference[feature_help > 0.2] = b * covariate[feature_help > 0.2]
        X = np.dstack((feature, batch, covariate))[0]
        ConQur_class = scaler.ConQur(
            np.array([1]),
            np.array([2]),
            {1: 0},
            integer_columns=[],
            penalty="none",
            alphas=0.0,
        )
        Xt = ConQur_class.fit_transform(X)
        res = feature_reference - Xt[:, 0]
        res[res <= 1] = 0.0
        assert np.array_equal(res, np.zeros(len))
