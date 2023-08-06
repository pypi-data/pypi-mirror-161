#!/usr/bin/env python3

import base64
import cv2
import datetime
import io
import json
import logging
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import natsort
import numpy as np
import os
import pandas as pd
from pathlib import Path
import PIL
from PIL import Image
from PIL import UnidentifiedImageError
import re
import shutil
from typing import List, Tuple

from bioblu.ds_manage import bbox_conversions
from bioblu.main import IMG_FORMATS, YOLO_IMG_FORMATS


# ToDo: - add_set_column(): refactor this into ds_split
#       - make the show_annotation script use class for color and add a label to each annotation.
#       - in create_yolo_annotation_txt_files(): Make this more generalizable, using list of categories and boxes.
#         Should include the possibility to receive empty bbox and category lists, only fname.
#       - Turn BBox into a dataclass?
#       -  Allow BBox conversions to return the output, not change the box itself (add "inplace" parameter?)
#       - Turn LabelmeAnnotation() into a dataclass?
#       - LabelmeAnnotation: add self.json_fpath (to self, basically)
#       - Maybe use tuples instead of lists for bboxes
#       - Make get_corresponding_file() recursive


class BoxFormatError(Exception):
    def __init__(self, error_message=None):
        if error_message is None:
            error_message = "Wrong BBox format."
        super().__init__(error_message)


class BBox:
    def __init__(self, bbox: List, material: str, bbox_format: str, img_width: int, img_height: int,
                 img_fpath=None, confidence=None):
        """

        :param bbox:
        :param material:
        :param bbox_format: can be one of: 'yolo', 'coco', 'voc', 'labelme'
        :param img_width:
        :param img_height:
        :param img_fpath:
        :param confidence:
        """
        self._BBOX_TYPE_OPTIONS = {'yolo', 'coco', 'voc', 'labelme'}
        self.material = material
        if bbox_format.lower() in self._BBOX_TYPE_OPTIONS:
            self.bbox_format = bbox_format.lower()
        else:
            raise ValueError(f'Invalid bbox type {type}. Possible bbox types: {self._BBOX_TYPE_OPTIONS}')
        self.bbox = bbox
        if self.bbox_format == "labelme":
            self.bbox = bbox_conversions.fix_labelme_point_order(self.bbox)
        self.img_width = img_width
        self.img_height = img_height
        self.img_dims_wh = (self.img_width, self.img_height)
        self.img_path = img_fpath
        self.img_name = None
        if self.img_path is not None:
            self.img_name = os.path.split(self.img_path)[-1]
        self.confidence = confidence

    @property  # Basically like a getter method, i.e. a dynamically-updating attribute.
    def box_center_xy(self) -> tuple:
        """
        Absolute center position in pixels (x, y).
        :return:
        """
        assert self.bbox_format in self._BBOX_TYPE_OPTIONS
        self.to_voc()
        xmin, ymin, xmax, ymax = self.bbox
        center_xy = (int((xmin + xmax) * 0.5), int((ymin + ymax) * 0.5))
        return center_xy

    @property
    def box_dims_wh(self):
        """
        Returns abs. box dimensions (width, height) in px.
        :return: (width, height)
        """
        assert self.bbox_format in self._BBOX_TYPE_OPTIONS
        self.to_coco()
        x, y, width, height = self.bbox
        return width, height

    def to_yolo(self):
        """Changes the bbox format to [center_x, center_y, width, height] (relative to image dimensions)."""
        if self.bbox_format != 'yolo':
            if self.bbox_format == 'voc':
                self.bbox = bbox_conversions.voc_to_yolo(self.bbox, self.img_width, self.img_height)
            elif self.bbox_format == 'coco':
                self.bbox = bbox_conversions.coco_to_yolo(self.bbox, self.img_width, self.img_height)
            elif self.bbox_format == 'labelme':
                self.bbox = bbox_conversions.labelme_to_yolo(self.bbox, self.img_width, self.img_height)
            self.bbox_format = 'yolo'
        else:
            logging.info('Already in yolo format.')

    def to_voc(self):
        """Changes the bbox format to [x0, y0, x1, y1] (absolute)."""
        if self.bbox_format != 'voc':
            if self.bbox_format == 'coco':
                self.bbox = bbox_conversions.coco_to_voc(self.bbox)
            elif self.bbox_format == 'labelme':
                self.bbox = bbox_conversions.labelme_to_voc(self.bbox)
            elif self.bbox_format == 'yolo':
                self.bbox = bbox_conversions.yolo_to_voc(self.bbox, self.img_width, self.img_height)
            self.bbox_format = 'voc'
        else:
            logging.info('Already in voc format.')

    def _return_as_coco(self) -> list:
        box_out = self.bbox
        if self.bbox_format != 'coco':
            if self.bbox_format == 'labelme':
                box_out = bbox_conversions.labelme_to_coco(self.bbox)
            elif self.bbox_format == 'voc':
                box_out = bbox_conversions.voc_to_coco(self.bbox)
            elif self.bbox_format == 'yolo':
                box_out = bbox_conversions.yolo_to_coco(self.bbox, self.img_width, self.img_height)
        return box_out

    def to_coco(self):
        """Changes the bbox format to [x0, y0, w, h] (absolute)."""
        if self.bbox_format != 'coco':
            if self.bbox_format == 'labelme':
                self.bbox = bbox_conversions.labelme_to_coco(self.bbox)
            elif self.bbox_format == 'voc':
                self.bbox = bbox_conversions.voc_to_coco(self.bbox)
            elif self.bbox_format == 'yolo':
                self.bbox = bbox_conversions.yolo_to_coco(self.bbox, self.img_width, self.img_height)
            self.bbox_format = 'coco'
        else:
            logging.info('Already in coco format.')

    def to_labelme(self):
        """Changes the bbox format to [[corner_0_x, corner_0_y], [corner_1_x, corner_1_y]] (absolute)."""
        if self.bbox_format != 'labelme':
            if self.bbox_format == 'coco':
                self.bbox = bbox_conversions.coco_to_labelme(self.bbox)
            elif self.bbox_format == 'voc':
                self.bbox = bbox_conversions.voc_to_labelme(self.bbox)
            elif self.bbox_format == 'yolo':
                self.bbox = bbox_conversions.yolo_to_labelme(self.bbox, self.img_width, self.img_height)
            self.bbox_format = 'labelme'
        else:
            logging.info('Already in labelme format.')

    def format_is_labelme(self) -> bool:
        if self.bbox_format == "labelme":
            return True
        else:
            return False

    def format_is_yolo(self) -> bool:
        if self.bbox_format == "yolo":
            return True
        else:
            return False

    def format_is_coco(self) -> bool:
        if self.bbox_format == "coco":
            return True
        else:
            return False

    def format_is_voc(self) -> bool:
        if self.bbox_format == "voc":
            return True
        else:
            return False

    def show(self):
        img = cv2.imread(self.img_path)[:, :, ::-1]
        coco_box = self._return_as_coco()
        fig, ax = plt.subplots()
        ax.imshow(img)
        rect = patches.Rectangle(coco_box[:2], coco_box[2], coco_box[3], color='red', fill=None)
        ax.add_patch(rect)
        plt.show()

    def __str__(self):
        return f"{self.bbox_format} BBox. Material: {self.material}. Coords: {self.bbox}. " \
               f"Confidence: {self.confidence}. Image: {self.img_path}"

    def __eq__(self, other):
        if not isinstance(other, BBox):
            return NotImplemented  # don't attempt to compare against unrelated types

        return (self._BBOX_TYPE_OPTIONS == other._BBOX_TYPE_OPTIONS) and (
                self.material == other.material) and (
                       self.bbox == other.bbox) and (
                       self.bbox_format.lower() == other.bbox_format.lower()) and (
                       self.img_name == other.img_name) and (
                       self.img_path == other.img_path) and (
                       self.img_width == other.img_width) and (
                       self.img_height == other.img_height) and (
                       self.img_dims_wh == other.img_dims_wh) and (
                       self.confidence == other.confidence)


