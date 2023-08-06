import os
import shutil
import sys
import csv
import json
import copy
import time
import atexit
import logging
import inspect
import argparse

import pandas as pd
import numpy as np
import torch
import torch.nn

from abc import abstractmethod
from torch.utils.data import DataLoader

logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s",
                    stream=sys.stdout, level=logging.INFO)


class RunningStatus:
    TRAIN = "train"
    TEST = "test"
    VAL = "val"


def validate(method):
    """Decorator to validate Client"""

    def wrapper(*args, **kwargs):
        cls = args[0]
        if cls.instance is None:
            cls()

        if cls.instance.enabled:
            return method(*args, **kwargs)
        else:
            if method.__name__.startswith("handle"):
                if len(args) > 1:
                    return args[1]
                else:
                    sig = inspect.signature(method)
                    handle_key = list(sig.parameters.keys())[1]
                    return kwargs[handle_key]

    return wrapper


class Client:

    PARAMS_DIR = "params"
    DATASET_DIR = "dataset"
    METRICS_DIR = "metrics"
    WEIGHTS_DIR = "weights"
    API_DATA_DIR = "api_data"

    PARAMS_FILENAME = "params.json"
    DATASET_FILENAME = "dataset.json"
    METRICS_FILENAME = "metrics.csv"

    METRICS_HEADER = ["seq", "tag", "value", "time"]

    DEFAULT_CLIENT_DIR_ENV_VAR = "CLIENT_DIR"
    DEFAULT_RESUME_DIR_ENV_VAR = "RESUME_DIR"
    DEFAULT_RESUME_MODEL_PATH_ENV_VAR = "RESUME_MODEL_PATH"
    DEFAULT_RUNNING_STATUS_ENV_VAR = "RUNNING_STATUS"

    RUNNING_STATUS_LIST = ["train", "test"]

    # weights file name should have to be "weights" with different ext
    # according to AI framework, such as ".pt" or ".pth" for pytorch,
    # or ".pb" for tensorflow.
    WEIGHTS_FILENAME = "weights"

    instance = None

    def __init__(self, client_dir: str = None, resume_dir: str = None,
                 resume_model_path: str = None):
        self.enabled = True

        # client_dir
        if client_dir is None:
            if self.DEFAULT_CLIENT_DIR_ENV_VAR in os.environ:   # normal mode (container running)
                self.client_dir = os.environ[self.DEFAULT_CLIENT_DIR_ENV_VAR]
                logging.info(f"Set client_dir from environ: {self.client_dir}")
            else:   # disable mode
                self.enabled = False
                logging.info(f"{self.__class__.__name__} client is disabled")

        else:   # debug mode
            self.client_dir = os.path.abspath(client_dir)
            if not os.path.exists(self.client_dir):
                os.makedirs(self.client_dir)
            logging.info(f"Set client_dir from arguments: {self.client_dir}")

        # get resume mode path
        # # from arguments
        if resume_model_path:
            self.resume_model_path = resume_model_path
        # # from enviromnent variables
        elif self.DEFAULT_RESUME_MODEL_PATH_ENV_VAR in os.environ:
            self.resume_model_path = os.environ[self.DEFAULT_RESUME_MODEL_PATH_ENV_VAR]
        # # from resume_dir
        else:
            if resume_dir is None:
                if self.DEFAULT_RESUME_DIR_ENV_VAR in os.environ:
                    self.resume_dir = os.environ[self.DEFAULT_RESUME_DIR_ENV_VAR]
                    logging.info(f"Set resume_dir from environ: {self.resume_dir}")
                else:
                    self.resume_dir = None
                    logging.info("resume_dir is not provided(ok with the first round)")
            else:
                self.resume_dir = os.path.abspath(resume_dir)
                logging.info(f"Set resume_dir from arguments: {self.resume_dir}")

            if self.resume_dir is not None:
                self.resume_model_path = os.path.join(self.resume_dir,
                                                      "aggregated",
                                                      self.WEIGHTS_FILENAME)
            else:
                self.resume_model_path = None

        # running status
        if self.DEFAULT_RUNNING_STATUS_ENV_VAR in os.environ:
            self.running_status = \
                os.environ[self.DEFAULT_RUNNING_STATUS_ENV_VAR].lower()
            assert self.running_status in self.RUNNING_STATUS_LIST
        else:
            self.running_status = None

        if self.enabled:
            self.params_dir = os.path.join(self.client_dir, self.PARAMS_DIR)
            self.metrics_dir = os.path.join(self.client_dir, self.METRICS_DIR)
            self.dataset_dir = os.path.join(self.client_dir, self.DATASET_DIR)
            self.weights_dir = os.path.join(self.client_dir, self.WEIGHTS_DIR)
            self.api_data_dir = os.path.join(self.client_dir, self.API_DATA_DIR)

            self.model = None

            atexit.register(self.save)

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    @classmethod
    def disable(cls, disable: bool = True):
        cls.instance.enabled = not disable

    @classmethod
    @validate
    def handle_dataset(cls, dataset, key: str):
        cls.add_dataset_quantity(key, len(dataset))
        return dataset

    @classmethod
    @validate
    def add_dataset_quantity(cls, dataset: str, quantity: int):
        """
        Parameters
        ----------
        dataset : str
            Name of dataset: train, training, val, validation, test
        quantity : int
            Dataset quantity.
        """
        dataset = dataset.lower()
        dataset = RunningStatus.TRAIN if RunningStatus.TRAIN in dataset else dataset
        dataset = RunningStatus.VAL if RunningStatus.VAL in dataset else dataset
        dataset = RunningStatus.TEST if RunningStatus.TEST in dataset else dataset

        # assert dataset in [RunningStatus.TRAIN,
        #                    RunningStatus.VAL,
        #                    RunningStatus.TEST], dataset
        assert quantity > 0

        if not os.path.exists(cls.instance.dataset_dir):
            os.makedirs(cls.instance.dataset_dir)

        dataset_file = os.path.join(cls.instance.dataset_dir, cls.DATASET_FILENAME)
        if os.path.exists(dataset_file):
            with open(dataset_file, "r") as f:
                json_data = json.load(f)
            json_data[dataset] = quantity
        else:
            json_data = {dataset: quantity}

        with open(dataset_file, "w") as f:
            json.dump(json_data, f)

    @classmethod
    @validate
    def add_scalar(cls, tag: str, value: float):
        value = float(value)

        if not os.path.exists(cls.instance.metrics_dir):
            os.makedirs(cls.instance.metrics_dir)

        metrics_file = os.path.join(cls.instance.metrics_dir,
                                    cls.METRICS_FILENAME)
        if os.path.exists(metrics_file):
            df = pd.read_csv(metrics_file)
        else:
            df = pd.DataFrame(columns=cls.METRICS_HEADER)

        tag_df = df[df["tag"] == tag]
        num = len(tag_df)

        data = {"seq": num + 1, "tag": tag,
                "value": value, "time": int(time.time())}
        df.append(data, ignore_index=True).to_csv(metrics_file, index=False)

    @classmethod
    @validate
    def add_scalars(cls, scalars: dict):
        for tag, value in scalars.items():
            cls.add_scalar(tag, value)

    @classmethod
    @validate
    def add_param(cls, item: str, value):
        if cls.instance.running_status == RunningStatus.TRAIN:
            cls.add_params({item: value})

    @classmethod
    @validate
    def add_params(cls, params: dict):
        if cls.instance.running_status == RunningStatus.TRAIN:
            if not os.path.exists(cls.instance.params_dir):
                os.makedirs(cls.instance.params_dir)

            params = copy.deepcopy(params)
            params_file = os.path.join(cls.instance.params_dir,
                                       cls.PARAMS_FILENAME)
            if os.path.exists(params_file):
                with open(params_file) as f:
                    params.update(json.load(f))

            with open(params_file, "w") as f:
                json.dump(params, f)

    @classmethod
    @validate
    def handle_arguments(cls, args: argparse.Namespace) -> argparse.Namespace:
        # todo remove unnecessary arguments
        cls.add_params(args.__dict__)
        return args

    @classmethod
    @validate
    def handle_model(cls, model):
        raise NotImplementedError

    def _create_api_data(self):
        if not os.path.exists(self.api_data_dir):
            os.makedirs(self.api_data_dir)

        # params - copy from self.params_dir/params.json
        if self.running_status == "train":
            api_params_dir = os.path.join(self.api_data_dir, "params")
            if not os.path.exists(api_params_dir):
                os.makedirs(api_params_dir)
            shutil.copy(src=os.path.join(self.params_dir, self.PARAMS_FILENAME),
                        dst=os.path.join(api_params_dir, "params.json"))

        # metrics - data
        api_metrics_dir = os.path.join(self.api_data_dir, "metrics")
        if not os.path.exists(api_metrics_dir):
            os.makedirs(api_metrics_dir)
        src_path = os.path.join(self.metrics_dir, self.METRICS_FILENAME)
        src_df = pd.read_csv(src_path).fillna(value="-")

        # metrics - summary & trend data
        summary_data = {}
        trend_data = {}
        for tag, tag_df in src_df.groupby(by="tag"):
            df = tag_df.sort_values(by="seq")
            summary_data[tag] = round(df["value"].iloc[-1], 3)
            trend_data[tag] = [round(v, 3) for v in df["value"].tolist()]

        path_summary = os.path.join(api_metrics_dir, "metrics_summary.json")
        with open(path_summary, "w") as f:
            json.dump(summary_data, f)

        if self.running_status == "train":
            path_trend = os.path.join(api_metrics_dir, "metrics_trend.json")
            with open(path_trend, "w") as f:
                json.dump(trend_data, f)

    @abstractmethod
    def save_model(self, model_path: str):
        raise NotImplementedError

    def save(self):
        if self.enabled:
            if self.running_status == "train":
                if not os.path.exists(self.weights_dir):
                    os.makedirs(self.weights_dir)
                weights_file = os.path.join(self.weights_dir,
                                            self.WEIGHTS_FILENAME)
                self.save_model(weights_file)

            self._create_api_data()


