import os
import shutil
import sys
import re
import argparse
import logging
import tqdm
import skvideo.io
import numpy as np
import pandas as pd
import cv2 as cv
import radiomics
import SimpleITK as sitk

from typing import Optional, List, Union
from multiprocessing import Manager, Pool
# from ffprobe import FFProbe
from collections import OrderedDict
from radiomics.featureextractor import RadiomicsFeatureExtractor


logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s",
                    stream=sys.stdout, level=logging.ERROR)
radiomics.logger.setLevel(logging.CRITICAL)


COL_LABEL = "label"

LABELS_FILENAME = "labels.csv"

DST_CONFIG_NAME = "radiomics_config.yaml"

RADIOMIC_FEATURE_DIRNAME = "feature_data"
RADIOMIC_FEATURE_FILENAME = "features.csv"

VIDEO_EXTS = {"mkv", "flv", "vob", "ogv", "ogg", "avi", "mov", "wmv", "rm",
              "rmvb", "mp4", "m4p", "m4v", "mpg", "mp2", "mpeg", "mpe", "mpv",
              "m2v", "m4v", "3gp", "3g2"}


class DatasetType:
    TS = 0
    NON_TS = 1


def is_video(path: str) -> bool:
    ext = os.path.splitext(path)[1].replace(".", "")
    if not ext:
        return False
    else:
        return ext.lower() in VIDEO_EXTS


def check_data(paths: Union[str, List[str]]) -> int:
    """

    Parameters
    ----------
    paths : List of data paths

    Returns
    -------
    0 : 2D or 3D, not time series
    1 : Video, time series
    2 : Error, mix includes 0, 1

    """
    # video_paths = [p for p in paths if len(FFProbe(p).video)]
    if isinstance(paths, str):
        paths = [paths]

    video_paths = [p for p in paths if is_video(p)]
    if video_paths:
        if len(video_paths) == len(paths):
            return DatasetType.TS
        else:
            raise Exception("It is supposed only time series data or"
                            " non-time series data in the paths.")
    else:
        return DatasetType.NON_TS


def convert_to_rel_paths(paths: List[str], root_dir: str) -> List[str]:
    # todo
    return paths


def rename_duplicate_path(path: str) -> str:
    p, ext = os.path.splitext(path)
    if re.match(".+_\d", os.path.basename(p)):
        splits = p.split("_")
        seq = int(splits[-1])
        new_path = "_".join(splits[:-1]) + f"_{seq + 1}" + ext
    else:
        new_path = p + "_1" + ext

    return rename_duplicate_path(new_path) \
        if os.path.exists(new_path) else new_path


class RadiomicsUtility:

    def __init__(self, extractor: RadiomicsFeatureExtractor, data_type: int):
        self.extractor = extractor
        self.dataset_type = data_type

    def extract(self, data_path: str, mask_path: str = None) -> \
            Union[OrderedDict, List[OrderedDict]]:

        assert self.dataset_type == check_data([data_path])

        if self.dataset_type == DatasetType.TS:
            return self._extract_ts(data_path, mask_path)
        else:
            return self._extract_non_ts(data_path, mask_path)

    def _extract_non_ts(self, data_path: str, mask_path: Optional[str]) -> \
            OrderedDict:
        # images
        img = cv.imread(data_path)
        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        img = sitk.GetImageFromArray(img_gray)

        # masks
        if mask_path:
            mask = cv.imread(mask_path)
            mask = cv.cvtColor(mask, cv.COLOR_BGR2GRAY)
            mask = sitk.GetImageFromArray(mask)
        else:
            mask = np.ones(shape=img_gray.shape[:2])
            mask[0, 0] = 0
            mask = sitk.GetImageFromArray(mask)

        return self.extractor.execute(img, mask, label=1)

    def _extract_ts(self, data_path: str, mask_path: Optional[str]) -> \
            List[OrderedDict]:

        frames = [cv.cvtColor(frame, cv.COLOR_RGB2GRAY)
                  for frame in skvideo.io.vreader(data_path)]

        if mask_path:
            mask = cv.imread(mask_path)
            mask = cv.cvtColor(mask, cv.COLOR_BGR2GRAY)
            mask = sitk.GetImageFromArray(mask)
        else:
            mask = np.ones(shape=frames[0].shape[:2])
            mask[0, 0] = 0
            mask = sitk.GetImageFromArray(mask)

        frames = [sitk.GetImageFromArray(frame) for frame in frames]

        return [self.extractor.execute(frame, mask, label=1) for frame in frames]


def extract_non_ts_(group_task: List, utility: RadiomicsUtility,
                    result_path: str, lock):
    feature_list = []
    for data_path, mask_path, label in group_task:
        feature: OrderedDict = utility.extract(data_path, mask_path)
        feature[COL_LABEL] = label
        feature_list.append(feature)

    feature_df = pd.DataFrame(feature_list)
    with lock:
        if not os.path.exists(result_path):
            feature_df.to_csv(result_path, index=False)
        else:
            feature_df.to_csv(result_path, index=False, mode="a", header=False)