class LabelmeAnnotation:
    def __init__(self, abs_img_fpath: str = None, annotations: List[BBox] = None, flags=None,
                 version="bioblu", save_img_data=False, fpath_json: str = None):
        """
        :param abs_img_fpath:
        :param annotations:
        :param flags:
        :param version:
        """
        self.version = version
        self.full_img_path = abs_img_fpath
        self.flags = flags
        if self.flags is None:
            self.flags = {}
        self.fpath_json = fpath_json
        self.shapes = []
        if not annotations:
            self.shapes = []
        else:
            for box in annotations:
                if not box.format_is_labelme():
                    print("WARNING: Original box is not in labelme format. Converting to labelme format.")
                    box.to_labelme()
                if not box.img_path == abs_img_fpath:
                    print(f"WARNING: inconsistent paths:\nabs_img_fpath: {abs_img_fpath}\nbbox path: {box.img_path}")
                self.shapes.append(box)

        self.img_dims_wh = None
        self.img_data = None
        if self.full_img_path:
            self.img_dims_wh = Image.open(self.full_img_path).size
            self.img_name = os.path.split(self.full_img_path)[-1]
            if save_img_data:
                self.img_data = encode_img_for_labelme(self.full_img_path)

    def add_box(self, box: BBox):
        if not box.format_is_labelme():
            raise BoxFormatError
        else:
            self.shapes.append(box)

    def to_json(self, overwrite=False, fpath_dst=None):
        bbox_dicts = []
        for box in self.shapes:
            bbox_dicts.append(cvt_labelme_bbox_to_shape_dict(box))
        out_dict = {"version": self.version,
                    "flags": self.flags,
                    "shapes": bbox_dicts,
                    "lineColor": [0, 255, 0, 128],
                    "fillColor": [255, 0, 0, 128],
                    "imagePath": self.img_name,
                    "imageData": self.img_data,
                    "imageHeight": self.img_dims_wh[1],
                    "imageWidth": self.img_dims_wh[0]
                    }
        if fpath_dst is None and self.fpath_json is None:
            raise FileNotFoundError("No target path specified. Provide either to LabelmeAnnotation class or in "
                                    ".to_json() method.")
        if fpath_dst is not None:
            target_path = fpath_dst
        else:
            target_path = self.fpath_json
        if os.path.isfile(target_path) and not overwrite:
            print("Not saved as json, file exists. Pass overwrite=True to overwrite.")
        else:
            with open(target_path, 'w') as f:
                f.write(json.dumps(out_dict, indent=2))


def clear_array_from_labelme_json(fpath, backup_orig=True):
    if backup_orig:
        fdir, fname = os.path.split(fpath)
        fdir_backup = os.path.join(fdir, "backup")
        os.makedirs(fdir_backup, exist_ok=True)
        shutil.copyfile(fpath, os.path.join(fdir_backup, fname))
    json_data = load_json(fpath)
    json_data["imageData"] = None
    with open(fpath, "w") as f:
        f.write(json.dumps(json_data, indent=2))


def clear_all_arrays_from_labelme_jsons(fdir):
    print(f"Clearing all arrays in {fdir}...")
    fpaths_json = get_all_fpaths_by_extension(fdir, (".json",))
    for fpath in fpaths_json:
        clear_array_from_labelme_json(fpath)
    print("Done.")


def inject_version_string_to_labelme(fpath_json: str, version_str: str = None, overwrite=False):
    """

    :param fpath_json:
    :param version_str:
    :param overwrite: If true, all versions will be overwritten. If False, only null values will be replaced.
    :return:
    """
    _annotation = load_json(fpath_json)
    _version_has_been_updated = False
    if "version" not in _annotation.keys():
        print(f"No 'version' key: {fpath_json}")
        return None
    _old_version = _annotation["version"]
    if _annotation["version"] is None:
        logging.info(f"Setting labelme version 'None' to '{version_str}'.")
        _annotation["version"] = version_str
        _version_has_been_updated = True
    else:
        if overwrite:
            logging.info(f"Overwriting labelme version '{_annotation['version']}' with '{version_str}'.")
            _annotation["version"] = version_str
            _version_has_been_updated = True
        else:
            print(
                f"Did not overwrite {_old_version} with {version_str}. Set overwrite=True to overwrite "
                f"existing version strings.S")
    if _version_has_been_updated:
        with open(fpath_json, "w") as f:
            f.write(json.dumps(_annotation, indent=2))
        print(f"Overwrote {_old_version} with {version_str}")


def inject_version_string_to_all_labelmes(fdir_labels: str, version_str: str, overwrite=False):
    """
    Recursive. Goes over all json files.
    :param fdir_labels:
    :param version_str:
    :param overwrite:
    :return:
    """
    json_fpaths = get_all_fpaths_by_extension(fdir_labels, ("json",))
    for fpath in json_fpaths:
        inject_version_string_to_labelme(fpath, version_str, overwrite=overwrite)


def load_labelme_annotation_file(fpath_json) -> LabelmeAnnotation:
    """
    Load the json file containing labelme annotations.
    Assumes that img files and corresponding JSON files are in the same directory!
    :param fpath_json:
    :return:
    """
    json_data = load_json(fpath_json)
    _loaded_bboxes = get_bboxes_from_labelme_json(fpath_json)
    logging.debug(f"First element of loaded boxes: {type(_loaded_bboxes[:1])}")
    _fpath_head = os.path.split(fpath_json)[0]
    _full_img_path = os.path.join(_fpath_head, json_data["imagePath"])
    logging.debug(_full_img_path)
    annotations = LabelmeAnnotation(abs_img_fpath=_full_img_path, annotations=_loaded_bboxes, fpath_json=fpath_json)
    return annotations


def decode_labelme_imgdata(encoded_img: str) -> PIL.Image:
    """
    Decodes labelimg imageData to a
    :param encoded_img:
    :return:
    """
    img_bytes = base64.b64decode(encoded_img)
    img_decoded = Image.open(io.BytesIO(img_bytes))
    return img_decoded


def cvt_voc_box_to_voc_dict(bbox: tuple) -> dict:
    """

    :param bbox: needs to be in format (x0, y0, x1, y1)
    :return:
    """
    coords = ("x0", "y0", "x1", "y1")
    boxdict = {k: v for k, v in zip(coords, bbox)}
    return boxdict


def cvt_coco_box_to_voc_dict(bbox: tuple) -> dict:
    """
    COCO box to dict

    :param bbox: (TLx, TLy, W, H)
    :return: xyxy dict
    """
    voc_bbox = bbox_conversions.coco_to_voc(list(bbox))
    return cvt_voc_box_to_voc_dict(voc_bbox)


