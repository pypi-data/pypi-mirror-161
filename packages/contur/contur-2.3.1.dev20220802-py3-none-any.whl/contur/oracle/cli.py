import logging
import pathlib
import os
import pickle
import shutil
import textwrap
from dataclasses import dataclass, asdict
import random
from typing import Dict, List, TypedDict, Optional, Tuple

import numpy as np
import pandas as pd
import contur.config.config as cfg
from contur.oracle.oracle import Oracle
from contur.oracle.hyperparams import SIGMA_1, SIGMA_2, TEST_SIZE, NUMBER_OF_TREES, CLTYPE
from sklearn.ensemble import RandomForestClassifier

import yaml

oracle_source_code = os.path.dirname(os.path.realpath(__file__))
default_config = pathlib.Path(oracle_source_code) / 'default_config.yaml'


cfg.setup_logger("{0}/{1}.log".format(os.getcwd(), 'oracle'), level="INFO")
logger=cfg.contur_log


class ConfigParam(TypedDict):
    """
    ConfigParam is a TypedDict that contains all the options that can be provided for how the axis of each parameter
    should be created when building the grid for prediction.
    """
    axis: Optional[List[float]]
    range: Optional[Tuple[float, float]]
    resolution: Optional[float]


@dataclass
class Config:
    """
    Configuration class for the oracle, that holds the parameters specified in the config.yaml file within the
    project folder.
    """
    # user-provided
    initial_points: int
    iteration_points: int
    params: Dict[str, ConfigParam]
    precision_goal: float
    recall_goal: float
    entropy_goal: float

    # system-generated
    processed_scans: List[str]
    pending_scans: List[str]


class fs:
    """
    This class contains helper functions for locating the relevant files and directories for the command-line
    interface of the Oracle.
    """
    @staticmethod
    def config_file(working_dir: pathlib.Path): return pathlib.Path(working_dir) / 'oracle.config.yaml'

    @staticmethod
    def dataset_file(working_dir: pathlib.Path): return pathlib.Path(working_dir) / 'dataset.csv'

    @staticmethod
    def param_file(working_dir: pathlib.Path): return pathlib.Path(working_dir) / 'param_file.dat'

    @staticmethod
    def param_files_dir(working_dir: pathlib.Path): return pathlib.Path(working_dir) / 'param_files'

    @classmethod
    def new_param_file(cls, working_dir: pathlib.Path, iteration: int):
        return cls.param_files_dir(pathlib.Path(working_dir)) / f'param_file_{iteration}.dat'

    @staticmethod
    def input_points_dir(working_dir: pathlib.Path): return pathlib.Path(working_dir) / 'input_points'

    @classmethod
    def input_points_file(cls, working_dir: pathlib.Path, iteration: int, csv=False):
        return cls.input_points_dir(pathlib.Path(working_dir)) / f'input-points-{iteration}.{"csv" if csv else "pkl"}'

    @staticmethod
    def output_cls_dir(working_dir: pathlib.Path): return pathlib.Path(working_dir) / 'output_cls'

    @classmethod
    def output_cls_file(cls, working_dir: pathlib.Path, iteration: int):
        return cls.output_cls_dir(working_dir) / f'run-output-{iteration}.csv'

    @staticmethod
    def output_contur_dir(working_dir: pathlib.Path): return pathlib.Path(working_dir) / 'contur_batch_output'

    @staticmethod
    def classifiers_dir(working_dir: pathlib.Path): return pathlib.Path(working_dir) / 'classifiers'

    @classmethod
    def classifier_file(cls, working_dir: pathlib.Path, iteration: int):
        return cls.classifiers_dir(working_dir) / f'classifier-{iteration}.pkl'

    @staticmethod
    def results_file(working_dir: pathlib.Path): return working_dir / 'results.csv'


def initialize_directory(working_dir):
    """
    Initializes the working directory, creating all the required folders, and copying
    the config file from the source code.
    """
    logger.info(f'Initializing Contur Oracle directory on {working_dir}...')

    logger.info('Creating config file...')
    shutil.copy(default_config, fs.config_file(working_dir))

    logger.info('Creating I/O directories...')

    fs.param_files_dir(working_dir).mkdir(exist_ok=True)
    fs.input_points_dir(working_dir).mkdir(exist_ok=True)
    fs.output_cls_dir(working_dir).mkdir(exist_ok=True)
    fs.output_contur_dir(working_dir).mkdir(exist_ok=True)
    fs.classifiers_dir(working_dir).mkdir(exist_ok=True)

    logger.info(f"Directory initialized on {working_dir}."
                "Don't forget to edit the oracle.config.yaml file and your param_file.dat files accordingly: in "
                "oracle.config.yaml you must specify the parameters that will be randomly sampled, while in "
                "param_file.dat you need to set these params to MODE=DF and use DATAFRAME_LOCATION as a "
                "placeholder for the location. This script will replace this placeholder with the location of the "
                "dataframe for each set of points.")


