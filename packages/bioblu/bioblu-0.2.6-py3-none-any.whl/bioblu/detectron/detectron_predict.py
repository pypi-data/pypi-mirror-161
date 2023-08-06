#!/usr/bin/env python3
import datetime
import json

import cv2
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.structures import BoxMode
import logging
import numpy as np
import os
import torch
from typing import List, Tuple, Dict

from bioblu.main import IMG_FORMATS
from bioblu.detectron import detectron


def load_model(fpath_model, use_cpu=True) -> dict:
    device_params = {}
    if use_cpu:
        device_params["map_location"] = torch.device('cpu')
    try:
        model = torch.load(fpath_model, **device_params)
    except FileNotFoundError:
        raise FileNotFoundError(f"Model not found: {fpath_model}")
    else:
        return model


def create_img_dict(fpath_img, inference_output_dims_wh: Tuple[int, int] = None) -> Dict:
    assert fpath_img.lower().endswith(IMG_FORMATS)
    _, img_name = os.path.split(fpath_img)
    img = np.array(cv2.imread(fpath_img))
    img_CHW = np.transpose(img, (2, 0, 1))  # Transpose from H, W, C to C, H, W
    img_tensor = torch.tensor(img_CHW)
    logging.debug(f"Loaded image {img_name} as tensor with shape {img_tensor.shape}")

    if inference_output_dims_wh is None:
        channels, img_height, img_width = tuple(img_tensor.shape)
    else:
        assert len(inference_output_dims_wh) == 2
        channels, (img_height, img_width) = 3, inference_output_dims_wh

    out_dict = {"image": img_tensor,
                "img_name": img_name,
                "height": img_height,
                "width": img_width}
    return out_dict


def load_previous_cfg(model_results_dir: str, use_cpu: bool = True, roi_heads_score_test_thresh: float = 0.6,
                      color_mode: str = "BGR"):
    cfg = get_cfg()
    _model_path = os.path.join(model_results_dir, "model_final.pth")
    _cfg_path = os.path.join(model_results_dir, "cfg.yaml")

    cfg.merge_from_file(_cfg_path)

    cfg.INPUT.FORMAT = color_mode.upper()
    cfg.MODEL.WEIGHTS = _model_path
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = roi_heads_score_test_thresh
    cfg.MODEL.DEVICE = "cpu" if use_cpu else "cuda"
    return cfg


def create_predictions_dir(fdir_predictions):
    try:
        os.makedirs(fdir_predictions)
    except FileExistsError:
        raise FileExistsError(f"Predictions output directory already exists: {fdir_predictions}")
    else:
        logging.info(f"Created output dir. {fdir_predictions}")


def load_imgs(fdir, inference_output_dims_wh=None) -> List[dict]:
    """
    Loads all images from one folder into a List[dict]. Can require a lot of memory.
    :param fdir:
    :param inference_output_dims_wh:
    :return:
    """
    files = sorted(os.listdir(fdir))
    imgs = []
    for file in files:
        if file.lower().endswith(IMG_FORMATS):
            img_fpath = os.path.join(fdir, file)
            logging.debug(f"Loading img. {img_fpath}")
            imgs.append(create_img_dict(img_fpath, inference_output_dims_wh))
        else:
            logging.info(f"Skipped  loading img '{file}' because format is not among {IMG_FORMATS}.")
    return imgs


def predict_single_img(fpath_img, model_dir, materials_dict,
                       roi_heads_score_test_thresh=0.6,
                       roi_heads_nms_thresh=0.7,
                       inference_output_dims_wh=None, use_cpu=True,
                       color_mode="RGB"):
    # Create input dict
    input_img = create_img_dict(fpath_img)
    # Load cfg
    cfg = load_previous_cfg(model_dir, use_cpu=use_cpu, roi_heads_score_test_thresh=roi_heads_score_test_thresh, color_mode=color_mode)
    cfg.MODEL.ROI_HEADS.NMS_THRESH_TEST = roi_heads_nms_thresh
    # Run prediction
    predictor = DefaultPredictor(cfg)
    result = predictor.model([input_img])[0]
    # Add some more info to the result:
    result["img_name"] = os.path.split(fpath_img)[-1]
    result["img_fpath"] = fpath_img
    result["materials_dict"] = materials_dict
    result["cfg"] = cfg  # Might be a bit overkill to add this to each result.
    return result


