import logging
import pathlib
import random
from dataclasses import dataclass
from typing import Sequence, List, Iterator, Optional, Iterable, Tuple

import numpy as np
import pandas as pd
from scipy.special import entr
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from contur.oracle.hyperparams import SIGMA_1, SIGMA_2, TEST_SIZE, NUMBER_OF_TREES, CLTYPE

LABEL_0_68 = 0
LABEL_68_95 = 1
LABEL_95_100 = 2

TRAINING_LABEL = 'CL-label'
ENTROPY = 'entropy'

random.seed(42)


@dataclass
class ClassificationError:
    # TP, FP, TN, FN stand for True Positive, False Positive, True Negative, False Negative
    tp_count: int
    fp_count: int
    fn_count: int
    tn_count: int


@dataclass
class TrainingResult:
    #
    # Source attributes
    #

    classifier: RandomForestClassifier
    # the probability distribution of the classifier for the whole grid
    prediction_probabilities: np.ndarray
    training_points_count: int
    testing_points_count: int

    classif_err_68_testing: ClassificationError
    classif_err_95_testing: ClassificationError
    classif_err_68_training: ClassificationError
    classif_err_95_training: ClassificationError

    #
    # Computed attributes
    #

    # PPV is the positive predictive value
    ppv_testing_68: float
    ppv_testing_95: float
    ppv_training_68: float
    ppv_training_95: float
    # TPR is the true positive rate
    tpr_testing_68: float
    tpr_testing_95: float
    tpr_training_68: float
    tpr_training_95: float

    mean_entropy: float
    mean_entropy_testing: float
    mean_entropy_training: float

    reached_goal: bool
    # the whole entropy grid
    prediction_entropies: np.ndarray


@dataclass
class DataSet:
    all_points: pd.DataFrame
    training_points: pd.DataFrame
    testing_points: pd.DataFrame


