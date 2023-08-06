import sys
import numpy as np
import pandas as pd
from scipy.optimize import root_scalar
from natsort import order_by_index, index_natsorted


def in_debug() -> bool:
    gettrace = getattr(sys, 'gettrace', None)
    if gettrace is None:
        # We can't check this
        return False
    elif gettrace():
        return True
    else:
        return False


def last_samples_before_event(data, people_col, time_col) -> pd.DataFrame:
    last = pd.DataFrame(columns=data.columns)
    for i, df in data.groupby(people_col):
        if data[time_col].values.dtype == "str":
            df = df.reindex(index=order_by_index(df.index, index_natsorted(df[time_col])))
        else:
            df = df.sort_values(time_col)
        last = last.append(df.iloc[len(df.index) - 1])
    return last


class Augment(object):
    """
    This class is for the data augmentation for the censored samples.
    """

    def __init__(self, tag: str, censor_df: pd.DataFrame, uncensord_df: pd.DataFrame, beta,
                 people_col, time_col,
                 bacteria_col_keyword="k__", only_last_sample_before_gvhd=True):
        """

        :param otu: otu df with all features and tag
        :param tag: name of tag
        :param censor_df: data frame of only censored samples
        :param uncensord_df: data frame of only uncensored samples
        :param bacteria_col_keyword: a sign for all the columns of bacterias in order to drop the other
                                     irrelevant columns of the sample.
        """
        self.beta = beta
        self.tag = tag
        self.censored_org_tag = censor_df[tag]
        self.uncensored_org_tag = uncensord_df[tag]
        self.people_col = people_col
        self.time_col = time_col

        # remove all columns which are not bacterias:
        self.last_samples_censord = last_samples_before_event(censor_df, self.people_col, self.time_col)
        self.last_samples_censord_only_microbiom = self.last_samples_censord[
            [col for col in censor_df.columns if bacteria_col_keyword in col]]
        self.last_censord_tag_before_event = censor_df[tag].loc[self.last_samples_censord.index]

        self.last_samples_uncensord = last_samples_before_event(uncensord_df,
                                                                self.people_col, self.time_col)
        self.last_samples_uncensord_only_microbiom = self.last_samples_uncensord[
            [col for col in censor_df.columns if bacteria_col_keyword in col]]
        self.last_uncensord_tag_before_event = uncensord_df[tag].loc[self.last_samples_uncensord.index]

    def augment(self, beta=0.01):
        raise NotImplementedError

    def add_tag_to_predict(self, censored_df, uncensored_df):
        raise NotImplementedError

    def augment_fix(self, artificial_time):
        """
        chooses the latest time for event time for censored samples
        :param artificial_time: the result of augment, sereies with artificial time
        :return: data frame with logical event time to censored samples
        """
        fixed_augment = \
            self.last_samples_censord.loc[
                self.last_samples_censord[self.tag].sort_index() >= artificial_time.sort_index()][
                self.tag]
        good_artificials = artificial_time.loc[
            self.last_samples_censord[self.tag].sort_index() < artificial_time.sort_index()]

        # prints the number of logical artificial samples vs unlogical ones
        if in_debug():
            print("Bad artificials: " + str(len(fixed_augment)))
            print("Good artificials: " + str(len(good_artificials)))
            print("Percent of good artificials: %" + str((len(good_artificials) / len(artificial_time)) * 100))
        self.good_frac = len(good_artificials) / len(artificial_time)
        return fixed_augment.append(good_artificials)

    def implement_augment(self, censored_df):
        """
        creates the new column of new time for the censored samples. The func adds the time to all samples
        by taking the time we created to the last sample.
        :type org_df: censored saliva otu or censored stool otu with all samples
        :param censored_df: .censored saliva otu or censored stool otu with all samples
        :param artificial_data: new time for censored samples.
        :param tag: name of tag
        :return: new censored df with the new column
        """
        artificial_data_for_censored_sample = self.augment(self.beta)

        censored_df["new_" + self.tag] = artificial_data_for_censored_sample
        for subject in censored_df.groupby(censored_df[self.people_col]):
            aug_index = set(subject[1].index).intersection(artificial_data_for_censored_sample.index)
            subject[1]["new_" + self.tag] = artificial_data_for_censored_sample[aug_index].values[0]
            censored_df.update(subject[1])
        return censored_df


