import numpy as np
from numpy.linalg import norm
from sklearn.utils import shuffle
from sklearn.base import RegressorMixin
from sklearn.linear_model._base import LinearModel

import warnings

warnings.simplefilter(action='ignore', category=UserWarning)

import pandas as pd


class Learning_regressor(RegressorMixin, LinearModel):
    def __init__(self, censored_flags, t_cen):
        super(Learning_regressor, self).__init__()
        self.censored_flags = censored_flags
        self.t_cen = t_cen
        self.lr = 1e-5
        self.reg = 1e-2
        self.epoch = 2
        self.alpha = 1
        self.init_beta = None
        self.intercept_guess = None
        self.gamma = 0.

    def set_hyperparameters(self, lr=None, reg=None, epoch=None, alpha=None, init_beta_guess=None, gamma=None,
                            intercept_guess=None):
        if lr is not None:
            self.lr = lr
        if reg is not None:
            self.reg = reg
        if epoch is not None:
            self.epoch = epoch
        if alpha is not None:
            self.alpha = alpha
        if init_beta_guess is not None:
            self.init_beta = init_beta_guess
        if intercept_guess is not None:
            self.intercept_guess = intercept_guess
        if gamma is not None:
            self.gamma = gamma

    def predict(self, X):
        return (X @ self.coef_ + self.intercept_)

    def loss(self, X, y):
        y_hat = self.predict(X)
        return (norm(y_hat - y) ** 2) + self.reg * norm(self.coef_) ** 2

    def update_rule(self, X, Z, beta):
        raise NotImplementedError

    def fit(self, X_, y):
        """Fit model."""
        bias = pd.Series(np.ones(X_.shape[0]), name="bias")
        bias.index = X_.index
        X = X_.join(bias)

        self.uncensored_x = X[self.censored_flags == 1]
        self.uncensored_y = y[self.censored_flags == 1]
        self.censored_x = X[self.censored_flags == 0]

        if self.init_beta is not None:
            if len(self.init_beta) != X_.shape[1]:
                raise IndexError(
                    f"The shape of the initial guess {len(self.init_beta)} is not equal to the shape of X {X_.shape[1]}.")
            beta = self.init_beta
            if self.intercept_guess is not None:
                beta = np.append(beta, self.intercept_guess)
            else:
                beta = np.append(beta, np.random.randn(1))
        else:
            beta = np.random.randn(X.shape[1])

        self.intercept_ = self.intercept_guess
        self.coef_ = beta[:-1]

        L = []
        g_norm = []
        for epoch in range(self.epoch):
            Z = shuffle(X.index, (self.censored_flags == 0.), y)
            beta = self.update_rule(X, Z, beta)

            try:
                self.intercept_ = beta["bias"]
            except:
                self.intercept_ = beta[-1]
            self.coef_ = beta[:X.shape[1] - 1]  # .values

            l = self.loss(X_, y)
            g_norm.append(self.norm_of_gradient)
            L.append(l)


class GD_regressor(Learning_regressor):
    def __init__(self, censored_flags, t_cen):
        super().__init__(censored_flags, t_cen)

    def update_rule(self, X: pd.DataFrame, Z, beta):
        """
        Update the model.
        @param X: The data to predict with a 1 vector in the end (for the bias)
        @param Z: List with 3 components:
            Z[0]- names of the rows in X.
            Z[1] - A true/false vector indicating if the chosen data is censored or not.
            Z[2] - The tag.
        @param beta: The current weights with the intercept at the end.
        @return: The new weights vector
        """
        # save the norm of the gradient for plotting:
        censored_data = X[Z[1]]
        uncensored_data = X[~Z[1]]

        uncensored_update = (
                self.lr * ((uncensored_data.dot(beta) - Z[2]).dropna() @ uncensored_data + self.reg * beta))

        censored_pred = censored_data @ beta

        censored_data_right = censored_data[(self.t_cen - censored_pred) < 0]
        censored_data_wrong = censored_data[(self.t_cen - censored_pred) > 0]
        censored_right_update = beta * self.alpha * self.lr * self.reg
        if len(censored_data_wrong) == 0:
            censored_wrong_update = 0
        else:
            censored_wrong_update = self.lr * (
                    (self.t_cen - censored_data_wrong.dot(beta)).dropna().dot(-censored_data_wrong) * self.alpha +
                    self.gamma * (Z[2] - censored_data_wrong.dot(beta)).dropna().dot(-censored_data_wrong)
                    + self.reg * beta * self.alpha
            )

        update = (uncensored_update * len(uncensored_data) + censored_right_update * len(
            censored_data_right) + censored_wrong_update * len(censored_data_wrong)) / len(X)

        self.norm_of_gradient = norm(update / self.lr)
        return beta - update