class Oracle:
    def __init__(self,
                 grid,
                 # model_name: str,
                 iteration_points: int,
                 n_trees: int,
                 params: Iterable[str],
                 precision_goal: float,
                 recall_goal: float,
                 entropy_goal: float,
                 test_size: float,
                 # class_weight,
                 cl_label: str = 'CLSMBG',
                 results_backup: List[TrainingResult] = None
                 ) -> None:

        self.iteration_points = iteration_points
        self.grid = grid
        self.n_trees = n_trees
        self.params = params
        self.cl_label = cl_label
        self.precision_goal = precision_goal
        self.recall_goal = recall_goal
        self.entropy_goal = entropy_goal
        self.results_stack: List[TrainingResult] = results_backup or []
        self.dataset: Optional[DataSet] = None
        self.test_size = test_size
        self.status = ""
        # self.class_weight = class_weight
        # self.model_name = model_name

    @property
    def latest_classifier(self):
        return self.results_stack[-1].classifier

    @staticmethod
    def get_false_true_positive_negative_counts(
            predicted_excluded, predicted_not_excluded,
            labeled_excluded, labeled_not_excluded):
        true_positives = np.logical_and(predicted_excluded, labeled_excluded)
        false_positives = np.logical_and(predicted_excluded, labeled_not_excluded)
        true_negatives = np.logical_and(predicted_not_excluded, labeled_not_excluded)
        false_negatives = np.logical_and(predicted_not_excluded, labeled_excluded)
        return ClassificationError(
            tp_count=np.sum(true_positives),
            fp_count=np.sum(false_positives),
            fn_count=np.sum(false_negatives),
            tn_count=np.sum(true_negatives)
        )

    @classmethod
    def get_classification_error_count(cls, predictions, labels):
        # 95 % confidence interval
        predicted_excluded_95 = predictions == 2
        predicted_not_excluded_95 = predictions != 2
        labeled_excluded_95 = labels == 2
        labeled_not_excluded_95 = labels != 2
        classif_err_95 = cls.get_false_true_positive_negative_counts(
            predicted_excluded_95,
            predicted_not_excluded_95,
            labeled_excluded_95,
            labeled_not_excluded_95)

        # 68 % confidence interval
        predicted_excluded_68 = predictions >= 1
        predicted_not_excluded_68 = predictions == 0
        labeled_excluded_68 = labels >= 1
        labeled_not_excluded_68 = labels == 0
        classif_err_68 = cls.get_false_true_positive_negative_counts(
            predicted_excluded_68,
            predicted_not_excluded_68,
            labeled_excluded_68,
            labeled_not_excluded_68)

        return classif_err_68, classif_err_95

    @classmethod
    def get_performance_metric_indicators(cls, classif_error: ClassificationError) -> Tuple[float, float]:
        """
        This function takes in the true positive, false positive, true negative and false negative counts,
        and returns the positive predictive value and true positive rate.
        """
        ppv = classif_error.tp_count / (classif_error.tp_count + classif_error.fp_count)
        tpr = classif_error.tp_count / (classif_error.tp_count + classif_error.fn_count)
        return ppv, tpr

    def train(self, training_data: pd.DataFrame, testing_data: pd.DataFrame) -> TrainingResult:
        classifier = RandomForestClassifier(n_estimators=self.n_trees, class_weight='balanced')
        classifier.fit(training_data[self.params].to_numpy(), training_data[TRAINING_LABEL].to_numpy())

        test_predictions = classifier.predict(testing_data[self.params].to_numpy())
        training_predictions = classifier.predict(training_data[self.params].to_numpy())

        print(self.grid)
        print(testing_data[self.params])
        test_prediction_probabilities = classifier.predict_proba(testing_data[self.params].to_numpy())
        train_prediction_probabilities = classifier.predict_proba(training_data[self.params].to_numpy())
        grid_prediction_probabilities = classifier.predict_proba(self.grid)

        entropy_array = entr(grid_prediction_probabilities).sum(axis=1) / np.log(3)
        entropy_array_test = entr(test_prediction_probabilities).sum(axis=1) / np.log(3)
        entropy_array_train = entr(train_prediction_probabilities).sum(axis=1) / np.log(3)

        mean_entropy = entropy_array.mean()
        mean_entropy_test = entropy_array_test.mean()
        mean_entropy_train = entropy_array_train.mean()

        classif_err_68_testing, classif_err_95_testing = self.get_classification_error_count(
            test_predictions, testing_data[TRAINING_LABEL])
        classif_err_68_training, classif_err_95_training = self.get_classification_error_count(
            training_predictions, training_data[TRAINING_LABEL])

        ppv_testing_68, tpr_testing_68 = self.get_performance_metric_indicators(classif_err_68_testing)
        ppv_testing_95, tpr_testing_95 = self.get_performance_metric_indicators(classif_err_95_testing)
        ppv_training_68, tpr_training_68 = self.get_performance_metric_indicators(classif_err_68_training)
        ppv_training_95, tpr_training_95 = self.get_performance_metric_indicators(classif_err_95_training)

        # TODO this can be customized by the user i.e. does the recall/precision apply to the 95 or 68 confidence
        #  interval? Do we check the entropy value from the entire grid or just the testing data?
        reached_goal = (
            (mean_entropy < self.entropy_goal) and
            ppv_testing_95 > self.precision_goal and
            tpr_testing_95 > self.recall_goal
        )

        return TrainingResult(
            classifier=classifier,
            prediction_probabilities=grid_prediction_probabilities,
            testing_points_count=len(testing_data[self.params]),
            training_points_count=len(training_data[self.params]),
            classif_err_68_training=classif_err_68_training,
            classif_err_95_training=classif_err_95_training,
            classif_err_68_testing=classif_err_68_testing,
            classif_err_95_testing=classif_err_95_testing,

            ppv_testing_68=ppv_testing_68,
            ppv_testing_95=ppv_testing_95,
            tpr_testing_68=tpr_testing_68,
            tpr_testing_95=tpr_testing_95,
            ppv_training_68=ppv_training_68,
            ppv_training_95=ppv_training_95,
            tpr_training_68=tpr_training_68,
            tpr_training_95=tpr_training_95,

            reached_goal=reached_goal,
            mean_entropy=mean_entropy,
            mean_entropy_training=mean_entropy_train,
            mean_entropy_testing=mean_entropy_test,
            prediction_entropies=entropy_array
        )

    def get_next_param_points(self, dataset: DataSet, training_result: TrainingResult) -> pd.DataFrame:
        grid_df = self.get_entropy_grid(training_result)
        grid_df = pd.merge(grid_df.round(5), dataset.all_points[self.params].round(5), how="outer", indicator=True)
        grid_df = grid_df[grid_df['_merge'] == 'left_only'].drop(['_merge'], axis=1)
        grid_df = grid_df.sample(frac=1).sort_values(ENTROPY, ascending=False)
        grid_df.to_csv("entropy-sorted-predictions.csv")
        return grid_df.head(self.iteration_points)[self.params]

    @staticmethod
    def label_dataframe(df: pd.DataFrame):
        df[TRAINING_LABEL] = 0
        df.loc[df[CLTYPE] <= SIGMA_1, TRAINING_LABEL] = LABEL_0_68
        df.loc[(df[CLTYPE] > SIGMA_1) & (df[CLTYPE] <= SIGMA_2), TRAINING_LABEL] = LABEL_68_95
        df.loc[(df[CLTYPE] > SIGMA_2), TRAINING_LABEL] = LABEL_95_100
        return df

    @classmethod
    def convert_contur_to_oracle_dataset(cls, contur_data: pd.DataFrame, test_size: float) -> DataSet:
        contur_data = cls.label_dataframe(contur_data)
        contur_data = contur_data.drop_duplicates()
        train_data, test_data = train_test_split(contur_data, test_size=test_size)
        return DataSet(
            all_points=contur_data,
            testing_points=test_data,
            training_points=train_data
        )

    def get_random_sample(self, n_points: int = None) -> pd.DataFrame:
        """
        randomly samples n_points from the grid generated from the user range and goal
        resolution.
        """
        sample = np.array(random.sample([p for p in self.grid], (n_points or self.iteration_points)))
        sample_df = pd.DataFrame(sample)
        sample_df.columns = self.params
        return sample_df

    def get_entropy_grid(self, training_result: TrainingResult):
        grid_df = pd.DataFrame(self.grid)
        grid_df.columns = self.params
        grid_df[ENTROPY] = training_result.prediction_entropies
        return grid_df

    def main(self) -> Iterator[pd.DataFrame]:
        """
        Generator that takes in the latest dataset, trains a classifier, adds it to the result stack, and gives the
        new points to add to the dataset
        """
        if self.dataset is None:
            yield self.get_random_sample()
        while True:
            results = self.train(self.dataset.training_points, self.dataset.testing_points)
            self.results_stack.append(results)
            result_text = (f"it {len(self.results_stack)}: "
                           f"Recall: [{results.tpr_testing_95:.2f}/{self.recall_goal:.2f}], "
                           f"Precision: [{results.ppv_testing_95:.2f}/{self.precision_goal:.2f}], "
                           f"Entropy: [{results.mean_entropy:.2f}/{self.entropy_goal:.2f}], "
                           f"total points: {len(self.dataset.all_points)}, "
                           f"testing: {len(self.dataset.testing_points)}")
            self.status = result_text
            print(result_text)
            if not results.reached_goal:
                next_points = self.get_next_param_points(self.dataset, results)
                if len(next_points) == 0:
                    print('Did not reach results goal. No more points to sample')
                    return
                yield next_points
            else:
                self.status = result_text + "\n Reached results goal."
                print('Reached results goal.')
                return

    def add_new_points(self, new_points: pd.DataFrame):
        new_dataset_fragment = self.convert_contur_to_oracle_dataset(new_points, self.test_size)
        if self.dataset is None:
            self.dataset = new_dataset_fragment
        else:
            self.dataset = DataSet(
                all_points=self.dataset.all_points.append(new_dataset_fragment.all_points),
                testing_points=self.dataset.testing_points.append(new_dataset_fragment.testing_points),
                training_points=self.dataset.training_points.append(new_dataset_fragment.training_points)
            )


def get_grid_from_axes(axes):
    return np.array(np.meshgrid(*axes)).T.reshape(-1, len(axes))
