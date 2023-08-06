import functools
import multiprocessing
import pathlib
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
from contur.oracle.benchmarking import obtain_results, obtain_interpolation_results
from contur.oracle.oracle import Oracle, TRAINING_LABEL
import matplotlib.ticker as mtick
import numpy as np
from contur.oracle.hyperparams import SIGMA_1, SIGMA_2, TEST_SIZE, NUMBER_OF_TREES, CLTYPE


def generate_data(identifier: int, params: List[str], data: pd.DataFrame, model_name: str):
    iteration_points = int(np.ceil(data.shape[0] / 30))
    oracle = Oracle(
        grid=data[params].to_numpy(),
        iteration_points=iteration_points,
        n_trees=100,
        params=params,
        accuracy_goal=1,
        entropy_goal=0,
        test_size=1 / 4,
    )
    try:
        df = obtain_results(oracle, data)
    except BaseException as e:
        print(f'{identifier} {model_name} {e}')
    else:
        path = pathlib.Path(f'../../oracle-benchmarking/{model_name}/data/')
        path.mkdir(parents=True, exist_ok=True)
        df.to_csv(f'../../oracle-benchmarking/{model_name}/data/data-{identifier}.csv')


def generate_data_multiprocess(model_name, params):
    data = pd.read_csv(f'../../oracle-benchmarking/{model_name}/dataset.csv')
    pool = multiprocessing.Pool()
    identifiers = list(range(30))
    generate_data_worker = functools.partial(generate_data, params=params, data=data, model_name=model_name)
    pool.map(generate_data_worker, identifiers)


def combine_data(model_name: str, interpolation: bool = False):
    folder = f'data-interpolation' if interpolation else 'data'
    save_to_file = 'aggr-interpolation' if interpolation else 'aggr'
    column_name = 'fraction' if interpolation else 'fraction_total_points'
    files = [f
             for f in pathlib.Path(f'../../oracle-benchmarking/{model_name}/{folder}/').glob('**/*.csv')
             if f.is_file()]
    dfs = [pd.read_csv(file) for file in files]
    df = pd.concat(dfs)
    df = df.drop(columns=['Unnamed: 0'])
    # pd.set_option('display.max_columns', None)
    df_aggr = df.groupby(column_name, as_index=False).agg(['mean', 'std'])
    df_aggr.to_csv(f'../../oracle-benchmarking/{model_name}/{save_to_file}.csv')
    df_aggr.to_pickle(f'../../oracle-benchmarking/{model_name}/{save_to_file}.pkl')


def subsample_performance(identifier: int, params: List[str], data: pd.DataFrame, model_name: str):
    fractions = np.linspace(0, 1, 31)[1:]

    df = pd.DataFrame(np.zeros((len(fractions), 5)))
    df.columns = [
        'fraction',
        'ppv_68',
        'ppv_95',
        'tpr_68',
        'tpr_95',
    ]
    for idx, fraction in enumerate(fractions):
        print(f'{model_name} {identifier} fraction: {fraction:.2f}')
        interpolated_results = obtain_interpolation_results(data, fraction, params)
        error_68, error_95 = Oracle.get_classification_error_count(
            interpolated_results[TRAINING_LABEL], data[TRAINING_LABEL])
        ppv_95, tpr_95 = Oracle.get_performance_metric_indicators(error_95)
        ppv_68, tpr_68 = Oracle.get_performance_metric_indicators(error_68)

        df.loc[idx, 'fraction'] = fraction
        df.loc[idx, 'ppv_68'] = ppv_68
        df.loc[idx, 'ppv_95'] = ppv_95
        df.loc[idx, 'tpr_68'] = tpr_68
        df.loc[idx, 'tpr_95'] = tpr_95

    path = pathlib.Path(f'../../oracle-benchmarking/{model_name}/data-interpolation/')
    path.mkdir(parents=True, exist_ok=True)
    df.to_csv(f'../../oracle-benchmarking/{model_name}/data-interpolation/data-{identifier}.csv')


def subsample_performance_multiprocess(model_name, params):
    data = pd.read_csv(f'../../oracle-benchmarking/{model_name}/dataset.csv')
    iterations = list(range(30))

    Oracle.label_dataframe(data)

    pool = multiprocessing.Pool()
    subsample_performance_worker = functools.partial(subsample_performance, params=params, data=data, model_name=model_name)
    pool.map(subsample_performance_worker, iterations)

# def add_ppv_and_tpr():
#     """
#     The following function adds the PPV and TPR values for each confidence level and testing/training,
#     for each run experiment CSV file, from the ./data/ directory.
#     """
#     files = [f for f in pathlib.Path('../../oracle-benchmarking/dm/data/').glob('**/*.csv') if f.is_file()]
#     modes = ['testing', 'training']
#     confidence_levels = [68, 95]
#     classif_err_combinations = list(itertools.product(modes, confidence_levels))
#     for file in files:
#         df = pd.read_csv(file)
#         for mode, cl in classif_err_combinations:
#             df[f"ppv_{mode}_{cl}"] = df[f"tp_{mode}_{cl}"] / (df[f"tp_{mode}_{cl}"] + df[f"fp_{mode}_{cl}"])
#             df[f"tpr_{mode}_{cl}"] = df[f"tp_{mode}_{cl}"] / (df[f"tp_{mode}_{cl}"] + df[f"fn_{mode}_{cl}"])
#         print(df.columns)
#         df.to_csv(file, index=False)