def verify_directory(working_dir: pathlib.Path):
    """
    Verifies that the working directory is initialized and properly configured.
    """
    if not (config_file := fs.config_file(working_dir)).exists() \
            or not (param_file := fs.param_file(working_dir)).exists():
        raise RuntimeError(f'Directory {working_dir} is not initialized. Please run initialize_directory() first.')

    parm_file_text = param_file.read_text()
    if 'DATAFRAME_LOCATION' not in parm_file_text:
        raise RuntimeError(f'The param file on directory {working_dir} must contain the desired params in DF mode, '
                           f'where the pickle file name must be "DATAFRAME_LOCATION" so that this script can '
                           f'generate a param file for each iteration with the correct dataframe path.')

    config = Config(**yaml.load(config_file.read_text(), Loader=yaml.FullLoader))
    if config.initial_points == 0 or config.iteration_points == 0:
        raise RuntimeError(f'The config file on directory {working_dir} must contain the desired initial and '
                           f'iteration points.')


def load_config(working_dir: pathlib.Path) -> Config:
    """
    Loads the config file from the working directory.
    """
    logger.info(f'Loading config file from {working_dir}...')
    config_str = fs.config_file(working_dir).read_text()
    config_dict = yaml.load(config_str, Loader=yaml.FullLoader)
    config_obj = Config(**config_dict)
    return config_obj


def dump_config(config: Config, working_dir: pathlib.Path):
    """
    Dumps the config file to the working directory.
    """
    logger.info(f'Dumping config file to {working_dir}...')
    config_str = yaml.dump(asdict(config), default_flow_style=False)
    fs.config_file(working_dir).write_text(config_str)


def get_current_iteration(config: Config) -> int:
    """
    Gets the number of the current iteration, which is always one plus the sum of the number of processed scans and of
    pending scans
    """
    return len(config.processed_scans) + len(config.pending_scans) + 1


def load_classifier(working_dir: pathlib.Path, iteration: int) -> RandomForestClassifier:
    """
    Loads the classifier for the given iteration.
    """
    logger.info(f'Loading classifier for iteration {iteration}...')
    classifier_file = fs.classifiers_dir(working_dir) / f'classifier_{iteration}.pkl'
    with open(classifier_file, 'rb') as f:
        classifier = pickle.load(f)
    return classifier


def dump_classifier(classifier: RandomForestClassifier, working_dir: pathlib.Path, iteration: int):
    """
    Dumps the classifier for the given iteration.
    """
    logger.info(f'Dumping classifier for iteration {iteration}...')
    classifier_file = fs.classifier_file(working_dir, iteration)
    with open(classifier_file, 'wb') as f:
        pickle.dump(classifier, f)


def generate_grid_from_config(config: Config) -> np.ndarray:
    """
    Generates the Oracle grid from the config file. For each parameter, it generates an axis, and then combines all
    axes into a matrix, including all combinations. If an axis is provided in the config
    file, it takes that axis. Otherwise, it generates one from the range and resolution of that parameter.
    """
    logger.info('Generating grid from config...')
    axes = []
    for param_details in config.params.values():
        param_axis = param_details.get('axis')
        param_range = param_details.get('range')
        param_resolution = param_details.get('resolution')
        if param_axis is None and (param_range is None or param_resolution is None):
            raise ValueError("You must specify either an axis or a range and resolution for each parameter.")
        if param_axis is None:
            param_axis = np.arange(*param_range, param_resolution)
        axes.append(param_axis)
    grid = np.array(np.meshgrid(*axes)).T.reshape(-1, len(axes))
    return grid


def process_scan_results(working_dir: pathlib.Path):
    """
    Reads all pending scan CSV files from the working directory, creates the 1-sigma and 2-sigma columns from the chosen CL type
    values, and appends them to the processed scans CSV file.
    """
    config = load_config(working_dir)
    dataset_file = fs.dataset_file(working_dir)
    dataset_file_exists = dataset_file.exists()

    logger.info('Processing scan results...')

    scans = []

    # The list of scan files to process is the list of pending scans, plus the list of processed scans only if the
    # dataset file has been deleted.
    scan_files = config.pending_scans if dataset_file_exists else config.processed_scans + config.pending_scans

    # Process each scan file, adding the 1-sigma and 2-sigma columns to the dataframe
    for scan_file in scan_files:
        if not pathlib.Path(scan_file).exists():
            logger.warning(f'Scan file {scan_file} has not been generated yet, skipping...')
            continue
        scan_df = pd.read_csv(scan_file)
        scan_df['label-1-sigma'] = np.array((scan_df[CLTYPE] > SIGMA_1).astype(int))
        scan_df['label-2-sigma'] = np.array((scan_df[CLTYPE] > SIGMA_2).astype(int))
        scans.append(scan_df)

    # Combine all scans into one dataframe
    if len(scans) > 0:
        if dataset_file_exists:
            dataset_df = pd.read_csv(dataset_file)
            dataset_df = pd.concat([dataset_df, *scans])
        else:
            dataset_df = pd.concat(scans)
        dataset_df.to_csv(dataset_file, index=False)

    # Remove the pending scans from the config file, and add them to the processed scans
    config.processed_scans.extend(config.pending_scans)
    config.pending_scans = []
    dump_config(config, working_dir)


