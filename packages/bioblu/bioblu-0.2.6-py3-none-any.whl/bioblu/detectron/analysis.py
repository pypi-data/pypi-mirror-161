#!/usr/bin/env python3

import json
import logging
import re
import os
import pandas as pd
from typing import List
import yaml

import detectron2.config
from detectron2.config import get_cfg


def find_slurm_file(fdir) -> str:
    slurm_file_pattern = re.compile(r"slurm-\d\d\d\d\.out$")
    fpaths = [os.path.join(fdir, f) for f in sorted(os.listdir(fdir))]

    slurm_files = []
    for f in fpaths:
        match = slurm_file_pattern.findall(f)
        if match:
            slurm_files.append(match[0])
    if slurm_files:
        return slurm_files[0]
    return ""


def load_slurm_output(fdir) -> list:
    slurm_out_contents = []
    slurm_file = find_slurm_file(fdir)
    if slurm_file:
        try:
            with open(os.path.join(fdir, slurm_file), "r") as f:
                slurm_out_contents = f.readlines()
        except FileNotFoundError:
            print(f"Did not find slurm file {slurm_file}")
    return slurm_out_contents


def get_dataset_name(fdir_res) -> str:
    """Extracts the dataset name from the slurm output file."""
    dataset_name = ""
    slurm_contents = load_slurm_output(fdir_res)
    logging.info(f"Slurm loaded: {bool(slurm_contents)}")
    for line in slurm_contents:
        line_s = line.strip()
        if line_s.startswith("yolo_ds_root_dir"):
            ds_path = line_s.lstrip("yolo_ds_root_dir:\t").strip().rstrip("/")
            dataset_name = os.path.split(ds_path)[-1]
    return dataset_name


def strip_filepath(fpath: str):
    return fpath.replace("file://", "")


def put_slurm_id_to_front(df):
    colnames = df.columns.tolist()
    colnames = [colnames.pop(colnames.index("SLURM_ID"))] + colnames
    return df[colnames]


def create_empty_eval_results_dict() -> dict:
    data = {"bbox.AP": [pd.NA],
            "bbox.AP50": [pd.NA],
            "bbox.AP75": [pd.NA],
            "bbox.APs": [pd.NA],
            "bbox.APm": [pd.NA],
            "bbox.APl": [pd.NA],
            }
    return data


def create_empty_eval_results_df() -> pd.DataFrame:
    data = {"bbox.AP": [pd.NA],
            "bbox.AP50": [pd.NA],
            "bbox.AP75": [pd.NA],
            "bbox.APs": [pd.NA],
            "bbox.APm": [pd.NA],
            "bbox.APl": [pd.NA],
            }
    return pd.DataFrame(data)


def get_slurm_id_from_path(fpath: str):
    pattern = re.compile(r".*/(\d\d\d\d)_\d\d\d\d-\d\d-\d\d_\d\d\d\d\d\d")
    logging.info(f"Path: {fpath}")
    if fpath:
        match = pattern.findall(fpath)
        logging.debug(match)
        if match:
            return match[0]
    return None


def get_date_from_path(fpath:str):
    pattern = re.compile(r".*/\d\d\d\d_(\d\d\d\d-\d\d-\d\d)_\d\d\d\d\d\d")
    logging.info(f"Path: {fpath}")
    if fpath:
        match = pattern.findall(fpath)
        logging.debug(match)
        if match:
            return match[0]
    return None


def load_cfg(fpath_cfg: str) -> detectron2.config.CfgNode:
    cfg = get_cfg()
    try:
        cfg.merge_from_file(fpath_cfg)
    except AssertionError:
        cfg = {}
    return cfg


def flatten_cfg(cfg: detectron2.config.CfgNode):
    cfg_dict = dict(cfg.items())
    cfg_flat = pd.DataFrame(pd.json_normalize(cfg_dict))
    return cfg_flat


def load_cfg_flat(fpath_cfg: str):
    try:
        cfg = load_cfg(fpath_cfg)
    except KeyError as e:  # If there are entries that detectron2 does not want/know
        print(f"KeyError. Falling back to loading via yaml. {fpath_cfg}: Error: {e}")
        with open(fpath_cfg, "r") as f:
            cfg = yaml.safe_load(f)

    return flatten_cfg(cfg)