class Bar_thesis_Augment(Augment):
    def __init__(self, tag: str, censor_df: pd.DataFrame, uncensord_df: pd.DataFrame, beta, people_col, time_col):
        self.tag = tag
        censored_df = censor_df
        uncensored_df = uncensord_df
        self.censored_tag_for_loss = censored_df[tag]
        self.uncensored_time_to_tag = uncensored_df[tag]
        super().__init__(f"{tag}", censored_df, uncensored_df, beta, people_col=people_col, time_col=time_col,
                         only_last_sample_before_gvhd=False)

    def augment_function_1(self, c, beta=0.01, agumented_data=None):
        if agumented_data is not None:
            last_samples = self.last_samples_uncensord_only_microbiom.append(agumented_data, ignore_index=True)
        else:
            last_samples = self.last_samples_uncensord_only_microbiom
        Y = last_samples.sub(c, axis=1)
        Y = np.sqrt(np.square(Y).sum(axis=1))
        Y = Y * (-beta)
        di = np.exp(Y)
        return di

    def augment_function_2(self, c, beta=0.01, agumented_data=None):
        if agumented_data is not None:
            last_samples = self.last_samples_uncensord_only_microbiom.append(agumented_data, ignore_index=True)
        else:
            last_samples = self.last_samples_uncensord_only_microbiom
        Y = last_samples.sub(c, axis=1)
        Y = np.sqrt(np.square(Y).sum(axis=1))
        di = 1 / Y
        return di

    def augment_function_3(self, c, beta=0.01, agumented_data=None):
        if agumented_data is not None:
            last_samples = self.last_samples_uncensord_only_microbiom.append(agumented_data, ignore_index=True)
        else:
            last_samples = self.last_samples_uncensord_only_microbiom
        Y = last_samples.sub(c, axis=1)
        Y = np.sqrt(np.square(Y).sum(axis=1))
        di = 1 / (1 + Y ** 2)
        return di

    def augment(self, beta=0.01, func=augment_function_3) -> pd.Series:
        """
        calculate the GVHD event time for the censored samples.
        calculation follows: time_i = (sum for all uncensored samples on d_i,j * time_j) / (sum for all uncensored samples on d_i,j)
        while d_i,j is: e ^ ( -beta*(norm_l2(sample_i - sample_j))^2)
        while i is an index of censored sample and j is an index of the uncensored sample
        :param beta:
        :return: series with artificial times
        """
        artificial_time = pd.Series()

        for x_line in self.last_samples_censord_only_microbiom.iloc:
            di = func(self, x_line, beta)
            di = di.sort_values()
            # take the 30 most closest only
            di = di[:30]

            line = pd.Series({x_line.name: (di * self.last_uncensord_tag_before_event.loc[di.index]).sum() / di.sum()})

            artificial_time = artificial_time.append(line)

        augmented_data = self.augment_fix(artificial_time)
        artificial_time = pd.Series()

        for i in range(0):
            for x_line in self.last_samples_censord_only_microbiom.iloc:
                augmented_data_without_x_line = augmented_data[augmented_data.index != x_line.name]
                di = func(x_line, beta, augmented_data_without_x_line)
                line = pd.Series({x_line.name: (di * self.last_uncensord_tag_before_event.append(
                    augmented_data_without_x_line)).sum() / di.sum()})
                artificial_time = artificial_time.append(line)

            augmented_data = self.augment_fix(artificial_time)
        return augmented_data

    def add_tag_to_predict(self, censored_df, uncensored_df):
        """
        add a tag of the time passes from the sample time to the event in uncensored:
        and in censored: the time passes from the sample time to the augmented event and a column for the time passes
        from the sample to competing event.
        :param censor_df: data frame of censor
        :param uncensor_df: data frame of uncensored
        :param tag: name of tag
        :return: censor_df, uncensor_df
        """
        days = 1
        cols = list(censored_df.columns)
        cols.insert(len(censored_df.columns), "time_to_" + self.tag)
        empty = pd.DataFrame(columns=cols)
        # make dates dates

        censored_df[['Date', 'DateEnd']] = censored_df[['Date', 'DateEnd']].apply(pd.to_datetime)
        self.last_samples_censord[['Date', 'DateEnd']] = self.last_samples_censord[['Date', 'DateEnd']].apply(
            pd.to_datetime)
        for i, df in censored_df.groupby(self.people_col):
            df[['Date', 'DateEnd']] = df[['Date', 'DateEnd']].apply(pd.to_datetime)
            df = df.reindex(index=order_by_index(df.index, index_natsorted(df[self.time_col])))
            for row in range(len(df.index)):
                df["time_to_" + self.tag] = None

                df["time_to_" + self.tag][row] = (df.iloc[len(df.index) - 1]['Date'] - df.iloc[row]['Date']).days

                empty = empty.append(df.iloc[row])

            # add column tag to censored
        censored_df["time_to_" + self.tag] = empty["time_to_" + self.tag] + censored_df["new_" + self.tag] * days
        censored_df[self.tag + "_for_loss"] = censored_df[self.tag] * days
        # add column to uncensored
        uncensored_df["time_to_" + self.tag] = uncensored_df[self.tag] * days
        uncensored_df[self.tag + "_for_loss"] = uncensored_df[self.tag] * days

        return censored_df, uncensored_df