class TorchClient(Client):

    WEIGHTS_FILENAME = "weights.pth"

    @classmethod
    @validate
    def handle_dataloader(cls, dataloader: DataLoader, key: str) -> DataLoader:
        cls.add_dataset_quantity(key, len(dataloader.dataset))
        return dataloader

    @classmethod
    @validate
    def handle_model(cls, model: torch.nn.L1Loss):
        cls.instance.model = model

        # load resumed weights --- aggregated weights from last round
        if cls.instance.resume_model_path is not None and \
                cls.instance.running_status == RunningStatus.TRAIN:

            weights_path = cls.instance.resume_model_path
            logging.info(f"The resumed weights paths is supposed to be: "
                         f"{weights_path}")

            if os.path.exists(weights_path):
                if not torch.cuda.is_available():
                    state_dict = torch.load(weights_path, map_location="cpu")
                    logging.info("cuda is not available in loading weights, "
                                 "set map_location=cpu")
                else:
                    state_dict = torch.load(weights_path, map_location="cuda:0")
                    logging.info("cuda is available in loading weights, "
                                 "set map_location=cuda:0")

                cls.instance.model.load_state_dict(state_dict)
                logging.info("Last round aggregated weights is loaded.")

            else:
                logging.warning("No resumed weights file found --- "
                                "ok if it is the first round!")

        return cls.instance.model

    @classmethod
    @validate
    def handle_optimizer(cls, optimizer: torch.optim.Optimizer):
        cls.instance.optimizer = optimizer
        return cls.instance.optimizer

    @classmethod
    @validate
    def handle_criterion(cls, criterion):
        cls.instance.criterion = criterion
        return cls.instance.criterion

    def save_model(self, model_path: str):
        torch.save(self.model.state_dict(), model_path)


class FlowerClient(Client):

    WEIGHTS_FILENAME = "parameters.npy"

    @classmethod
    @validate
    def handle_model(cls, model: np.ndarray):
        cls.instance.model = model
        return cls.instance.model

    def save_model(self, model_path: str):
        np.save(model_path, self.model, allow_pickle=True)
