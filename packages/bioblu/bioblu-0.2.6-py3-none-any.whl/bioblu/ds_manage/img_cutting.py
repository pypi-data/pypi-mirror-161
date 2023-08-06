#!/usr/bin/env python3
import PIL.Image
import cv2
import logging
from datetime import datetime
import numpy as np
import os
import pandas as pd
from typing import Tuple, List, Union

from bioblu.main import IMG_FORMATS, YOLO_IMG_FORMATS
from bioblu.ds_manage import geoprocessing, ds_annotations

# ToDo: 1.) General: Add place and date to tile names?


def get_larges_img_dim(fdir):
    largest_dim = 0
    img_paths = ds_annotations.get_all_fpaths_by_extension(fdir, YOLO_IMG_FORMATS)
    for fpath in img_paths:
        width, height, _ = cv2.imread(fpath).shape
        if max(width, height) > largest_dim:
            largest_dim = max(width, height)
    return largest_dim


def calculate_offset_yx(tile_center_yx: Tuple[int, int], img_center_yx: Tuple[int, int]):
    """
    Calculates the pixel offset of a tile_position_yx center from the original image center.
    :param tile_center_yx:
    :param img_center_yx:
    :return: np.array
    """
    y_offset = tile_center_yx[0] - img_center_yx[0]
    x_offset = tile_center_yx[1] - img_center_yx[1]
    logging.info(f"y_offset, x_offset: {y_offset, x_offset}")
    return y_offset, x_offset