class FIESTA(Bar_thesis_Augment):
    """
    uniFormatIve fEatureS daTa Augmentation (FIESTA) defines the augmented TTE of the censored samples.
    The DA process contains 2 steps:
    1. Defining the augmented TTE as a weighted average of the uncensored samples based
    on the difference in M between samples (as described in our paper).
    There are 3 options for declaying functions Exponential (function_1), Hyperbolic (function_2) and Cauchy (function_3), which
    is the default.
    2. Computing the augmented TTE using Maximum Likelihood Estimation (MLE) on a model
    where a constant censoring rate of lamda is assumed and the event is normally distributed around the previously computed in step 1.

    """

    def __init__(self, tag: str, censor_df: pd.DataFrame, uncensord_df: pd.DataFrame, beta, lamda, people_col,
                 time_col):
        """
        Initialize FIESTA with all its relevant parameters.
        :param tag: name of tag
        :param censor_df: A dataframe with all the censored samples, must include:
                                    1. A column names "Date" of the date of the sample, the date should be in an American format
                                        of month/day/year
                                    2. A column names "DateEnd" of the date of a competing event for censored,
                                        the date should be in an American format of month/day/year
                                    3. A people column names similar to the people_col parameter, contains the identity of a patient
                                    4. A time column names similar to the time_col parameter, contains the order of samples (for sequntial data)
                                    5. A tag column names tag with the comperting event times
        :param uncensord_df: A dataframe with all the uncensored samples, must include:
                                    1. A column names "Date" of the date of the sample, the date should be in an American format
                                        of month/day/year
                                    2. A column names "DateEnd" of the date of an event for uncensored,
                                        the date should be in an American format of month/day/year
                                    3. A people column names similar to the people_col parameter, contains the identity of a patient
                                    4. A time column names similar to the time_col parameter, contains the order of samples for sequntial data
                                    5. A tag column names tag with the TTEs
        :param beta: Hyperparameter in the decaying augmented function (float)
        :param lamda: An assumed constant censoring rate (float)
        :param people_col: Name of patients id column (str)
        :param time_col: Name of times order column (str)
        """
        super().__init__(tag, censor_df, uncensord_df, beta, people_col, time_col)
        self.TC = super().augment(lamda)

    def MLE_func_prop_dev(self, t):
        return t - self.tc + np.e ** (-self.lamda * t) * (self.sigma ** 2 - t + self.tc)

    def MLE_func(self, t):
        return -(((t - self.tc) / self.sigma) ** 2) + (
                (self.lamda * np.e ** (-self.lamda * t)) / (1 - (np.e ** (-self.lamda * t))))

    def augment(self, lamda):
        self.lamda = lamda
        t = pd.Series()
        for i in self.TC.index:
            self.tc = self.TC[i]
            t = t.append(pd.Series({i: root_scalar(self.MLE_func, x0=self.tc, x1=1).root}))
        return self.augment_fix(t.astype(dtype="float"))

    def implement_augment(self, censored_df, lamda=0.01):
        """
        creates the new column of new time for the censored samples. The func adds the time to all samples
        by taking the time we created to the last sample.
        :type org_df: censored saliva otu or censored stool otu with all samples
        :param censored_df: .censored saliva otu or censored stool otu with all samples
        :param artificial_data: new time for censored samples.
        :param tag: name of tag
        :return: new censored df with the new column
        """
        self.bar_good_frac = self.good_frac
        self.sigma = self.TC.values.mean() * 2
        artificial_data_for_censored_sample = self.augment(lamda)

        censored_df["new_" + self.tag] = artificial_data_for_censored_sample
        for subject in censored_df.groupby(censored_df[self.people_col]):
            aug_index = set(subject[1].index).intersection(artificial_data_for_censored_sample.index)
            subject[1]["new_" + self.tag] = artificial_data_for_censored_sample[aug_index].values[0]

            censored_df.update(subject[1])
        return censored_df
