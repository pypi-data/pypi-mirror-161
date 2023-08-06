from typing import List

import numpy as np
import pandas as pd
import scipy.interpolate
from contur.oracle.oracle import Oracle, ClassificationError, TRAINING_LABEL
from itertools import product
from contur.oracle.hyperparams import SIGMA_1, SIGMA_2, TEST_SIZE, NUMBER_OF_TREES, CLTYPE

TRAINING_LABEL_SUBSAMPLE = 'CL-label-subsample'


def obtain_results(oracle: Oracle, full_grid: pd.DataFrame) -> pd.DataFrame:
    print('Starting benchmarking...')
    fraction_total_points = []
    entropy_full_grid = []
    entropy_testing = []
    entropy_training = []

    classif_err_results = {
        'tp_testing_68': [],
        'fp_testing_68': [],
        'fn_testing_68': [],
        'tn_testing_68': [],

        'tp_testing_95': [],
        'fp_testing_95': [],
        'fn_testing_95': [],
        'tn_testing_95': [],

        'tp_training_68': [],
        'fp_training_68': [],
        'fn_training_68': [],
        'tn_training_68': [],

        'tp_training_95': [],
        'fp_training_95': [],
        'fn_training_95': [],
        'tn_training_95': [],

        'tp_full_grid_68': [],
        'fp_full_grid_68': [],
        'fn_full_grid_68': [],
        'tn_full_grid_68': [],

        'tp_full_grid_95': [],
        'fp_full_grid_95': [],
        'fn_full_grid_95': [],
        'tn_full_grid_95': [],
    }
    types = ['tp', 'fp', 'fn', 'tn']
    modes = ['testing', 'training', 'full_grid']
    confidence_levels = [68, 95]
    classif_err_combinations = list(product(types, modes, confidence_levels))
    oracle.label_dataframe(full_grid)

    for next_param_points in oracle.main():
        if len(oracle.results_stack) > 0:
            result = oracle.results_stack[-1]

            used_points = result.training_points_count + result.testing_points_count
            fraction_total_points.append(used_points / len(oracle.grid) * 100)

            prediction = result.classifier.predict(full_grid[oracle.params])
            classif_err_68, classif_err_95 = oracle.get_classification_error_count(
                prediction, full_grid[TRAINING_LABEL])
            classif_err_full_grid_results = {
                '68': classif_err_68,
                '95': classif_err_95
            }
            for err_type, mode, cl in classif_err_combinations:
                if mode == 'full_grid':
                    classif_err_result = classif_err_full_grid_results[str(cl)]
                else:
                    classif_err_result: ClassificationError = getattr(result, f"classif_err_{cl}_{mode}")
                classif_err_results[f'{err_type}_{mode}_{cl}'].append(getattr(classif_err_result, f"{err_type}_count"))

            entropy_full_grid.append(result.mean_entropy)
            entropy_testing.append(result.mean_entropy_testing)
            entropy_training.append(result.mean_entropy_training)

        new_points = pd.merge(full_grid, next_param_points)
        oracle.add_new_points(new_points)

    fraction_total_points = np.array(fraction_total_points)
    entropy_full_grid = np.array(entropy_full_grid)
    entropy_testing = np.array(entropy_testing)
    entropy_training = np.array(entropy_training)

    for key in classif_err_results.keys():
        classif_err_results[key] = np.array(classif_err_results[key])

    df = pd.DataFrame({
        'fraction_total_points': fraction_total_points,
        'entropy_testing': entropy_testing,
        'entropy_training': entropy_training,
        'entropy_full_grid': entropy_full_grid,
        **classif_err_results
    })

    classif_err_combinations = list(product(modes, confidence_levels))
    for mode, cl in classif_err_combinations:
        df[f"ppv_{mode}_{cl}"] = df[f"tp_{mode}_{cl}"] / (df[f"tp_{mode}_{cl}"] + df[f"fp_{mode}_{cl}"])
        df[f"tpr_{mode}_{cl}"] = df[f"tp_{mode}_{cl}"] / (df[f"tp_{mode}_{cl}"] + df[f"fn_{mode}_{cl}"])

    return df


def obtain_interpolation_results(full_grid: pd.DataFrame, fraction: float, params: List[str]):
    """
    This function obtains a random subsample of the full grid of size fraction * len(full_grid),
    calculates an interpolation of the chosen CL type values from the subsample (after normalization) and
    and obtains the interpolated chosen CL type value for the entire grid.
    """
    sample = full_grid.sample(frac=fraction)
    params_normalized = [f"{param}_normalized" for param in params]

    def normalize_df(df):
        df[params_normalized] = (df[params] - df[params].min()) / (df[params].max() - df[params].min())
    interpolated_results = full_grid.copy()
    normalize_df(interpolated_results)
    normalize_df(sample)
    interpolated_cl = scipy.interpolate.griddata(
        sample[params_normalized], sample[CLTYPE],
        interpolated_results[params_normalized])
    interpolated_results[CLTYPE] = interpolated_cl
    Oracle.label_dataframe(interpolated_results)
    return interpolated_results

# def obtain_axis_subsample(axis: np.ndarray, fraction: float) -> np.ndarray:
#     num_els = int(np.ceil(len(axis) * fraction))
#     ideal_els = np.linspace(np.min(axis), np.max(axis), num_els)
#     real_els = np.zeros(num_els)
#     for i in range(num_els):
#         real_els[i] = get_closest_value(axis, ideal_els[i])
#     return real_els
#
#
# def get_closest_value(array: np.ndarray, value: float):
#     return array[np.argmin(np.abs(array - value))]
#
#
# def obtain_grid_subsample(grid: pd.DataFrame, params, fraction: float) -> pd.DataFrame:
#     reduced_axes = {
#         param: obtain_axis_subsample(np.array(list(set(grid[param].values))), fraction)
#         for param in params
#     }
#     print(reduced_axes)
#
#     def grid_subsample_transform(row):
#         condition_list = [(param, get_closest_value(reduced_axes[param], row[param])) for param in params]
#         f = '{0[0]} == {0[1]}'.format
#         querystring = " & ".join(f(t) for t in condition_list)
#         row[TRAINING_LABEL_SUBSAMPLE] = grid.query(querystring)[TRAINING_LABEL].values[0]
#         return row
#
#     return grid.apply(grid_subsample_transform, axis=1)
#
#


# def obtain_subsample_performance(grid: pd.DataFrame, params, fraction: float):
#     Oracle.label_dataframe(grid)
#     interpolated_results = obtain_interpolation_results(grid, fraction, params)
#     error_68, error_95 = Oracle.get_classification_error_count(interpolated_results[TRAINING_LABEL], grid[TRAINING_LABEL])
#     return [Oracle.get_performance_metric_indicators(i) for i in [error_68, error_95]]