def cvt_yolo_box_to_relative_voc_dict(bbox: list) -> dict:
    """
    Converts to "relative" voc dict: x0, y0, x1, y2}
    :param bbox: [center_x_rel, center_y_rel, width_rel, height_rel]
    :return:
    """
    center_x_rel, center_y_rel, width_rel, height_rel = bbox
    bbox_out = [center_x_rel - 0.5 * width_rel, center_y_rel - 0.5 * height_rel,
                center_x_rel + 0.5 * width_rel, center_y_rel + 0.5 * height_rel]
    names = ["x0", "y0", "x1", "y1"]
    if np.any(np.array(bbox_out) < 0):
        raise BoxFormatError(f"Box contains negative coordinates: {bbox_out}")
    return {k: v for k, v in zip(names, bbox_out)}


def convert_bbox_coco_to_yolo_bbox(coco_bbox: list, img_width: int, img_height: int):
    """
    DEPRECATED.
    Use bbox_conversions module instead.

    Converts a bbox list from coco to yolo format
    :param coco_bbox:
    :param img_width:
    :param img_height:
    :return:
    """
    _bbox_x, _bbox_y, _bbox_width, _bbox_height = coco_bbox
    bbox_center_x_normalised = (_bbox_x + 0.5 * _bbox_width) / img_width
    bbox_center_y_normalised = (_bbox_y + 0.5 * _bbox_height) / img_height
    bbox_width_normalised = (_bbox_width / img_width)
    bbox_height_normalised = (_bbox_height / img_height)
    bbox_out = [bbox_center_x_normalised, bbox_center_y_normalised, bbox_width_normalised, bbox_height_normalised]
    if np.any(np.array(bbox_out) < 0):
        raise BoxFormatError(f"Box contains negative coordinates: {bbox_out}")
    return bbox_out


def get_iou(bb1: dict, bb2: dict):
    """
    Based on code by Martin Thoma: https://stackoverflow.com/a/42874377
    Calculate the Intersection over Union (IoU) of two bounding boxes.

    Parameters
    ----------
    bb1 : dict
        Keys: {'x0', 'x1', 'y0', 'y1'}
        The (x0, y0) position is in the top left corner,
        the (x1, y1) position is in the bottom right corner
    bb2 : dict
        Keys: {'x0', 'x1', 'y0', 'y1'}
        The (x, y) position is at the top left corner,
        the (x1, y1) position is at the bottom right corner

    Returns
    -------
    float
        in [0, 1]
    """
    assert bb1['x0'] < bb1['x1']
    assert bb1['y0'] < bb1['y1']
    assert bb2['x0'] < bb2['x1']
    assert bb2['y0'] < bb2['y1']

    # determine the coordinates of the intersection rectangle
    x_left = max(bb1['x0'], bb2['x0'])
    y_top = max(bb1['y0'], bb2['y0'])
    x_right = min(bb1['x1'], bb2['x1'])
    y_bottom = min(bb1['y1'], bb2['y1'])

    # Check if there's overlap
    if x_right < x_left or y_bottom < y_top:
        return 0.0

    # The intersection of two axis-aligned bounding boxes is always an axis-aligned bounding box
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # compute the area of both AABBs
    bb1_area = (bb1['x1'] - bb1['x0']) * (bb1['y1'] - bb1['y0'])
    bb2_area = (bb2['x1'] - bb2['x0']) * (bb2['y1'] - bb2['y0'])

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the intersection area
    iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
    assert iou >= 0.0
    assert iou <= 1.0
    return iou


def add_set_column(annotations: pd.DataFrame, split_dict: dict, index_column_name='file_name') -> pd.DataFrame:
    """
    Adds a column "set" to the annotations pd.df that has the values "train", "val" and "test", depending on which set
    the corresponding image belongs to.

    :param annotations: annotations dataframe
    :param split_dict: dict containing as key the set ("train", "val" or "test") and as values e.g. file names
    used to identify which set an image belongs to.
    :param index_column_name:
    :return: pd.DataFrame
    """
    for k, v in split_dict.items():
        for _img_name in v:
            annotations.loc[annotations[index_column_name] == _img_name, 'set'] = k
    return annotations


def all_imgs_have_yolo_annotation(fdir) -> bool:
    """
    Checks whether all image files in the folder have a corresponding .txt file.
    :param fdir:
    :return:
    """
    # Get names of files
    img_files = [os.path.split(fpath)[-1] for fpath in sorted(os.listdir(fdir)) if fpath.lower().endswith(IMG_FORMATS)]
    img_names = [fpath.split('.')[0] for fpath in img_files]
    txt_files = [os.path.split(fpath)[-1] for fpath in sorted(os.listdir(fdir)) if fpath.lower().endswith(".txt")]
    txt_names = [fpath.split('.')[0] for fpath in txt_files]
    assert len(img_names) == len(set(img_names))
    # Check if they correspond
    for img in img_names:
        if img not in txt_names:
            print(f"Image {img} does not have a corresponding txt file.")
            return False
    # Check the reverse (only if more txt files than img files):
    if len(txt_names) > len(img_names):
        for txt in txt_names:
            if txt not in img_names:
                logging.debug(f"[ WARNING ] Text file {txt}.txt does not have a corresponding image file!")
    return True


def all_x_have_y(fdir: str, ext_x: str, ext_y: str):
    """
    Checks if all files (in folder fdir) with the extension ext_x have a corresponding file with the extension ext_y.
    :param fdir:
    :param ext_x:
    :param ext_y:
    :return:
    """
    flag = True
    x_files = [os.path.split(fpath)[-1] for fpath in sorted(os.listdir(fdir)) if fpath.lower().endswith(ext_x.lower())]
    x_names = [file.split('.')[0] for file in x_files]
    y_files = [os.path.split(fpath)[-1] for fpath in sorted(os.listdir(fdir)) if fpath.lower().endswith(ext_y.lower())]
    y_names = [file.split('.')[0] for file in y_files]
    for x in x_names:
        if x not in y_names:
            print(f"{x}.{ext_x} does not have a corresponding {x}.{ext_y}")
            flag = False
    return flag


def get_corresponding_file(base_file: str, checkdir: str, extensions: Tuple[str]) -> str:
    """
    Checks against files in checkdir if there is a file corresponding to the file specified as fpath_file.
    Can include or exclude extension. \n
    :param base_file: path or filename
    :param checkdir: fdir
    :param keep_extension: bool
    :param extension:
    :return:
    """
    extensions = tuple(ext.lower() for ext in extensions)

    basename = os.path.split(base_file)[-1].rsplit(".")[0]
    matches = []
    for root, dirs, files in os.walk(checkdir):
        for file in files:
            if file.lower().endswith(extensions):
                file_basename = file.rsplit(".")[0]
                if file_basename == basename:
                    matches.append(os.path.join(root, file))
    if not matches:
        return None
    if len(matches) > 1:
        print(f"More than one match found:\n{matches}")
        return None
    return matches[0]


def box_is_sliced(box: BBox,
                  vertical_cut_locations: List[int] = None,
                  horizontal_cut_locations: List[int] = None) -> bool:
    """
    Returns true if the BBox is cut by the lines provided.
    :param box: A BBox with the BBox.bbox_format "labelme"
    :param vertical_cut_locations:
    :param horizontal_cut_locations:
    :return:
    """
    if not box.format_is_labelme():
        box.to_labelme()

    [TLx, TLy], [BRx, BRy] = box.bbox
    # Check for vertical cuts:
    for vcut in vertical_cut_locations:
        if TLx < vcut < BRx:
            return True
    # Check for horizontal cuts:
    for hcut in horizontal_cut_locations:
        if TLy < hcut < BRy:
            return True
    # If none of the above triggered:
    return False