def load_eval_results(fpath_eval_results_txt: str) -> dict:
    """Loads eval """
    results = create_empty_eval_results_dict()
    if os.path.exists(fpath_eval_results_txt):
        if not os.stat(fpath_eval_results_txt).st_size == 0:
            with open(fpath_eval_results_txt, "r") as f:
                results = json.load(f)
        else:
            print(f"File is empty:{fpath_eval_results_txt}. Using empty fallback results object.")
    else:
        print(f"Did not find file {fpath_eval_results_txt}. Using empty fallback results object.")
    return results


def merge_cfg_and_results(fpath_cfg, fpath_eval_results_txt):
    cfg = load_cfg_flat(fpath_cfg)
    results = pd.json_normalize(load_eval_results(fpath_eval_results_txt))
    line = pd.DataFrame(cfg)
    line = line.join(results)  # Glue the results to the end of the line
    return line


def add_line_to_existing_csv(fpath_csv: str, line: pd.DataFrame):
    try:
        existing = pd.read_csv(fpath_csv)
    except FileNotFoundError:
        print(f"Creating new csv file, provided csv file not found: {fpath_csv}")
        line.to_csv(fpath_csv)
    else:
        existing = existing.append(line)
        existing.to_csv(fpath_csv)


def load_table(fdir_results) -> pd.DataFrame:
    cfg_path = os.path.join(fdir_results, "cfg.yaml")
    res_fpath = os.path.join(fdir_results, "evaluation_results.txt")
    data = merge_cfg_and_results(cfg_path, res_fpath)
    data["Results_dir"] = fdir_results
    data["SLURM_ID"] = get_slurm_id_from_path(fdir_results)
    data["Date"] = get_date_from_path(fdir_results)
    data["DS"] = get_dataset_name(fdir_results)
    return data


def merge_multiple_results(fdirs: List[str]):
    """
    Takes a list of training result dirs and merges all their settings and results into one data frame
    :param fdirs:
    :return:
    """
    fpaths = [strip_filepath(fpath) for fpath in fdirs]
    data = pd.DataFrame()
    for fpath in fpaths:
        logging.info(f"Processing {fpath}")
        data = data.append(load_table(fpath))
    return data


def save_cfg_as_csv(fpath_cfg) -> None:
    """Saves a single config as a one-liner csv with the same name"""
    fdir, fname = os.path.split(fpath_cfg)
    fname_base = fname.split(".")[0]
    fpath_csv_out = os.path.join(fdir, fname_base + ".csv")
    cfg_flat = load_cfg_flat(fpath_cfg)
    logging.info(f"Saving as {fpath_csv_out}")
    cfg_flat.to_csv(fpath_csv_out)


def get_all_cfg_and_results(fdir: str, save_as: str = "", select_columns: list = None):
    fdirs = [os.path.join(fdir, p) for p in sorted(os.listdir(fdir)) if os.path.isdir(os.path.join(fdir, p))]
    fdirs = [p for p in fdirs if get_slurm_id_from_path(p)]  # Only keep those that follow the slurmid-date-time pattern
    all_merged = merge_multiple_results(fdirs)
    if select_columns is not None:
        all_merged = all_merged[select_columns]
    if save_as:
        all_merged.to_csv(save_as)
    return all_merged


if __name__ == "__main__":
    loglevel = logging.DEBUG
    logformat = "[%(levelname)s]\t%(funcName)15s: %(message)s"
    logging.basicConfig(level=loglevel, format=logformat)
    logging.disable()

    # save_path = "/home/findux/Desktop/results.csv"
    #
    #
    # data = merge_multiple_results(fdirs)
    # data.to_csv(save_path)

    fdir = "/media/findux/DATA/Documents/Malta_II/results/"
    save_to = "/home/findux/Desktop/results_merged.csv"
    columns = ["Date",
               "SLURM_ID",
               "DS", "Results_dir",
               "SOLVER.BASE_LR",
               "SOLVER.IMS_PER_BATCH",
               "SOLVER.MAX_ITER",
               "MODEL.ROI_HEADS.SCORE_THRESH_TEST",
               "MODEL.ROI_HEADS.SCORE_THRESH_TRAIN",
               ]
    get_all_cfg_and_results(fdir, save_to, columns)

    # resdir = "/media/findux/DATA/Documents/Malta_II/results/5693_2022-05-25_154629"
    # DS = get_dataset_name(resdir)
    # print(DS)