def predict_multiple_imgs(fdir_imgs: str, fdir_model: str, materials_dict: dict = None, save_predictions=True, save_visualisations=False,
                          roi_heads_score_test_thresh=0.6, roi_heads_nms_thresh=0.7,
                          use_cpu=True, color_mode="RGB", output_style: str = "coco"):
    if not output_style.lower() in ["coco", "detectron"]:
        print(f"Invalid output style {output_style}. Deafaulting to coco.")

    if materials_dict is None:
        materials_dict = {0: "trash"}
    if save_predictions or save_visualisations:
        fdir_predictions_out = f"{fdir_imgs}/predictions_{format(datetime.datetime.now(), '%Y-%m-%d_%H%M')}"
        os.makedirs(fdir_predictions_out)
        logging.info(f"Output dir created: {fdir_predictions_out}")

    input_img_paths = [os.path.join(fdir_imgs, path) for path in
                       sorted(os.listdir(fdir_imgs)) if path.lower().endswith(IMG_FORMATS)]

    # Load model & create predictor
    cfg = load_previous_cfg(fdir_model, use_cpu=use_cpu, roi_heads_score_test_thresh=roi_heads_score_test_thresh,
                            color_mode=color_mode)
    cfg.MODEL.ROI_HEADS.NMS_THRESH_TEST = roi_heads_nms_thresh

    predictor = DefaultPredictor(cfg)

    if output_style.lower() == "coco":
        predictions = {"info": {"description": f"Inferences on images in {fdir_imgs} using model in {fdir_model}"},
                       "images": [],
                       "annotations": [],
                       "categories": [{"id": key, "name": value, "supercategory": value} for key, value in materials_dict.items()]}

        for i, img_path in enumerate(input_img_paths):

            img_name = os.path.split(img_path)[-1]
            logging.info(f"Processing image {img_name}")
            img = cv2.imread(img_path)

            # Update the img info
            current_img_info = {"id": i,
                                "file_name": img_path}
            current_img_info["height"], current_img_info["width"], _ = img.shape
            predictions["images"].append(current_img_info)

            # Predict and serialize results
            img_results = predictor(img)
            print(img_results)
            img_results_s = detectron.serialize_instance(img_results)  # ToDo:maybe skip this detour
            print(img_results_s)
            # Update the predictions
            for j, (bbox, bbox_center, score, category_id) in enumerate(zip(img_results_s["instances"]["pred_boxes"],
                                                                            img_results_s["instances"]["box_centers"],
                                                                            img_results_s["instances"]["scores"],
                                                                            img_results_s["instances"]["pred_classes"])):
                current_img_pred = {"id": j,
                                    "image_id": i,
                                    "file_name": img_path,
                                    "segmentation": [], "area": None, "iscrowd": 0,
                                    "bbox": bbox,
                                    "bbox_center": bbox_center,
                                    "category_id": category_id,
                                    "score": score,
                                    "bbox_mode": BoxMode.XYXY_ABS}
                predictions["annotations"].append(current_img_pred)

            if save_visualisations:
                print(f"Saving prediction visualisations to: {fdir_predictions_out}")
                img_pred_name = os.path.join(fdir_predictions_out, img_name.split(".")[0] + "_prediction.png")
                logging.debug(f"Save prediction img as {img_pred_name}")
                detectron.visualize_detectron_prediction(img_results_s, materials_dict, save_as=img_pred_name, show_img=False,
                                                         color_mode=color_mode)
    else:
        predictions = []
        for i, img_path in enumerate(input_img_paths):
            img_name = os.path.split(img_path)[-1]
            logging.info(f"Processing image {img_name}")
            img = cv2.imread(img_path)
            img_results_s = predictor(img)
            print(img_results_s)
            logging.info(f"Prediction: {detectron.serialize_instance(img_results_s)}")
            img_results_s["img_name"] = img_name
            img_results_s["img_fpath"] = img_path
            img_results_s["materials_dict"] = materials_dict
            if save_visualisations:
                img_pred_name = os.path.join(fdir_predictions_out, img_name.split(".")[0] + "_prediction.png")
                logging.debug(f"Save prediction img as {img_pred_name}")
                detectron.visualize_detectron_prediction(img_results_s, save_as=img_pred_name, show_img=False, color_mode=color_mode)
            predictions.append(img_results_s)
        predictions = [detectron.serialize_instance(inst) for inst in predictions]  # Makes them "saveable"

    if save_predictions:
        with open(os.path.join(fdir_predictions_out, "predictions.json"), "w") as f:
            f.write(json.dumps(predictions, indent=4))

    return predictions


if __name__ == "__main__":

    # ToDo: add model to prediction result dict

    print(f"torch: {torch.__version__}")
    os.environ["LRU_CACHE_CAPACITY"] = "1"  # fix memory leak according to https://github.com/pytorch/pytorch/issues/29893

    loglvl = logging.INFO
    logformat = "[%(levelname)s]\t%(funcName)15s: %(message)s"
    logging.basicConfig(level=loglvl, format=logformat)

    # fdir_model = "/media/findux/DATA/Documents/Malta_II/results/5239_2022-05-07_052041/"
    # imgs_fdir = "/home/findux/Desktop/tmp/gnejna_test_paradise_model/"
    # imgs_fdir = "/home/findux/Desktop/nonsquare_test/"
    # fpath_img = "/home/findux/Desktop/tmp/gnejna_test_paradise_model/Gnejna_DJI_0737_0-1.tif"
    # # predict_multiple_imgs(imgs_fdir, fdir_model, materials_dict={0: "trash"}, save_predictions=True, save_visualisations=True)
    # # pred = predict_single_img(fpath_img=fpath_img, model_dir=fdir_model, materials_dict={0: "trash"})
    # pred = predict_multiple_imgs(imgs_fdir, fdir_model, {0: "trash"}, save_predictions=True, save_visualisations=True)
    # print(pred)
    # pred = predict_multiple_imgs(imgs_fdir, fdir_model, {0: "trash"})

    # prediction_dict = detectron.serialize_instance(pred)
    # with open("/home/findux/Desktop/test.json", 'w') as f:
    #     f.write(json.dumps(prediction_dict, indent=4))

    # imgs_fdir = "/media/findux/DATA/Documents/Malta_II/datasets/cecilia_martin/selection/non-empties/test/"
    # fdir_model = "/media/findux/DATA/Documents/Malta_II/results/5763_2022-05-26_183938/"
    # predict_multiple_imgs(imgs_fdir, fdir_model, {0: "trash"}, save_predictions=True, save_visualisations=True)

    imgs_fdir = "/media/findux/DATA/Documents/Malta_II/2022-06-21_catania_update/test_images/images_yolo_detectron/test/"
    fdir_model = "/media/findux/DATA/Documents/Malta_II/results/5343_2022-05-10_122636/"
    predict_multiple_imgs(imgs_fdir, fdir_model, materials_dict={0: "trash"},
                          save_predictions=True, save_visualisations=False, use_cpu=True,
                          roi_heads_score_test_thresh=0.25, roi_heads_nms_thresh=0.45)