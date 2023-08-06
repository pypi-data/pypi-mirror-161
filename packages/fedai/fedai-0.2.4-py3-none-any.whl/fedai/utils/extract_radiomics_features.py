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

from typing import Optional, List
from multiprocessing import Manager, Pool
# from ffprobe import FFProbe
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


def is_video(path: str) -> bool:
    ext = os.path.splitext(path)[1].replace(".", "")
    if not ext:
        return False
    else:
        return ext.lower() in VIDEO_EXTS


def check_data(paths: List[str]) -> int:
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
    video_paths = [p for p in paths if is_video(p)]
    if video_paths:
        if len(video_paths) == len(paths):
            return 1
        else:
            return 2
    else:
        return 0


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


def extract_non_ts(group_task: List, extractor, result_path: str, lock):
    imgs = []
    masks = []
    labels = []
    for data_path, mask_path, label in group_task:
        # images
        img = cv.imread(data_path)
        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        img = sitk.GetImageFromArray(img_gray)
        imgs.append(img)

        # masks
        if mask_path:
            mask = cv.imread(mask_path)
            mask = cv.cvtColor(mask, cv.COLOR_BGR2GRAY)
            mask = sitk.GetImageFromArray(mask)
        else:
            mask = np.ones(shape=img_gray.shape[:2])
            mask[0, 0] = 0
            mask = sitk.GetImageFromArray(mask)
        masks.append(mask)

        # labels
        labels.append(label)

    features = [extractor.execute(img, mask, label=1)
                for img, mask in zip(imgs, masks)]
    feat_df = pd.DataFrame(features)
    feat_df[COL_LABEL] = labels

    with lock:
        if not os.path.exists(result_path):
            feat_df.to_csv(result_path, index=False)
        else:
            feat_df.to_csv(result_path, index=False, mode="a", header=False)


def extract_ts(data_path: str, mask_path: Optional[str], label, extractor,
               result_path: str):
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
    features = [extractor.execute(frame, mask, label=1) for frame in frames]
    feat_df = pd.DataFrame(features)
    feat_df[COL_LABEL] = label

    if os.path.exists(result_path):
        result_path = rename_duplicate_path(result_path)

    feat_df.to_csv(result_path, index=False)


def extract(data_dir: str, result_dir: str, config_path: str,
            processes: int = 2) -> None:
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

    # non-time series
    if data_type == 0:
        result_path = os.path.join(feature_data_dir, RADIOMIC_FEATURE_FILENAME)
        assert not os.path.exists(result_path)

        group_len = 1000
        group_tasks = [tasks[i: i + group_len]
                       for i in range(0, len(tasks), group_len)]

        lock = Manager().Lock()
        bar = tqdm.tqdm(total=len(group_tasks))
        for group_task in group_tasks:
            pool.apply_async(
                func=extract_non_ts,
                args=(group_task, extractor, result_path, lock),
                callback=lambda _: bar.update()
            )
            # extract_non_ts(group_task, extractor, result_path, lock)

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
                func=extract_ts,
                args=(data_path, mask_path, label, extractor, result_path),
                callback=lambda _: bar.update()
            )
            # extract_ts(data_path, mask_path, label, extractor, result_path)

    pool.close()
    pool.join()


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