def new_tile_cutter(fdir: str, nrows: int, ncols: int,
                             altitude_m: Union[float, int],
                             target_dir: str = "",
                             location_name: str = "",
                             focal_length_mm: float = 8.6, sensor_width_mm: float = 12.8333,
                             save_csv: bool = True, keep_file_type: bool = False, file_type: str = ".JPG",
                             inject_gps_exif: bool = True, inject_uav_yaw: bool = True,
                    include_coords_in_fname=True) -> Tuple[str, dict]:
    """
    New, streamlined tile cutter, with no memory leak.
    :param fdir:
    :param nrows:
    :param ncols:
    :param altitude_m:
    :param target_dir:
    :param location_name:
    :param focal_length_mm:
    :param sensor_width_mm:
    :param save_csv:
    :param keep_file_type: Overrides parameter file_type
    :param file_type:
    :param inject_gps_exif: Only works if the saved tiles are jpg or jpeg
    :param inject_uav_yaw:
    :return:
    """
    if location_name:
        location_name += "_"  # Add underscore
    img_paths = [os.path.join(fdir, fname) for fname in sorted(os.listdir(fdir)) if fname.lower().endswith(IMG_FORMATS)]
    img_count = len(img_paths)

    tiles_dir = target_dir
    if not tiles_dir:
        tstamp = format(datetime.now(), "%Y-%m-%d")
        tiles_dir = os.path.join(fdir, f"tiles_{tstamp}")

    if not os.path.isdir(tiles_dir):
        os.makedirs(tiles_dir)

    tiles_df = None
    for i, fpath in enumerate(img_paths):
        print(f"Processing img. {i+1}/{img_count}: {fpath}")
        img_base_name = os.path.split(fpath)[-1].split(".")[0]

        img_coordinates, coords_found = geoprocessing.get_coordinates_from_img(fpath)
        uav_yaw = geoprocessing.get_uav_yaw(fpath)
        print(f"DRONE YAW: {uav_yaw} degrees.")
        img = cv2.imread(fpath)
        img_height, img_width, channels = img.shape
        img_gsd_cm = geoprocessing.get_gsd(altitude_m=altitude_m, focal_length_real_mm=focal_length_mm,
                                           sensor_width_mm=sensor_width_mm, img_width=img_width)
        img_center_xy = (np.array([img_width, img_height]) / 2).astype(int)
        logging.debug(f"Img. center xy: {img_center_xy}")
        colwidth, rowheight = img_width / ncols, img_height / nrows

        for col in range(ncols):
            tile_center_latlong = (0, 0)  # To keep pycharm from complaining
            start_px_h = int(col * colwidth)
            end_px_h = int((col + 1) * colwidth)
            for row in range(nrows):
                start_px_v = int(row * rowheight)
                end_px_v = int((row + 1) * rowheight)
                logging.info(f"x, y: {(start_px_h, start_px_v)} to {end_px_h, end_px_v}")
                tile = img[start_px_v:end_px_v, start_px_h:end_px_h, :]
                coords_string = "_no_coords"
                if coords_found:
                    tile_center_xy = np.array([start_px_h + int(0.5 * colwidth), start_px_v + int(0.5 * rowheight)])
                    tile_center_latlong = geoprocessing.geolocate_point(pixel_xy=tuple(tile_center_xy),
                                                                        img_dims_wh=(img_width, img_height),
                                                                        img_lat_lon=img_coordinates,
                                                                        gsd_cm=img_gsd_cm, drone_yaw_deg=uav_yaw)
                    coords_string = geoprocessing.dd_coords_to_string(tile_center_latlong)

                if keep_file_type:
                    file_type = os.path.split(fpath)[-1].split('.')[-1]
                tile_name = f"{location_name}{img_base_name}_{row}-{col}{coords_string}.{file_type.strip().strip('.')}"
                tile_path = os.path.join(tiles_dir, tile_name)
                tile_img = PIL.Image.fromarray(tile[:, :, ::-1])
                tile_img.save(tile_path)
                cv2.imwrite(tile_path, tile)

                # Update the dataframe
                tile_info = {"img_path": [fpath], "tile_path": tile_path, "tile_name": [tile_name], "gsd_cm": [img_gsd_cm],
                             "img_lat": [img_coordinates[0]], "img_lon": [img_coordinates[1]],
                             "tile_lat": [tile_center_latlong[0]], "tile_lon": [tile_center_latlong[1]],
                             "uav_yaw_deg": uav_yaw}
                if tiles_df is None:
                    tiles_df = pd.DataFrame(tile_info)
                else:
                    tiles_df = tiles_df.append(pd.DataFrame(tile_info))
                if inject_gps_exif:
                    try:
                        geoprocessing.inject_coord_info(tile_path, tile_center_latlong, 10)
                    except geoprocessing.ImageFormatError:
                        logging.info("Could not inject GPS info into exif data.")
                if inject_uav_yaw and uav_yaw is not None:
                    geoprocessing.inject_uav_yaw(tile_path, uav_yaw)
    if save_csv:
        tiles_df.to_csv(os.path.join(tiles_dir, "tiles.csv"))

    gsd_values = tiles_df[["tile_path", "gsd_cm"]].to_dict("list")  # use .to:dict("records") or .to_dict("list")

    print("Image cutting completed.")
    return tiles_dir, gsd_values


if __name__ == "__main__":
    loglevel = logging.INFO
    logformat = "[%(levelname)s]\t%(funcName)30s: %(message)s"
    logging.basicConfig(level=loglevel, format=logformat)
    logging.disable()

    # fpath_img = "/media/findux/DATA/Documents/Malta_II/surveys/Messina/DJI/frames/" \
    #             "Messina_tiles_2022-05-18/Messina_DJI_0003_out_67_1-0.tif"
    # img = cv2.imread(fpath_img)
    #
    # tile = Tile(array=img, timestamp=None, location="Messina",tile_position_yx=(1, 0), tile_center_abs_yx=(2, 2),
    #             tile_name="testtile", total_tiles_yx=(3, 3), dims_orig_img_yx=(123, 12332), orig_center=(20, 20),
    #             fpath_orig_img="/fuck/the/duck/", gsd_cm=2.3, fpath_tile="asjh")
    # print(tile)
    # tile.show()

    fpath_src = "/media/findux/DATA/Documents/Malta_II/surveys/Messina/new_tono_mela/DJI_0165_W_250_frame_interval/"
    new_tile_cutter(fpath_src, 2, 3, 7, location_name="tono_mela_65")