def cvt_labelme_bbox_to_shape_dict(box: BBox) -> dict:
    """
    Transforms a BBox with the BBox.bbox_format "labelme" to a dict as used in the "shapes" list as used in a json
    anotation file created by labelme.
    :param box: BBox (using BBox.bbox_format "labelme"
    :return: dict with the keys ["label", "line_color", "fill_color", "points", "shape_type", "flags"]
    """
    if not box.format_is_labelme():
        raise BoxFormatError
    _shape = {"label": box.material,
              "line_color": None,
              "fill_color": None,
              "points": box.bbox,
              "shape_type": "rectangle",
              "flags": {}}
    return _shape


def count_yolo_annotations(fdir, yolo_formatted_subdirs=False) -> int:
    """
    Counts all annotations in the folder and sub folders. Annotation format: yolo txt files. (Maybe make this flexible)
    """

    total_annotations = 0
    processed_files = 0
    for root, fdirs, files in os.walk(fdir):
        txt_files = []
        if yolo_formatted_subdirs:
            if os.path.split(root)[-1] in ['train', 'test', 'valid']:
                txt_files = [file for file in files if file.endswith(".txt")]
        else:
            txt_files = [file for file in files if file.endswith(".txt")]

        if txt_files:
            for txt_file in txt_files:
                txt_filepath = os.path.join(root, txt_file)
                logging.info(f"Reading annotations from file: {txt_filepath}")
                with open(txt_filepath, 'r') as f:
                    annotation_lines = f.readlines()
                if annotation_lines:  # i.e. if there are annotations in the image.
                    # ToDo: regex the lines to see if the .txt file was actually a yolo annotation?
                    total_annotations += len(annotation_lines)
                processed_files += 1
    logging.info(f"{processed_files} annotations files processed.")
    return total_annotations


def create_coco_materials_dicts(materials_dict: dict) -> List[dict]:
    """
    Creates a list of material dicts as used in coco annotation files.

    :param materials_dict: materials dict {index: material_name}
    :return:
    """
    coco_materials = []
    for index, material in materials_dict.items():
        coco_materials.append({"id": index,
                               "name": material,
                               "supercategory": material,
                               })
    return coco_materials


def cvt_df_coco_bbox_annotations_to_yolo(annotations_df: pd.DataFrame):
    """
    Converts annotations in a dataframe from coco to yolo style.
    :param annotations_df: Needs columns 'bbox', 'img_width', 'img_height'
    :return:
    """
    yolo_boxes = []
    for i, line in annotations_df.iterrows():
        _coco_bbox = line['bbox']
        _img_width, _img_height = line['img_width'], line['img_height']
        _yolo_bbox = bbox_conversions.coco_to_yolo(_coco_bbox, _img_width, _img_height)
        yolo_boxes.append(_yolo_bbox)
    annotations_df['yolo_bbox'] = yolo_boxes
    return annotations_df


def copy_image_files(img_source_dir: str, target_dirs: dict, annotations_df: pd.DataFrame):
    """
    Copies images according to a dictionary that contains target directories (for train, val and test), and an
    annotations_df dataframe that has info on which image belong to which set.
    ToDo: Now, "file_name" actually means "image_name". Change this so that it works on a name w/o exts.
    :param img_source_dir:
    :param target_dirs: dict: {'images':{<sets>: <setpath>}
    :param annotations_df: requires columns 'file_name', 'set'.
    :return:
    """
    print("Copying img files...")
    annotations_df_reduced = annotations_df.drop_duplicates(subset='file_name')
    assert len(annotations_df_reduced['file_name']) == \
           len(set(annotations_df['file_name'])) == \
           len(set(annotations_df_reduced['file_name']))
    i = 0
    for i, _img_name in enumerate(annotations_df_reduced['img_name']):
        _current_set = annotations_df_reduced.loc[annotations_df_reduced['img_name'] == _img_name, 'set'].values[0]
        logging.debug(f"{i}: {_img_name}:\t{_current_set}")
        _source_path = os.path.join(img_source_dir, _img_name)
        _target_path = os.path.join(target_dirs['images'][_current_set], _img_name)
        logging.debug(f'Copying {_img_name} from {_source_path} to {_target_path}')
        shutil.copyfile(_source_path, _target_path)
    logging.info(f'Copied {i + 1} images.')
    print('Done copying.')


def copy_yolo_files(source_dir: str, target_dirs: dict, annotations_df: pd.DataFrame):
    print("Copying img files...")
    annotations_df_reduced = annotations_df.drop_duplicates(subset='file_name')
    assert len(annotations_df_reduced['file_name']) == \
           len(set(annotations_df['file_name'])) == \
           len(set(annotations_df_reduced['file_name']))
    i = 0
    for i, _img_name in enumerate(annotations_df_reduced['img_name']):
        _current_set = annotations_df_reduced.loc[annotations_df_reduced['img_name'] == _img_name, 'set'].values[0]
        logging.debug(f"{i}: {_img_name}:\t{_current_set}")
        _source_path = os.path.join(source_dir, _img_name)
        _target_path = os.path.join(target_dirs['images'][_current_set], _img_name)
        logging.debug(f'Copying {_img_name} from {_source_path} to {_target_path}')
        shutil.copyfile(_source_path, _target_path)
    logging.info(f'Copied {i + 1} images.')
    print('Done copying.')


def create_yolo_annotation_line(category_id_no: int, bbox: List[float]):
    """
    Takes a cateogry id and yolo-formatted bbox coordinates and returns a string to be used in the annotation file.
    :param category_id_no:
    :param bbox: [x_center_normalised, y_center_normalised, box_width_normalised, box_height_normalised]
    :return:
    """
    logging.debug(category_id_no)
    logging.debug(bbox)

    category_id = str(category_id_no)
    _bbox_annotation = category_id
    for boxval in bbox:
        _bbox_annotation = ' '.join([_bbox_annotation, str(boxval)])
    return _bbox_annotation


def create_fallback_yolo_materials_dict(yolo_root_dir) -> dict:
    """
    Creates a unidirectional materials dict: {i: str}
    :param yolo_root_dir:
    :return:
    """
    materials_dict = {}
    unique_material_ids = get_material_ids_from_yolo_ds(yolo_root_dir)
    for i in unique_material_ids:
        materials_dict[int(i)] = "unspecified_" + str(i)
    return materials_dict


def create_materials_dict(materials: List[str], flip=False) -> dict:
    """
    Takes a materials list and returns a dictionary with an index for each unique material: {material: index}
    :param materials:
    :param flip: Flip the dict from {i: material} format to {material: i} format.
    :return:
    """
    mats_dict = {0: materials[0]}
    if len(materials) > 1:
        for mat in materials[1:]:
            if mat not in mats_dict.values():
                mat_id = max(mats_dict.keys()) + 1
                mats_dict[mat_id] = mat

    if flip:
        mats_dict = {v: k for k, v in mats_dict.items()}
    return mats_dict


def create_yolo_directories(target_directory: str) -> dict:
    """
    Creates the target directory, with subfolders according to yolo requirements. Also creates a "..._testing" folder in
    the parent directory.
    :param target_directory: str
    :return: dictionary with target directory paths
    """
    path_img_train = os.path.join(target_directory, 'images/train')
    path_img_val = os.path.join(target_directory, 'images/valid')
    path_img_test = os.path.join(target_directory, 'images/test')

    path_labels_train = os.path.join(target_directory, 'labels/train')
    path_labels_val = os.path.join(target_directory, 'labels/valid')
    path_labels_test = os.path.join(target_directory, 'labels/test')
    try:
        os.mkdir(target_directory)
        os.makedirs(path_img_train)
        os.makedirs(path_img_val)
        os.makedirs(path_img_test)
        os.makedirs(path_labels_train)
        os.makedirs(path_labels_val)
        os.makedirs(path_labels_test)
        print('Created directories.')
    except FileExistsError:
        raise FileExistsError('One or more target directories already exist.')
    else:
        directories = {'images': {'train': path_img_train,
                                  'val': path_img_val,
                                  'test': path_img_test},
                       'labels': {'train': path_labels_train,
                                  'val': path_labels_val,
                                  'test': path_labels_test}}
        return directories