def extract_ts_(data_path: str, mask_path: Optional[str], label,
                utility: RadiomicsUtility, result_path: str):

    feature_list: List[OrderedDict] = utility.extract(data_path, mask_path)
    feature_df = pd.DataFrame(feature_list)
    feature_df[COL_LABEL] = label

    if os.path.exists(result_path):
        result_path = rename_duplicate_path(result_path)

    feature_df.to_csv(result_path, index=False)


def extract(data_dir: str, result_dir: str, config_path: str,
            processes: int = 2) -> RadiomicsUtility:
    """

    Parameters
    ----------
    data_dir : str
        原始数据文件夹路径，文件下面必须包含一个annotation.csv，其中记录了数据集信息，
    该csv的header包含：
        1. data_path - 以data_dir为根目录的数据相对路径，必须字段
        2. mask_path - 以data_dir为根目录的mask相对路径，可选字段，如果没有该字段，
                       则在整个数据区域抽取radiomics特征
        3. label - 数据的目标值

    result_dir : str
        提取到的radiomics特征文件存放文件夹

    config_path : str
        radiomics配置文件路径

    processes : int
        提取radiomics的进程数量

    """

    data_dir = os.path.abspath(data_dir)
    labels_path = os.path.join(data_dir, LABELS_FILENAME)

    assert os.path.exists(data_dir), "Dataset directory not exists."
    assert os.path.exists(labels_path), f"No labels.csv found in {data_dir}."
    assert os.path.exists(config_path), f"Config yaml file not found."

    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    feature_data_dir = os.path.join(result_dir, RADIOMIC_FEATURE_DIRNAME)
    if not os.path.exists(feature_data_dir):
        os.makedirs(feature_data_dir)

    # copy config file in result_dir
    dst_config_path = os.path.join(result_dir, DST_CONFIG_NAME)
    shutil.copy(src=config_path, dst=dst_config_path)

    # create tasks
    labels_df = pd.read_csv(labels_path)

    data_paths = [os.path.join(data_dir, rel_data_path)
                  for rel_data_path in labels_df["data_path"]]

    data_paths = convert_to_rel_paths(data_paths, data_dir)

    logging.info(f"Total {len(data_paths)} data found.")

    data_type = check_data(data_paths)
    assert data_type != 2, \
        "Dataset is mixed with time series data and non-time series data"
    logging.info(f"dataset type is {data_type}")

    mask_paths = []
    if "mask_path" in labels_df:
        mask_paths = [os.path.join(data_dir, rel_mask_path)
                      for rel_mask_path in labels_df["mask_path"]]
        mask_paths = convert_to_rel_paths(mask_paths, data_dir)
    else:
        logging.info("No mask found in labels.csv.")

    labels = labels_df[COL_LABEL].tolist()

    if mask_paths:
        tasks = [(data_path, mask_path, label)
                 for data_path, mask_path, label
                 in zip(data_paths, mask_paths, labels)]
    else:
        tasks = [(data_path, None, label)
                 for data_path, label in zip(data_paths, labels)]

    # execute tasks
    pool = Pool(processes=processes)
    extractor = RadiomicsFeatureExtractor(config_path)

    radiomics_utility = RadiomicsUtility(extractor=extractor,
                                         data_type=data_type)

    # non-time series
    if data_type == DatasetType.NON_TS:
        result_path = os.path.join(feature_data_dir, RADIOMIC_FEATURE_FILENAME)
        assert not os.path.exists(result_path)

        group_len = 1000
        group_tasks = [tasks[i: i + group_len]
                       for i in range(0, len(tasks), group_len)]

        lock = Manager().Lock()
        bar = tqdm.tqdm(total=len(group_tasks))
        for group_task in group_tasks:
            pool.apply_async(
                func=extract_non_ts_,
                args=(group_task, radiomics_utility, result_path, lock),
                callback=lambda _: bar.update()
            )

    # time series
    else:    # data_type == 1
        result_paths = [
            os.path.join(feature_data_dir,
                         os.path.splitext(os.path.basename(path))[0] + ".csv")
            for path in data_paths]

        bar = tqdm.tqdm(total=len(labels_df))
        for i, (data_path, mask_path, label) in enumerate(tasks):
            result_path = result_paths[i]
            pool.apply_async(
                func=extract_ts_,
                args=(data_path, mask_path, label, radiomics_utility, result_path),
                callback=lambda _: bar.update()
            )

    pool.close()
    pool.join()

    return radiomics_utility


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data_dir",
        type=str,
        help="raw data dir"
    )
    parser.add_argument(
        "--result_dir",
        type=str,
        help="Directory to save the features result."
    )
    parser.add_argument(
        "--config_path",
        type=str,
        help="yaml file path."
    )
    parser.add_argument(
        "--processes",
        type=int,
        help="multiprocessing pool max size."
    )

    args = parser.parse_args()

    extract(data_dir=args.data_dir,
            config_path=args.config_path,
            result_dir=args.result_dir,
            processes=args.processes)
