import math
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from MLE_augmentor import FIESTA
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import LabelBinarizer
from customize_regressor import GD_regressor
from sksurv.metrics import concordance_index_censored



def categorizator(stool_uncensor_df, categories, stool_censor_df: pd.DataFrame = None):
    aa = stool_uncensor_df[
        categories]
    stool_uncensor_df = stool_uncensor_df.loc[aa.index]
    if stool_censor_df is not None:
        bb = stool_censor_df[
            categories]
        stool_censor_df = stool_censor_df.loc[bb.index]
        aa = aa.append(bb)

    for col in aa.columns:
        try:
            aa[col].astype(np.float64)
        except:
            aa[col] = aa[col].fillna("unknown")
            le = LabelBinarizer()  # LabelEncoder()
            tmp_mat = le.fit_transform(aa[col])
            tmp_mat = pd.DataFrame(tmp_mat, index=aa.index)
            tmp_mat = tmp_mat.rename(columns=lambda x: str(x) + "_" + col)
            del aa[col]
            aa = aa.join(tmp_mat, rsuffix=col)
    return aa, stool_uncensor_df, stool_censor_df


class LBL:
    """
    suRvival Analysis lefT barrIer lOss (RATIO) and DA combined with Ridge regression
    Minimizes the objective function of:
    Sum on uncensored(||w*x_i -Te_i||^2) + Sum on censored(||w*x_i-Tc_i||^2*I(w*x_i < Tc_i))
    This model solves a regression model where the loss function is the linear least squares function
    for the uncensored data and a linear left barrier loss for the wrong censored samples.
    The user can moderate the relations between the censored and uncensored loss.
    In addition, a regularization is given by the l2-norm. The model uses the Gradient Descent (GD)
    approach for the solution, the initial guess is based on the weights of the regular Ridge regression
    on the uncensored data only.
    """

    def __init__(self, tag_column, id_column, order_of_samples_column, num_of_bact=0, lamda=0.1, beta=1e-3, lr=1e-2,
                 epoch=20, gamma=0, feature_selection=None, only_microbiome=False, normelize=True, categories=None,
                 augmented_censored=False, reg=1e-2, alpha=1, with_microbiome=True):
        """
        Initialize the model with all its relevant parameters. This function also checks the validity of the input
        :param tag_column: Name of tag column (str)
        :param id_column: Name of person id column (str)
        :param order_of_samples_column: Name of the order of samples column, id data is static can put 1 to all
        :param num_of_bact: If there is microbial data, the number of ASVs (optional, int)
        :param lamda: Hyperparameter that determines the censoring rate for second step of DA (float)
        :param beta: Hyperparameter that affects the decreasing rate of dij (float)
        :param lr: Learning rate of Ridge (float)
        :param epoch: Number of GD iterations (int)
        :param gamma: Loss coefficient for DA (float)
        :param feature_selection: Number of features to keep, highest correlative features in train (int)
        :param only_microbiome: If True learns only on the microbiome (bool)
        :param normelize: If True applies z-score to input and output (bool)
        :param categories: List of categorical columns' names (list of str)
        :param augmented_censored: If True applies DA (bool)
        :param reg: Regularization coefficient (float)
        :param alpha: Loss coefficent loss-wrong (float)
        :param with_microbiome: If True uses non microbial features as input (bool)
        """
        self.tag_column = tag_column
        self.id_column = id_column
        self.order_of_samples_column = order_of_samples_column
        self.beta = beta
        self.lamda = lamda
        self.num_of_bact = num_of_bact
        self.categories = categories
        self.HP = {
            "num_of_bact": num_of_bact,
            "lr": lr,
            "epoch": epoch,
            "gamma": gamma,
            "feature_selection": feature_selection,
            "only_microbiome": only_microbiome,
            "normelize": normelize,
            "augmented_censored": augmented_censored,
            "reg": reg,
            "alpha": alpha,
            "with_microbiome": with_microbiome
        }

        if only_microbiome == True and with_microbiome == False:
            raise Exception("Invalid input - if only_microbiome is True with_microbiome must be True as well")

        # if with_microbiome == False and num_of_bact > 0:
        #     raise Exception("Invalid input - if  with_microbiome is True num_of_bact must be higher than 0")

        if augmented_censored == False and gamma != 0:
            raise Exception(
                "Invalid input - try one of the following: augmented_censored = False, gamma=0, augmented_censored = True with every gamma")

    def fit(self, uncensored_data, censored_data):
        """
        Training of the model - making categorical features to numeric, z-score normalization, augmentation if needed.
        :param uncensored_data: A dataframe with all the uncensored samples, must include:
                                    1. A column names "Date" of the date of the sample, the date should be in an American format
                                        of month/day/year
                                    2. A column names "DateEnd" of the date of an event for uncensored,
                                        the date should be in an American format of month/day/year
                                    3. A people column names similar to the people_col parameter, contains the identity of a patient
                                    4. A time column names similar to the time_col parameter, contains the order of samples for sequntial data
                                    5. A tag column names tag with the TTEs
        :param censored_data: A dataframe with all the censored samples, must include:
                                    1. A column names "Date" of the date of the sample, the date should be in an American format
                                        of month/day/year
                                    2. A column names "DateEnd" of the date of a competing event for censored,
                                        the date should be in an American format of month/day/year
                                    3. A people column names similar to the people_col parameter, contains the identity of a patient
                                    4. A time column names similar to the time_col parameter, contains the order of samples (for sequntial data)
                                    5. A tag column names tag with the comperting event times
        :return: None
        """
        augmentor_instance = FIESTA(self.tag_column, censored_data, uncensored_data, self.beta, self.lamda,
                                    self.id_column, self.order_of_samples_column)
        censor_df = augmentor_instance.implement_augment(censored_data)
        censor_df, uncensor_df = augmentor_instance.add_tag_to_predict(censor_df, uncensored_data)
        self._fit(uncensored_data, self.tag_column, self.id_column, stool_censor_df=censor_df, **self.HP)

    def score(self, uncensored_data, Y):
        """
        Calculating the Concordance Index (CI) between the real TTE and the predicted TTE
        Calculating the Spearman correaltion between the real TTE and the predicted TTE
        Calculating the AUC, while making the task binary by predicting before median TTE time in train or after
        :param uncensored_data: A dataframe with all the uncensored samples, must include:
                                    1. A column names "Date" of the date of the sample, the date should be in an American format
                                        of month/day/year
                                    2. A column names "DateEnd" of the date of an event for uncensored,
                                        the date should be in an American format of month/day/year
                                    3. A people column names similar to the people_col parameter, contains the identity of a patient
                                    4. A time column names similar to the time_col parameter, contains the order of samples for sequntial data
                                    5. A tag column names tag with the TTEs
                                Notice: cannot deal with censored data
        :param Y: real TTE
        :return: CI, SCC, p-value, AUC
        """
        X = uncensored_data
        Y_hat = self.predict(X)

        Score = dict()

        Score["ci"] = 1 - concordance_index_censored(np.ones_like(Y).astype(bool), Y, Y_hat)[0]

        spr = spearmanr(Y, Y_hat)
        Score["corr"] = spr.correlation
        Score["pval"] = spr.pvalue

        try:
            Score["auc"] = roc_auc_score(Y > self.Y_median, Y_hat > self.Y_median)
        except:
            Score["auc"] = None
        return Score

    def predict(self, uncensored_data):
        """
        Applying inference based on the trained model. One must all the fit function before the predict function.
        Predict can be used only on uncensored data
        :param uncensored_data: dataframe of uncensored data, cannot deal with censored data
        :return: The predicted TTEs
        """
        if self.HP['only_microbiome'] == False:
            X = categorizator(uncensored_data, self.categories)[0]
        else:
            X = uncensored_data.iloc[:, :-5]

        X = X[[n[0] for n in self.features_selected]]

        if self.HP["normelize"]:
            for col in X.columns:
                if col in self.X_std:
                    X[col] = (X[col] - self.X_mean[col]) / self.X_std[col]
                else:
                    X[col] = (X[col] - self.X_mean[col])

        Y_hat = self.model.predict(X)

        if self.HP["normelize"]:
            Y_hat = (Y_hat * self.Y_std) + self.Y_mean

        return Y_hat

    def _fit(self, stool_uncensor_df: pd.DataFrame, tag, people_col, num_of_bact, feature_selection=20,
             gamma=None, only_microbiome=False, augmented_censored=True,
             stool_censor_df: pd.DataFrame = None, lr=None, epoch=None, reg=None, alpha=None,
             normelize=False, with_microbiome=False):
        """
        The training of the model, in this implementation it is a Ridge regression with the additional loss and an optional DA
        :param stool_uncensor_df: A dataframe with all the uncensored samples, must include:
                                    1. A column names "Date" of the date of the sample, the date should be in an American format
                                        of month/day/year
                                    2. A column names "DateEnd" of the date of an event for uncensored,
                                        the date should be in an American format of month/day/year
                                    3. A people column names similar to the people_col parameter, contains the identity of a patient
                                    4. A time column names similar to the time_col parameter, contains the order of samples for sequntial data
                                    5. A tag column names tag with the TTEs

        :param tag: Name of tag column (str)
        :param people_col: Name of patients id column (str)
        :param num_of_bact: Number of microbiome in dataset if exists (int)
        :param feature_selection: Number of features to keep (int)
        :param gamma: Loss coefficient for DA (float)
        :param only_microbiome: If True learns only on the microbiome (bool)
        :param augmented_censored: If True applies DA (bool)
        :param stool_censor_df: A dataframe with all the censored samples, must include:
                                    1. A column names "Date" of the date of the sample, the date should be in an American format
                                        of month/day/year
                                    2. A column names "DateEnd" of the date of a competing event for censored,
                                        the date should be in an American format of month/day/year
                                    3. A people column names similar to the people_col parameter, contains the identity of a patient
                                    4. A time column names similar to the time_col parameter, contains the order of samples for sequntial data
                                    5. A tag column names tag with the TTEs
        :param lr: Learning rate of Ridge (float)
        :param epoch: Number of GD iterations (int)
        :param reg: Regularization coefficient (float)
        :param alpha: Loss coefficent loss-wrong (float)
        :param normelize: If True applies z-score to input and output (bool)
        :param with_microbiome: If True uses non microbial features as input (bool)
        :return: None
        """
        if only_microbiome and not with_microbiome:
            Exception("only_microbiome and with_microbiome flags contradict")
        if stool_censor_df is None:
            cols = list(stool_uncensor_df.columns)
            cols.extend([tag + "_for_loss"])
            stool_censor_df = pd.DataFrame(columns=cols)
        elif augmented_censored == False:
            stool_censor_df["time_to_" + tag] = stool_censor_df[tag + "_for_loss"]

        if not with_microbiome:
            gg = stool_uncensor_df.groupby(people_col)
            tmp_df = pd.DataFrame(columns=stool_uncensor_df.columns)
            for g in gg:
                tmp_df = tmp_df.append(g[1].iloc[0])
            stool_uncensor_df = tmp_df
            if stool_censor_df is not None:
                gg = stool_censor_df.groupby(people_col)
                tmp_df = pd.DataFrame(columns=stool_censor_df.columns)
                for g in gg:
                    tmp_df = tmp_df.append(g[1].iloc[0])
                stool_censor_df = tmp_df

        aa1 = stool_uncensor_df[stool_uncensor_df.columns[:num_of_bact]]
        if stool_censor_df is not None:
            aa1 = aa1.append(stool_censor_df[stool_censor_df.columns[:num_of_bact]])
        if only_microbiome == False:
            aa, stool_uncensor_df, stool_censor_df = categorizator(stool_uncensor_df, self.categories, stool_censor_df)

        if only_microbiome:
            aa = aa1
        elif with_microbiome:
            aa = aa.join(aa1)

        X = aa

        if normelize:
            self.X_std = dict()
            self.X_mean = dict()
            for col in X.columns:
                # zscore
                self.X_mean[col] = X[col].mean()
                if X[col].std(ddof=0) != 0:
                    self.X_std[col] = X[col].std(ddof=0)
                    X[col] = (X[col] - X[col].mean()) / X[col].std(ddof=0)
                else:

                    X[col] = (X[col] - X[col].mean())

        num_of_uncensored_in_train = len(stool_uncensor_df["time_to_" + tag])
        if stool_censor_df is not None:
            Y = stool_uncensor_df["time_to_" + tag].append(stool_censor_df["time_to_" + tag])
            best_f = self._feature_selector(X, Y, feature_selection=feature_selection,
                                            last_uncensored_sample=num_of_uncensored_in_train)
        else:
            Y = stool_uncensor_df["time_to_" + tag]
            best_f = self._feature_selector(X, Y, feature_selection=feature_selection)
        self.features_selected = best_f

        X = X[[n[0] for n in best_f]]

        self.Y_median = Y.median()

        if normelize:
            self.Y_mean = Y.mean()
            self.Y_std = Y.std(ddof=0)
            Y = (Y - Y.mean()) / Y.std(ddof=0)

        censored_flags = np.hstack([np.ones(num_of_uncensored_in_train), np.zeros(len(Y) - num_of_uncensored_in_train)])

        # GD
        kk = Ridge(fit_intercept=True, tol=0, max_iter=epoch)
        kk.fit(X, Y)

        self.model = GD_regressor(censored_flags, stool_censor_df[tag + "_for_loss"])
        self.model.set_hyperparameters(lr=lr, epoch=epoch, reg=reg, alpha=alpha, init_beta_guess=kk.coef_, gamma=gamma,
                                       intercept_guess=kk.intercept_)
        self.model.fit(X, Y)

    def _feature_selector(self, X, Y, feature_selection=15, last_uncensored_sample=None):
        """
        Choosing the Kth highest correlative feature in regard to the TTE on the taining set
        :param X: Features dataframe
        :param Y: Tag
        :param feature_selection: Number of features to keep
        :param last_uncensored_sample: Dataframe of only the last sample of patient if he has more than one sample
        :return: List of names of best features
        """
        max_l = []
        for col in X:
            if max(X[col][:last_uncensored_sample].isna()):
                continue
            if X[col][:last_uncensored_sample].values.max() == X[col][:last_uncensored_sample].values.min():
                continue
            sp = spearmanr(X[col][:last_uncensored_sample], Y[:last_uncensored_sample])[0]
            if not math.isnan(sp):
                max_l.append((col, sp))
        best_features = sorted(max_l, key=lambda x: abs(x[1]), reverse=True)[:feature_selection]
        return best_features