def encode_img_for_labelme(img_fpath):
    """
    Encodes an image into a string using io.BytesIO and base64 encoding as in labelme:
    https://github.com/wkentaro/labelme.
    :param img_fpath:
    :return:
    """
    image_pil = Image.open(img_fpath)
    with io.BytesIO() as f:
        image_pil.save(f, format="PNG")
        f.seek(0)
        img_data = f.read()
    encoded_img = base64.b64encode(img_data).decode("utf-8")
    logging.debug(f"Encoded img has type {type(encoded_img)}")
    return encoded_img


def get_all_fpaths_by_extension(root_fdir: str, exts: Tuple[str, ...], recursive=True) -> List[str]:
    """
    Recursively extracts all file paths to files ending with the given extension down the folder hierarchy (i.e. it
    includes subfolders).
    :param root_fdir: str. Root directory from where to start searching
    :param exts: Tuple of extension strings. e.g. (".txt", "WAV")
    :param recursive:
    :return: sorted list of file paths
    """
    exts = (ext.lower() for ext in exts)
    # Make sure they have a preceding period
    exts = tuple([ext if ext.startswith(".") else "." + ext for ext in exts])
    if recursive:
        file_paths = [str(path) for path in Path(root_fdir).rglob('*') if path.suffix.lower() in exts]
    else:
        file_paths = [os.path.join(root_fdir, fname) for fname in sorted(os.listdir(root_fdir)) if fname.endswith(exts)]
    return sorted(file_paths)


def get_paths_to_txt_files(fdir) -> List[str]:
    """
    Returns a list of the paths to all annotation files in the dataset (assumes a yolo-structured dataset).
    :param fdir: Base dir of a yolo dataset.
    :return: list of paths
    """
    return get_all_fpaths_by_extension(fdir, ("txt",))


def get_annotation_from_line(line: str):
    """
    Extract a list with the bbox coordinates from a yolo line.
    Yolo annotation structure: "class renter_rel_x center_rel_y rel_width rel_height confidence"
    Note that confidence is optional. It might be there or not, depending on whether it is a ground truth or inference
    box.
    Example: "0 0.7222 0.234 0.12 0.17" (without confidence)
    Example: "0 0.7222 0.234 0.12 0.17 0.8104" (with confidence)
    :param line:
    :return:
    """
    pattern = re.compile(r'(^\d+) (\d\.\d+) (\d\.\d+) (\d\.\d+) (\d\.\d+)( \d\.\d+)?')
    try:
        matches = list(pattern.findall(line)[0])
    except IndexError:
        print(f'No annotations found in line {line}')
        return None
    else:
        # Remove last element if empty (the confidence value):
        if not matches[5]:
            matches = matches[:-1]

        matches = [float(elem) for elem in matches]
        matches[0] = int(matches[0])
    return matches


def get_bboxes_from_labelme_json(fpath_json: str) -> List[BBox]:
    """
    Assumes that the json is in labelme_format.
    :param fpath_json:
    :return:
    """
    json_content = load_json(fpath_json)
    img_name = json_content['imagePath']
    img_width = json_content["imageWidth"]
    img_height = json_content["imageHeight"]
    _json_dir = os.path.split(fpath_json)[0]
    img_path = os.path.join(_json_dir, img_name)
    bboxes = []
    if json_content["shapes"]:  # If there ARE boxes in the json:
        for annotation in json_content['shapes']:
            if annotation['shape_type'] == 'rectangle':
                point_0, point_1 = np.array(annotation['points'][0]), np.array(annotation['points'][1])
                # Correct for possibly wrong order of points (because labelme creates them in "click order")
                if np.all(point_0 > point_1):  # i.e. if first point is bottom-right, not top-left
                    point_0, point_1 = point_1, point_0
                box_coords = [list(point_0), list(point_1)]
                bbox = BBox(bbox=box_coords,
                            material=annotation["label"],
                            bbox_format="labelme",
                            img_width=img_width,
                            img_height=img_height,
                            img_fpath=img_path)
                logging.debug(type(bbox))
                bboxes.append(bbox)
    return bboxes


def get_materials_from_labelme_jsons(json_fdir, recursive=True) -> List[str]:
    """Returns a list (with duplicates) of all the materials found in the json files in the target dir."""
    json_files = get_all_fpaths_by_extension(json_fdir, ("json",), recursive=recursive)
    materials = []
    for json_path in json_files:
        json_data = load_json(json_path)
        file = json_data['imagePath']
        for bbox in json_data['shapes']:
            material = bbox.get('label')
            logging.debug(f"{file}: {material}")
            if material is not None:
                materials.append(material.lower())
    return materials


def get_materials_dict_from_labelme_jsons(json_fdir, recursive=True, sorted_output=True) -> dict:
    """
    Returns a dict of all the materials found in the json files in the target dir.
    :param json_fdir:
    :param recursive:
    :return: dict. {index: material}
    """
    materials_dict = None
    materials = get_materials_from_labelme_jsons(json_fdir, recursive=recursive)
    if materials:
        materials_dict = {0: materials[0]}
        if len(materials) > 1:
            for mat in materials[1:]:
                if mat not in materials_dict.values():
                    mat_i = max(materials_dict.keys()) + 1
                    materials_dict[mat_i] = mat
    if sorted_output:
        materials_dict = {k: v for k, v in sorted(materials_dict.items(), key=lambda x: x[1])}
    return materials_dict


def get_materials_dict_from_coco_json(fpath_json) -> dict:
    annotations = load_json(fpath_json)
    materials = annotations["categories"]
    materials_dict = {mat["id"]: mat["name"] for mat in materials}
    return materials_dict


def get_material_ids_from_yolo_ds(yolo_root_fdir) -> list:
    """
    Recursively extracts the material ids from txt files in a yolo-structured folder.
    :param yolo_root_fdir:
    :return:
    """
    fpaths = get_all_fpaths_by_extension(yolo_root_fdir, (".txt",))
    ids = []
    for fpath in fpaths:
        with open(fpath, 'r') as f:
            lines = f.readlines()
        for line in lines:
            current_id = line.split(" ")[0]
            if current_id not in ids:
                ids.append(current_id)
    return ids


def get_bg_img(fpath_annotations_json: str, img_dir: str):
    # ToDo: Make this take a json path or a pd.df?
    """Takes a COCO style json and checks for images which are not part of the json dataset."""
    annotation_data = load_json(fpath_annotations_json)
    img_info = pd.DataFrame({'id': [img['id'] for img in annotation_data['images']],
                             'img_name': [img['file_name'] for img in annotation_data['images']]})
    img_files = [file for file in os.listdir(img_dir) if not file.startswith('.')]
    assert set(img_info['img_name']) == set(img_files)
    bg_imgs = []
    for img in img_files:
        if img not in img_info['img_name'].values:
            bg_imgs.append(img)
    return bg_imgs