def generate_results(working_dir: pathlib.Path):
    """
    Writes to a CSV file the predictions of the latest available classifier
    """
    logger.info("Generating results...")
    config = load_config(working_dir)
    iteration = get_current_iteration(config)
    classifier = load_classifier(working_dir, iteration)
    param_grid = generate_grid_from_config(config)
    predictions = classifier.predict(param_grid)
    results_df = pd.DataFrame(param_grid)
    results_df.columns = config.params.keys()
    results_df['prediction'] = predictions
    return results_df


def prepare_next_scan(working_dir: pathlib.Path, param_values: pd.DataFrame):
    """
    Prepares the next contur scan by creating the new param file for the new scan, dumping the param values to the
    input points pickle file so that contur can use them for those params in DF mode, and prints the commands to be
    executed to start running the contur scan.
    """
    logger.info("Preparing next scan...")
    config = load_config(working_dir)
    iteration = get_current_iteration(config)

    # Dump the param values to the pickle file for contur to access it later
    input_file_path = str(fs.input_points_file(working_dir, iteration))
    param_values.to_pickle(input_file_path)
    param_values.to_csv(str(fs.input_points_file(working_dir, iteration, csv=True)))

    # Update the config file to reflect the scan that is about to be run
    config.pending_scans.append(str(fs.output_cls_file(working_dir, iteration)))
    dump_config(config, working_dir)

    # Create the param_file.dat for this iteration
    param_file_content = fs.param_file(working_dir).read_text().replace("DATAFRAME_LOCATION", input_file_path)
    new_param_file = fs.new_param_file(working_dir, iteration)
    new_param_file.write_text(param_file_content)

    # Print the commands to be executed to start running the contur scan
    logger.warning(textwrap.dedent(f"""
    You can now run the following commands:

    1. Contur batch to generate the events:
    contur-batch -p {new_param_file} -o contur_batch_output_{iteration} -Q medium --seed 101 -n 30000 -b 7TeV,8TeV,13TeV

    2. Contur to analyse the points
    contur -g contur_batch_output_{iteration} -o contur_analysis_{iteration}

    3. Contur export to extract the corresponding CSV wiThis th the results
    contur-export -i contur_analysis_{iteration}/contur.map -o output_cls/run-output-{iteration}.csv

    4. Contur oracle to process the results, train the classifier, and determine if more points need to be generated
    contur-oracle start
    """))


def start_oracle(working_dir: pathlib.Path):
    verify_directory(working_dir)
    config = load_config(working_dir)
    grid = generate_grid_from_config(config)
    iteration = get_current_iteration(config)

    process_scan_results(working_dir)

    # Create an Oracle instance with the specified user-defined parameters
    oracle = Oracle(
        grid=grid,
        iteration_points=config.iteration_points,
        n_trees=NUMBER_OF_TREES,
        params=config.params.keys(),
        recall_goal=config.recall_goal,
        precision_goal=config.precision_goal,
        entropy_goal=config.entropy_goal,
        test_size=TEST_SIZE,
    )

    # Add existing dataset to the oracle points 'repository'
    dataset_file = fs.dataset_file(working_dir)
    if dataset_file.exists():
        dataset_df = pd.read_csv(dataset_file)
        oracle.add_new_points(dataset_df)

    # Run one training episode, thus obtaining the next batch of points to run with contur
    try:
        next_points = next(oracle.main())
        logger.warning(textwrap.dedent(oracle.status))
    except StopIteration:
        logger.warning(textwrap.dedent(oracle.status))
        return
    else:
        # Create the required files for running the next contur scan and print the relevant
        # commands the user must execute.
        prepare_next_scan(working_dir, next_points)
    finally:
        # Dump the updated classifier, if one has been generated (i.e. always except for the first iteration)
        if len(oracle.results_stack) > 0:
            dump_classifier(oracle.latest_classifier, working_dir, iteration)