def round_dataset_to_significant_figures(model_name: str, n_significant_figures: int):
    """
    This function rounds the param columns of the dataset to the specified number of significant figures,
    and saves it back in the same location.
    """
    data = pd.read_csv(f'../../oracle-benchmarking/{model_name}/dataset.csv')
    params = list(set(data.columns) - {CLTYPE})
    for param in params:
        data[param] = data[param].round(n_significant_figures)

    data.to_csv(f'../../oracle-benchmarking/{model_name}/dataset.csv', index=False)


def plot_results(model_name: str, pretty_model_name: str):
    """
    The following function reads the values of the metrics from the csv file and plots them.
    """
    df = pd.read_pickle(f'../../oracle-benchmarking/{model_name}/aggr.pkl')
    plots = {
        f'Uncertainty ({pretty_model_name})': [
            ('entropy_testing', 'Entropy (testing dataset)'),
            # ('entropy_training', 'Training'),
            ('entropy_full_grid', 'Entropy (full dataset)')
        ],
        f'Accuracy ({pretty_model_name})': [
            # ('ppv_testing_68', 'Testing, 68% CL'),
            # ('ppv_testing_95', 'Testing'),
            # ('ppv_training_68', 'Training, 68% CL'),
            # ('ppv_training_95', 'Training, 95% CL'),
            # ('ppv_full_grid_68', 'Full grid, 68% CL'),
            ('ppv_full_grid_95', 'PPV (full dataset)'),
            ('tpr_full_grid_95', 'TPR (full dataset)'),
        ],
        # 'Sensitivity (DM model)': [
        #     # ('tpr_testing_68', 'Testing, 68% CL'),
        #     ('tpr_testing_95', 'Testing'),
        #     # ('tpr_training_68', 'Training, 68% CL'),
        #     # ('tpr_training_95', 'Training, 95% CL'),
        #     # ('tpr_full_grid_68', 'Full grid, 68% CL'),
        #     ('tpr_full_grid_95', 'Full grid'),
        # ]

    }

    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = 'Charter'
    for plot_name, plot_metrics in plots.items():
        plt.figure(dpi=200)
        for (metric, metric_label) in plot_metrics:
            df_metric = df[metric]
            plt.errorbar(df_metric.index, df_metric['mean'], df_metric['std'], label=metric_label, capsize=2,
                         elinewidth=1, markeredgewidth=1, marker='o', markersize=1.5, linestyle='-', linewidth=0)
        plt.title(plot_name, fontsize=14)
        plt.xlabel('% of full grid points')
        if plot_name == f'Accuracy ({pretty_model_name})':
            plt.ylim([0.9, 1])
        else:
            plt.ylim([0, 1])
        plt.legend(frameon=False)
        plt.savefig(f'../../oracle-benchmarking/{model_name}/plots/{plot_name}.svg')


def plot_results_against_interpolation(model_name: str, pretty_model_name: str):

    df_ai = pd.read_pickle(f'../../oracle-benchmarking/{model_name}/aggr.pkl')
    df_int = pd.read_pickle(f'../../oracle-benchmarking/{model_name}/aggr-interpolation.pkl')

    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = 'Charter'
    vars = ['tpr', 'ppv']
    cls = [68, 95]
    for var in vars:
        plt.figure(dpi=200)
        for cl in cls:
            plt.errorbar(df_ai.index, df_ai[f'{var}_full_grid_{cl}']['mean'], df_ai[f'{var}_full_grid_95']['std'],
                         label=f'Contur Oracle {cl}',
                         capsize=2, elinewidth=1, markeredgewidth=1, marker='o', markersize=1.5, linestyle='-',
                         linewidth=0.35)
            plt.errorbar(df_int.index * 100, df_int[f'{var}_{cl}']['mean'], df_int[f'{var}_95']['std'],
                         label=f'Interpolation {cl}',
                         capsize=2, elinewidth=1, markeredgewidth=1, marker='o', markersize=1.5, linestyle='-',
                         linewidth=0.35)
        plt.xlabel('% of full grid points')
        # The following line makes the x axis formatter to be a percentage
        plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter())
        plt.title(f'{var} ({pretty_model_name})', fontsize=14)
        plt.legend(frameon=False)
        plt.show()


if __name__ == '__main__':
    models = [
        {
            'model_name': 'dm',
            'params': ['gYXm', 'gYq', 'mXm', 'mY1'],
            'pretty_model_name': 'DM model'
        },
        {
            'model_name': 'vlq',
            'params': ['mtp', 'xitpw', 'zetaBbL', 'zetaXtL', 'zetaYbL'],
            'pretty_model_name': 'VLQ model'
        },
        {
            'model_name': '2hdma',
            'params': ['mXd', 'mh4', 'sinp', 'tanbeta'],
            'pretty_model_name': '2HDMA model'
        }
    ]
    for model in models:
        # generate_data_multiprocess(model_name=model['model_name'], params=model['params'])
        # combine_data(model['model_name'], interpolation=True)
        # subsample_performance_multiprocess(model['model_name'], model['params'])

        # plot_results(model['model_name'],
        #              model['pretty_model_name'])
        plot_results_against_interpolation(model['model_name'], model['pretty_model_name'])
    # round_dataset_to_significant_figures(model['model_name'], n_significant_figures=3)


def create_language_model():
    """
    The following function creates a tensorflow ML model for language recognition.
    """