def get_max_annotation_count(fdir_annotations) -> int:
    """
    Returns the maximum number of annotations per image found among all the annotations files.
    :param fdir_annotations: Path to directory containing yolo-style annotation txt files.
    :return: int. Maximum number of annotations found per image.
    """
    max_n_annot = 0
    filepaths = sorted(os.listdir(fdir_annotations))
    filepaths = [path for path in filepaths if path.endswith(".txt")]
    # filepaths = sorted(glob.glob(fdir_annotations, "*.txt"))
    for path in filepaths:
        with open(path, "r") as f:
            lines = f.readlines()
        if len(lines) > max_n_annot:
            max_n_annot = len(lines)
    return max_n_annot


def get_basename_only(fpath) -> str:
    """
    Strips off the path and the file extension.
    :param fpath:
    :return:
    """
    fname = os.path.split(fpath)[-1]
    fname = os.path.splitext(fname)[0]
    return fname


def list_image_names(img_dir: str) -> List[str]:
    """Returns a (sorted) list of filenames of images in a folder that can be opened by PIL.Image.open(). Note that
    they might be of various filetypes. Ignores files that can not be opened by PIL.Image.open()."""
    _files = sorted(os.listdir(img_dir))
    images = []
    for _fname_img in _files:
        try:
            _ = Image.open(os.path.join(img_dir, _fname_img))
        except UnidentifiedImageError:
            logging.info(f'{_fname_img} is not a readable image.')
        else:
            images.append(_fname_img)
    return images


def list_json_names(fdir: str) -> List[str]:
    """
    Returns an ordered list of all the json filenames in dfir.
    :param fdir:
    :return:
    """
    json_fnames = [file for file in sorted(os.listdir(fdir)) if file.endswith('.json')]
    assert len(json_fnames) == len(set(json_fnames))  # Make sure fnames are unique.
    return json_fnames


