import os
import sys
import csv
import json
import logging
import torch

from abc import abstractmethod
from collections import OrderedDict
from .constants import CHECK_METRICS, CHECK_PARAMS, METRICS_HEADER, \
    PARAMS_HEADER, CHECK_DATASET

logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s",
                    stream=sys.stdout, level=logging.INFO)

STATUS = ["training", "validation", "test"]


class FedCheck:

    DEFAULT_CHECK_DIR_ENV_VAR = "${CHECK_DIR}"

    instance = None
    initialized = False

    def __init__(self, check_dir: str = None):
        if not self.initialized:
            if check_dir is not None:
                self.check_dir = check_dir
            else:
                if self.DEFAULT_CHECK_DIR_ENV_VAR in os.environ:
                    self.check_dir = os.environ[self.DEFAULT_CHECK_DIR_ENV_VAR]
                else:
                    logging.warning("No check_dir found in environ.")
                    self.check_dir = os.path.abspath(os.path.curdir)

            logging.info(f"check_dir: {self.check_dir}")

            self.params_dir = os.path.join(self.check_dir, "params")
            self.metrics_dir = os.path.join(self.check_dir, "metrics")
            self.dataset_dir = os.path.join(self.check_dir, "dataset")
            self.weights_dir = os.path.join(self.check_dir, "weights")
            for d in [self.params_dir, self.metrics_dir, self.dataset_dir,
                      self.weights_dir]:
                if not os.path.exists(d):
                    os.makedirs(d)
            self.initialized = True

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    @classmethod
    def _validate_init(cls):
        if not cls.initialized:
            cls()

    @property
    @abstractmethod
    def model_filename(self) -> str:
        raise NotImplementedError

    @classmethod
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
        dataset = "training" if "train" in dataset else dataset
        dataset = "validation" if "val" in dataset else dataset
        dataset = "test" if "test" in dataset else dataset

        assert dataset in STATUS
        assert quantity > 0

        dataset_file = os.path.join(cls.instance.dataset_dir, CHECK_DATASET)
        if os.path.exists(dataset_file):
            with open(dataset_file, "r") as f:
                json_data = json.load(f)
            json_data[dataset] = quantity
        else:
            json_data = {dataset: quantity}

        with open(dataset_file, "w") as f:
            json.dump(json_data, f)

    @classmethod
    def add_metrics(cls, metrics: str, value: float, epoch: int, status: str):
        """

        Parameters
        ----------
        metrics : str
            Metrics name.
        value : float
            Metrics value.
        epoch : int
            Local epoch.
        status : str
            Status for the model: train, training, val, validation, test.

        """
        cls._validate_init()
        status = status.lower()
        status = "training" if "train" in status else status
        status = "validation" if "val" in status else status
        status = "test" if "test" in status else status
        assert status in STATUS

        def get_row(locals_dict):
            return [locals_dict[h] for h in METRICS_HEADER]

        metrics_file = os.path.join(cls.instance.metrics_dir, CHECK_METRICS)
        add_header = False if os.path.exists(metrics_file) else True
        with open(metrics_file, "a") as f:
            csv_writer = csv.writer(f)
            if add_header:
                csv_writer.writerow(METRICS_HEADER)
            row = get_row(locals())
            csv_writer.writerow(row)

    @classmethod
    @abstractmethod
    def add_weights(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def add_params(cls, params: dict):
        cls._validate_init()
        params_file = os.path.join(cls.instance.params_dir, CHECK_PARAMS)
        add_header = False if os.path.exists(params_file) else True
        with open(params_file, "w") as f:
            csv_writer = csv.writer(f)
            if add_header:
                csv_writer.writerow(PARAMS_HEADER)
            for k, v in params.items():
                csv_writer.writerow([k, v])


class TorchFedCheck(FedCheck):

    @property
    def model_filename(self) -> str:
        return "weights.pth"

    @classmethod
    def add_weights(cls, state_dict: OrderedDict):
        cls._validate_init()
        instance = cls.instance
        weights_file = \
            os.path.join(instance.weights_dir, instance.model_filename)
        torch.save(state_dict, weights_file)