def load_coco_ds(fpath_coco_json: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Takes path to the root directory of a COCO-style data set, then extracts info from the annotations.json file in the
    <annotations> subfolder     and returns two pandas data frames, one with info on images, one with the annotations.
    :param fpath_coco_json:
    :return: (pd.DataFrame, pd.DataFrame)
    """
    json_data = load_json(fpath_coco_json)
    images = pd.DataFrame(json_data['images'])
    annotations = pd.DataFrame(json_data['annotations'])
    return images, annotations


def load_json(json_fpath: str) -> dict:
    """Returns json data as a dict."""
    with open(json_fpath, 'r') as f:
        data = json.load(f)
    logging.debug(f'Loaded json object (type): {type(data)}')
    return data


def load_yolo_annotations_as_BBoxes(fpath_annotations_txt: str, img_fpath: str, materials_dict) -> List[BBox]:
    """
    Loads annotations from a yolo annotation txt file
    :param fpath_annotations_txt:
    :param img_fpath:
    :param materials_dict: {index: material_str}, example: {0: "plastic"}
    :return:
    """
    # ToDo: add lat/lon attribute and set them up during init.
    # Initiate bboxes and deal with possibly missing materials dict.
    bboxes = []
    # Open image and get dimensions
    img_dims_wh = (0, 0)
    try:
        img = Image.open(img_fpath)
    except FileNotFoundError:
        print(f"No file found at location {img_fpath}")
    except UnidentifiedImageError:
        print(f"Could not open file as an image: {img_fpath}")
    else:
        img_dims_wh = img.size
    # Load the annotations (i.e. BBoxes)
    confidence = None
    try:
        with open(fpath_annotations_txt, 'r') as f:
            annotations_raw = f.readlines()
    except FileNotFoundError:
        print(f"No annotation file found at: f{fpath_annotations_txt}")
    else:
        if annotations_raw:  # if there are any lines in the file
            for line in annotations_raw:
                logging.debug(type(line))
                logging.debug(line)
                current_box = get_annotation_from_line(line)
                material_index = int(current_box[0])
                current_bbox_coords = [float(num) for num in current_box[1:5]]  # inclusive:exclusive indexing
                assert len(current_bbox_coords) == 4
                print(current_bbox_coords)
                if len(current_box) == 6:
                    confidence = current_box[5]
                current_box_mat = materials_dict[material_index]
                bboxes.append(BBox(current_bbox_coords, current_box_mat, "yolo",
                                   img_width=img_dims_wh[0], img_height=img_dims_wh[1], img_fpath=img_fpath,
                                   confidence=confidence))
    logging.info(f"Successfully loaded annotations file {fpath_annotations_txt}")
    return bboxes


def load_yolo_annotation_only(fpath_annotations_file) -> List[dict]:
    """
    Loads only the annotation part and returns the file name, the box, material i and the confidence (if available)
    """
    with open(fpath_annotations_file, "r") as f:
        lines = f.readlines()
    file_name = os.path.split(fpath_annotations_file)[-1]
    logging.debug(file_name)
    lines_dict_list = []
    for line in lines:
        mat_i, cx, cy, w, h, *c = [float(e) for e in line.strip().split(" ")]  # *c: possible conf. value
        current_annotation = {"file_name": file_name, "bbox": [cx, cy, w, h], "material_i": int(mat_i)}
        if c:  # if there is a confidence value
            current_annotation["confidence"] = c[0]
        lines_dict_list.append(current_annotation)
    return lines_dict_list


def load_all_yolo_annotations_only(fdir_annotations):
    files = [os.path.join(fdir_annotations, fname) for fname in os.listdir(fdir_annotations)
             if fname.lower().endswith(".txt")]
    files = natsort.natsorted(files)
    all_dicts = []
    for fpath in files:
        all_dicts.extend(load_yolo_annotation_only(fpath))
    return all_dicts


def merge_img_info_into_labels(images: pd.DataFrame, labels: pd.DataFrame):
    """
    Used in converting coco ds to yolo. Not for converting labelme to yolo.
    :param images:
    :param labels:
    :return:
    """
    assert images.shape[0] == len(images['file_name'].unique())
    logging.info('Images data frame has one image per row.')
    for i, line in images.iterrows():
        _img_id = line["id"]
        _current_fname = line['file_name']
        _current_width = line['width']
        _current_height = line['height']

        labels.loc[labels['image_id'] == _img_id, 'file_name'] = _current_fname
        labels.loc[labels['image_id'] == _img_id, 'img_width'] = _current_width
        labels.loc[labels['image_id'] == _img_id, 'img_height'] = _current_height
    return labels


def point_within_limits(point_xy: Tuple[int, int], xmin: int, xmax: int, ymin: int, ymax: int) -> bool:
    """
    Checks whether a point lies within (or on) limits.
    Inclusive. If points lies ON the limit, is is still considered within.
    :param point_xy:
    :param xmin:
    :param xmax:
    :param ymin:
    :param ymax:
    :return:
    """
    ptx, pty = point_xy
    if xmin <= ptx <= xmax and ymin <= pty <= ymax:
        return True
    return False


def save_readable_json(fpath_json, fpath_output: str = None) -> None:
    """Takes an existing json and saves it as a neatly formatted json."""
    if fpath_output is None:
        tstamp = format(datetime.datetime.now(), '%Y_%m_%d-%H%M')
        fpath_output = '/home/findux/Desktop/readable_json_' + tstamp + '.json'
    json_data = load_json(fpath_json)
    with open(fpath_output, 'w') as f:
        json.dump(json_data, f, indent=4)


def make_json_readable(fpath_json, overwrite=True) -> None:
    """Overwrites an already existing json with a neatly formatted version of itself, or (if overwrite is set to false,
    creates a new file with a timestamp in the file name in the same location)"""
    json_data = load_json(fpath_json)
    file_out = fpath_json
    if not overwrite:
        tstamp = format(datetime.datetime.now(), '%Y_%m_%d-%H%M')
        file_out = fpath_json + tstamp + '.json'
    with open(file_out, 'w') as f:
        json.dump(json_data, f, indent=4)


def save_to_json(obj, out_path) -> None:
    """saves an object as a json file"""
    with open(out_path, "w") as f:
        json.dump(obj, f, indent=4)


def show_planned_cuts(fpath_img: str, vcut_locations: List[int], hcut_locations: List[int], fpath_annot: str = None):
    if fpath_annot is not None:
        visualize_single_img_annotations_yolo(fpath_img, fpath_annot)
    else:
        plt.imshow(Image.open(fpath_img))
    for vcut in vcut_locations:
        plt.axvline(x=vcut, color='white')
    for hcut in hcut_locations:
        plt.axhline(y=hcut, color='white')



def get_cut_locations(n_vertical_cuts, n_horz_cuts, img_dims_wh: Tuple[int, int]) -> Tuple[List[int], List[int]]:
    """
    Returns two lists, with the vertical and horizontal cut locations based on the number of cuts specified.
    :param n_vertical_cuts: int. Number of vertical cuts.
    :param n_horz_cuts: int. Number of horizontal cuts
    :param img_dims_wh: tuple. Image dimensions (width, height) in pixels.
    :return: Tuple([vertical cut locations], [horizontal cut locations])
    """
    img_width, img_height = img_dims_wh
    vertical_cut_locations = [int((img_width / (n_vertical_cuts + 1)) * (i + 1)) for i in range(n_vertical_cuts)]
    horizontal_cut_locations = [int((img_height / (n_horz_cuts + 1)) * (i + 1)) for i in range(n_horz_cuts)]
    return vertical_cut_locations, horizontal_cut_locations


def get_box_location(box: BBox, n_vcuts: int, n_hcuts: int) -> Tuple[int, int]:
    """
    Takes a labelme-formatted box and returns which quadrant the box is located in.
    :param box:
    :param n_vcuts:
    :param n_hcuts:
    :return:
    """
    if not box.format_is_labelme():
        box.to_labelme()
    vcuts, hcuts = get_cut_locations(n_vcuts, n_hcuts, box.img_dims_wh)
    assert not box_is_sliced(box, vcuts, hcuts)

    vcuts = [0] + vcuts + [box.img_dims_wh[0]]
    hcuts = [0] + hcuts + [box.img_dims_wh[1]]
    logging.info(f"Vertical cuts: {vcuts}")
    logging.info(f"Horizontal cuts: {hcuts}")

    col, row = None, None
    box_center = box.box_center_xy
    for v, vcut in enumerate(vcuts[:-1]):
        for h, hcut in enumerate(hcuts[:-1]):
            if point_within_limits(box_center, vcut, vcuts[v + 1], hcut, hcuts[h + 1]):
                col, row = v, h
    return row, col


def visualize_coco_annotations(coco_json_fpath: str):
    """
    Shows the images of a coco data set and the corresponding bounding boxes.
    :param coco_json_fpath:
    :return:
    """
    json_data = load_json(coco_json_fpath)
    images = json_data["images"]
    annotations = json_data["annotations"]

    for img_entry in images:
        img_path = img_entry["file_name"]
        img_name = os.path.split(img_path)[-1]
        img_id = img_entry["id"]
        img = plt.imread(img_path)

        fig, ax = plt.subplots()
        ax.imshow(img)

        annotation_count = 0
        for annotation in annotations:
            if annotation["image_id"] == img_id:
                bbox = annotation["bbox"]
                logging.debug(f"Bbox: {bbox}")
                rect = patches.Rectangle(bbox[:2], bbox[2], bbox[3], color='red',
                                         fill=None)  # Rectangle(xy, width, height, ...)
                ax.add_patch(rect)
                annotation_count += 1

        print_text = f'{img_name}  |  Img. ID: {img_id}  |  Annotations: {annotation_count}'
        plt.text(0, -30, print_text)
        fig.canvas.manager.full_screen_toggle()
        plt.show()


def update_all_labelme_materials(fpath_dir: str, old_material: str, new_material: str):
    """
    Updates all old materials in all labelme json files in the current directory to new material.
    WARNING: All json files in the directory must be labelme_json_files.
    :param fpath_dir:
    :param old_material:
    :param new_material:
    :return:
    """
    print("Updating labelme materials...")
    json_fpaths = get_all_fpaths_by_extension(fpath_dir, (".json",))
    for json_fpath in json_fpaths:
        logging.info(f"Processing file {os.path.split(json_fpath)[1]}")
        update_material_in_labelme_file(json_fpath, old_material, new_material)


def update_material_in_labelme_file(json_fpath: str, old_mat: str, new_mat: str) -> bool:
    """
    Updates the annotations in a given json file and replaces the old material with the new one.
    """
    img_annotations = load_json(json_fpath)
    file_changed = False
    for bbox in img_annotations["shapes"]:
        if bbox["label"] == old_mat:
            bbox["label"] = new_mat
            file_changed = True

    if file_changed:
        print(f"Updated {old_mat} to {new_mat} in {json_fpath}")
        with open(json_fpath, "w") as f:
            f.write(json.dumps(img_annotations, indent=2))
    return file_changed


def remove_material_annotations_from_labelme_files(fdir, material_to_remove):
    json_fpaths = get_all_fpaths_by_extension(fdir, ("json",))
    for fpath_json in json_fpaths:
        file_changed = False
        annotations = load_json(fpath_json)
        shapes_to_keep = []
        for annotation in annotations["shapes"]:
            if annotation["label"] == material_to_remove:
                file_changed = True
            else:
                shapes_to_keep.append(annotation)
        if file_changed:
            annotations["shapes"] = shapes_to_keep
            with open(fpath_json, "w") as f:
                f.write(json.dumps(annotations, indent=2))


def overwrite_all_labelme_materials_with_one(fdir_root: str, material: str):
    """
    Applies the given material to all objects, removing any classes.
    :param fdir_root:
    :param material:
    :return:
    """
    json_paths = get_all_fpaths_by_extension(fdir_root, (".json",))
    for fpath in json_paths:
        annotation = load_labelme_annotation_file(fpath)
        for bbox in annotation.shapes:
            bbox.material = material
        annotation.to_json(overwrite=True)


def visualize_single_img_annotations_coco(img_name: str, img_dir: str, annotations_df: pd.DataFrame,
                                          prefix_text: str = ""):
    """Shows the annotation boxes"""
    _img_annotations = annotations_df
    _img_annotations["basename"] = [os.path.split(line["file_name"])[0] for i, line in _img_annotations.iterrows()]
    _img_annotations = annotations_df.loc[annotations_df['basename'] == img_name, :]
    logging.debug(_img_annotations)
    _annotation_count = _img_annotations.shape[0]
    _current_id = _img_annotations['image_id'].unique()
    try:
        _img = Image.open(os.path.join(img_dir, img_name))
    except FileNotFoundError:
        print(f'Image {img_name} not found in {img_dir}. Did you use uppercase where necessary?')
    else:
        _fig, _ax = plt.subplots()
        _ax.imshow(_img)
        for _, _line in _img_annotations.iterrows():
            _bbox = _line['bbox']
            _rect = patches.Rectangle(_bbox[:2], _bbox[2], _bbox[3], color='red', fill=None)
            _ax.add_patch(_rect)

        print_text = prefix_text + f'  |  {img_name}  |  Img-ID: {_current_id}  |  Annotations: {_annotation_count}'
        plt.text(0, -30, print_text)
        _fig.canvas.manager.full_screen_toggle()
        plt.show()


def save_materials_dict(materials_dict: dict, fdir_dst: str, fname: str = "materials_dict.json"):
    with open(os.path.join(fdir_dst, fname), "w") as f:
        f.write(json.dumps(materials_dict, indent=2))


def visualize_yolo_predictions_and_ground_truths(fpath_img, fpath_gt_annotations, fpath_pred_annotations,
                                                 materials_dict=None, save_location=None, additional_text=""):
    """
    Displays a comparison of ground truths and predictions.
    :param fpath_img:
    :param fpath_gt_annotations:
    :param fpath_pred_annotations:
    :param materials_dict: {i: material_str}
    :param save_location: a directory
    :param additional_text:
    :return:
    """
    if materials_dict is None:
        materials_dict = {0: "unspecified"}
    # Read Image
    try:
        img = Image.open(fpath_img)
    except (FileNotFoundError, UnidentifiedImageError):
        print(f"Cannot open image at: {fpath_img}")
    else:
        img_name = os.path.split(fpath_img)[-1]
        img_width, img_height = img.size

        fig, ax = plt.subplots()
        ax.imshow(img)

        predictions = load_yolo_annotations_as_BBoxes(fpath_pred_annotations, fpath_img, materials_dict)
        for bbox in predictions:
            assert bbox.bbox_format == "yolo"
            coco_box = bbox_conversions.yolo_to_coco(bbox.bbox, img_width, img_height)
            box_patch = patches.Rectangle(coco_box[:2], coco_box[2], coco_box[3], color="red", fill=None, linewidth=1.5)
            confidence = bbox.confidence
            plt.text(coco_box[0], coco_box[1], s=f"{confidence:.2f} trash", c='white', va='bottom', size=10)
            ax.add_patch(box_patch)

        ground_truths = load_yolo_annotations_as_BBoxes(fpath_gt_annotations, fpath_img, materials_dict)
        for bbox in ground_truths:
            assert bbox.bbox_format == "yolo"
            coco_box = bbox_conversions.yolo_to_coco(bbox.bbox, img_width, img_height)
            box_patch = patches.Rectangle(coco_box[:2], coco_box[2], coco_box[3],
                                          facecolor=(188 / 255, 255 / 255, 20 / 255, 75 / 255),
                                          edgecolor=(188 / 255, 255 / 255, 20 / 255, 1))
            ax.add_patch(box_patch)

        print_text = f'{img_name} |  ' + additional_text
        plt.text(0, -30, print_text)
        if save_location:
            img_basename, ext = os.path.splitext(img_name)
            save_as = os.path.join(save_location, f"{img_basename}_comparison_yolo{ext}")
            plt.savefig(save_as, bbox_inches='tight', dpi=300)
        plt.show()


def visualize_single_img_annotations_yolo(fpath_img: str, color="red", materials_dict=None):
    """
    ToDo: Implement color palette per class
    :param fpath_img:
    :param color:
    :param materials_dict: {i: material}
    :return:
    """
    if materials_dict is None:
        materials_dict = {0: "trash"}

    img_base_name = os.path.split(fpath_img)[-1].split('.')[0]
    fpath_annotations = os.path.join(os.path.split(fpath_img)[0], img_base_name + ".txt")
    logging.debug(
        f"Showing {os.path.split(fpath_img)[-1]} with annotations from {os.path.split(fpath_annotations)[-1]}")
    try:
        img = Image.open(fpath_img)
    except (FileNotFoundError, UnidentifiedImageError):
        print(f"Cannot open image at: {fpath_img}")
    else:
        img_name = os.path.split(fpath_img)[-1]
        img_width, img_height = img.size
        bboxes = load_yolo_annotations_as_BBoxes(fpath_annotations, fpath_img, materials_dict)
        annotation_count = len(bboxes)
        fig, ax = plt.subplots()
        ax.imshow(img)

        for bbox in bboxes:
            assert bbox.bbox_format == "yolo"
            coco_box = bbox_conversions.yolo_to_coco(bbox.bbox, img_width, img_height)
            box_patch = patches.Rectangle(coco_box[:2], coco_box[2], coco_box[3], color=color, fill=None)
            ax.add_patch(box_patch)

        print_text = f'{img_name} |  Annotations: {annotation_count}'
        plt.text(0, -30, print_text)
        fig.canvas.manager.full_screen_toggle()


def visualize_all_yolo_annotations(fdir, materials_dict=None):
    """Assumes that images and txt files are in the same directory"""
    if materials_dict is None:
        materials_dict = create_fallback_yolo_materials_dict(fdir)
    img_paths = [os.path.join(fdir, img) for img in sorted(os.listdir(fdir)) if img.lower().endswith(YOLO_IMG_FORMATS)]
    for fpath in img_paths:
        print(fpath)
        visualize_single_img_annotations_yolo(fpath, materials_dict=materials_dict)
        plt.show()


# ToDo: after this: get predictions per obj (as a curve, with iou as x)
def cvt_yolo_annotations_to_coco_json(fdir_label_txts: str, fdir_imgs: str, fpath_dst: str, materials_dict: dict):
    txt_files = get_all_fpaths_by_extension(fdir_label_txts, (".txt",))
    img_files = get_all_fpaths_by_extension(fdir_imgs, YOLO_IMG_FORMATS)

    material_categories = [{"id": key, "name": value, "supercategory": value} for key, value in materials_dict.items()]
    print(material_categories)

    json_file = {"info": {"year": format(datetime.datetime.now(), "%Y"),
                          "version": None,
                          "description": f"COCO-version of the yolo labels in {fdir_label_txts}",
                          "contributor": None,
                          "url": None,
                          "date_created": format(datetime.datetime.now(), "%Y-%m-%d")},
                 "licences": [{"id": None,
                               "url": None,
                               "name": None}],
                 "categories": None}


if __name__ == '__main__':
    loglevel = logging.DEBUG
    logformat = "[%(levelname)s]\t%(funcName)15s: %(message)s"
    logging.basicConfig(level=loglevel, format=logformat)
    logging.disable()

    # fdir = "/media/findux/DATA/Documents/Malta_II/datasets/TACO_ORIG_SHAPED/"
    # save_to_json(list(get_materials_dict_from_labelme_jsons(fdir).values()),
    #              os.path.join("/media/findux/DATA/Documents/Malta_II/datasets/taco_classes.json"))

    print(count_yolo_annotations("/media/findux/DATA/Documents/Malta_II/datasets/dataset_01/labels/train/"))
    print(count_yolo_annotations("/media/findux/DATA/Documents/Malta_II/datasets/dataset_01/labels/valid/"))
    print(count_yolo_annotations("/media/findux/DATA/Documents/Malta_II/datasets/dataset_01/labels/test/"))
    print(count_yolo_annotations("/media/findux/DATA/Documents/Malta_II/datasets/dataset_02_mixed/"))
    print(count_yolo_annotations("/media/findux/DATA/Documents/Malta_II/datasets/dataset_04_gnejna_with_duplicates/labels/train/"))
    print(count_yolo_annotations("/media/findux/DATA/Documents/Malta_II/datasets/dataset_04_gnejna_with_duplicates/labels/valid/"))
    print(count_yolo_annotations("/media/findux/DATA/Documents/Malta_II/datasets/dataset_04_gnejna_with_duplicates/labels/test/"))