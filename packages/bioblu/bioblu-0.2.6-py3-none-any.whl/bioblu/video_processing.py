#!/usr/bin/env python3

import cv2
import json
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
import re
from typing import List, Union, Tuple

import pandas as pd

from bioblu.ds_manage import geoprocessing
from bioblu.ds_manage import ds_annotations


def get_video_resolution(fpath_video) -> tuple:
    """
    Returns a tuple (width, height)
    :param fpath_video:
    :return:
    """
    video = cv2.VideoCapture(fpath_video)
    height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    return width, height


def interpolate(start, stop, steps):
    step_size = (stop - start) / steps
    # print(f"step size: {step_size}")
    out_vals = [start + i * step_size for i in range(steps)]
    return out_vals


# def interpolate_np(start, stop, steps):
#     steps_ls = np.array(list(range(steps)))
#     print(steps_ls)
#     return np.interp(steps, [0, 5], [start, stop])


def interpolation_comparison():
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3)

    x_vals = np.linspace(0, 5, num=6)
    interp_np = np.interp(x_vals, [0, 5], [0, 2])
    x_vals2 = np.linspace(5, 10, num=6)
    interp_np2 = np.interp(x_vals2, [5, 10], [2, 10])
    # ax1.plot(x_vals, interp_np, c="red")
    ax1.scatter(x_vals, interp_np, c="blue", label="Interpolated values")
    ax1.scatter(x_vals2, interp_np2, c="blue")
    ax1.scatter([0, 5, 10], [0, 2, 10], c="red", label="Original values")
    ax1.legend()
    ax1.set_title("Numpy")

    interp_r1 = interpolate(0, 2, 5)
    ax2.scatter(list(range(5)), interp_r1, c="blue")
    interp_r2 = interpolate(2, 10, 5)
    x = [5, 6, 7, 8, 9]
    ax2.scatter(x, interp_r2, c="blue")
    ax2.scatter([0, 5, 10], [0, 2, 10], c="red")
    ax2.set_title("Roland")

    ax3.scatter(x_vals, interp_np, alpha=0.5, c="green", label="Numpy")
    ax3.scatter(x_vals2, interp_np2, alpha=0.5, c="green")
    ax3.scatter([0, 1, 2, 3, 4], interp_r1, alpha=0.5, c="red", label="Roland")
    ax3.scatter([5, 6, 7, 8, 9], interp_r2, alpha=0.5, c="red")
    ax3.set_title("Comparison")
    ax3.legend()
    plt.show()


def interpolate_latlon(latlon_start: tuple, latlon_stop: tuple, steps: int) -> Tuple[list, list]:
    latitudes = interpolate(latlon_start[0], latlon_stop[0], steps)
    longitudes = interpolate(latlon_start[1], latlon_stop[1], steps)
    return latitudes, longitudes


def create_srt(fpath_video: str, fpath_subs: str = None) -> None:
    """
    Creates an .srt file in the same place where the video file is located.
    :param fpath_video:
    :return: None.
    """
    if fpath_subs is None:
        fpath_subs = remove_extension(fpath_video) + ".srt"
    command = ["ffmpeg", "-i", fpath_video, fpath_subs]
    os.system(' '.join(command))


def get_latlon_from_srt(frame_string) -> Tuple[float, float, Tuple[str, str]]:
    """

    :param frame_string:
    :return: latitude, longitude, hemispheres
    """
    pattern = re.compile(r"GPS \((-?[\d]+\.[\d]+), (-?[\d]+\.[\d]+), [\d]+\),")  # GPS (14.2823, 36.0614, 15),
    matches = pattern.search(frame_string)
    longitude, latitude = float(matches.group(1)), float(matches.group(2))
    north_south = "N" if latitude >= 0 else "S"
    east_west = "E" if longitude >= 0 else "W"
    assert -90 <= latitude <= 90 and -180 <= longitude <= 180, f"Lat/Long {latitude} {longitude} contains invalid values."
    return latitude, longitude, (north_south, east_west)


def get_srt_second(frame_string) -> int:
    """
    Starts at 1 (not zero-indexing!)
    :param frame_string:
    :return:
    """
    pattern = re.compile(r"^[\n]?([\d]+)\n")
    match = pattern.search(frame_string).group()
    logging.debug(f"Match: {match}")
    return int(match)


def get_filename_only(fpath):
    fname = os.path.split(fpath)[-1].split('.')[0]
    return fname


def remove_extension(fpath: str):
    fpath_out = '.'.join(fpath.split('.')[:-1])
    return fpath_out


def create_frames_output_dir(fpath_video, frame_interval) -> str:
    video_name = get_filename_only(fpath_video)
    output_dir = os.path.join(os.path.split(fpath_video)[0], f"{video_name}_{frame_interval}_frame_interval")
    try:
        os.makedirs(output_dir)
    except FileExistsError:
        print("[ WARNING ] Output directory already exists.\nPress [Enter] to continue regardless, at the risk of overwriting files.")
        input()
    finally:
        return output_dir


def get_current_second(frame_number: int, fps: Union[float, int]) -> int:
    return frame_number // fps


def get_framerate(fpath_video: str) -> Union[float, int]:
    vid = cv2.VideoCapture(fpath_video)
    fps = vid.get(cv2.CAP_PROP_FPS)
    return np.round(fps, 1)


def get_total_frame_count(fpath_video) -> int:
    vid = cv2.VideoCapture(fpath_video)
    framecount = vid.get(cv2.CAP_PROP_FRAME_COUNT)
    return int(framecount)


def load_raw_srt(fpath_srt) -> List[str]:
    with open(fpath_srt, 'r') as f:
        sub_raw = f.read()
    subs = sub_raw.split("\n\n")  # Split them into one subtitle string per second.
    subs = [sub.strip() for sub in subs if sub.strip()]  # remove empty entries and leading/training \n
    return subs


# def read_srt(fpath_srt) -> dict:
#     """
#     Useful for GPS that's updated at 1 Hz.
#     :param fpath_srt:
#     :return:
#     """
#     subs = load_raw_srt(fpath_srt)
#     subs_dict = {}
#     for i, content in enumerate(subs):
#         logging.debug(content)
#         second = get_srt_second(content)
#         lat, long, hemispheres = get_latlon_from_srt(content)
#         logging.debug(f"i:{i}, second: {second}")
#         assert i + 1 == second
#         subs_dict[i] = {"latitude": lat,
#                         "longitude": long,
#                         "hemispheres_lat_long": hemispheres
#                         }
#     return subs_dict


def get_telemetry(fpath_srt: str) -> dict:
    """
    Returs a dictionary with frame numbers as key, and a dict {"latitude": float, "longitude": float, "yaw": float} as
    values. Note that frame numbers are zero indexed (as opposed to the contents of the srt file.

    :param fpath_srt:
    :param frame: zero-indexed frame number.
    :return: dict(frame: {"latitude": float, "longitude": float, "yaw": float})
    """
    with open(fpath_srt, "r") as f:
        srt_raw = f.read()
    srt_raw = [block for block in srt_raw.split("\n\n") if block]  # Avoid empty blocks
    frame_telemetry = {}

    for frame_i, frame_info in enumerate(srt_raw):
        frame = None
        lat, lon = None, None
        yaw = None
        uav_internal_alt = None
        timestamp = None
        frame_match = re.compile(r"^(\d+)\n").findall(frame_info)
        assert int(frame_match[0]) == frame_i + 1
        # When extracting latlon, account for spelling mistace in the data (long-t-itude).
        # Also account for a possible minus sign.
        latlon_match = re.compile(r"latitude: (-?\d+\.\d+).+(?:longitude|longtitude): (-?\d+\.\d+)").findall(frame_info)
        yaw_match = re.compile(r"Drone: Yaw:(-?\d+\.\d+),").findall(frame_info)
        altitude_match = re.compile(r"rel_alt: (-?\d+\.\d+) ").findall(frame_info)
        timestamp_match = re.compile(r"\n(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d(?:,|.)\d\d\d(?:,|.)\d\d\d)\n").findall(frame_info)

        if frame_match:
            frame = int(frame_match[0])
        if latlon_match:
            lat = float(latlon_match[0][0])
            lon = float(latlon_match[0][1])
        if yaw_match:
            yaw = float(yaw_match[0])
        if altitude_match:
            uav_internal_alt = float(altitude_match[0])
        if timestamp_match:
            timestamp = str(timestamp_match[0]).replace(",", "")

        logging.debug(f"Frame: {frame} | Lat.: {lat} | Lon. {lon} | Yaw: {yaw}")
        frame_telemetry[frame] = {"frame_lat": lat, "frame_lon": lon, "yaw": yaw, "internal_altitude": uav_internal_alt,
                                  "timestamp": timestamp}
    logging.info(f"Extracted telemetry data for {len(frame_telemetry.keys())} frames.")
    return frame_telemetry


def get_telemetry_list(fpath_srt) -> List[dict]:
    with open(fpath_srt, "r") as f:
        srt_raw = f.read()
    srt_raw = [block for block in srt_raw.split("\n\n") if block]  # Avoid empty blocks
    frame_telemetry = []
    for frame_i, frame_info in enumerate(srt_raw):

        frame = None
        lat, lon = None, None
        yaw = None
        uav_internal_alt = None
        tstamp = None

        frame_match = re.compile(r"^(\d+)\n").findall(frame_info)
        assert int(frame_match[0]) == frame_i + 1
        # When extracting latlon, account for spelling mistace in the data (long-t-itude).
        # Also account for a possible minus sign.
        latlon_match = re.compile(r"latitude: (-?\d+\.\d+).+(?:longitude|longtitude): (-?\d+\.\d+)").findall(frame_info)
        yaw_match = re.compile(r"Drone: Yaw:(-?\d+\.\d+),").findall(frame_info)
        altitude_match = re.compile(r"rel_alt: (-?\d+\.\d+) ").findall(frame_info)
        timestamp_pattern = re.compile(r"\n(?P<date>\d\d\d\d-\d\d-\d\d) "
                                       r"(?P<hours>\d\d):"
                                       r"(?P<minutes>\d\d):"
                                       r"(?P<seconds>\d\d)(?:,|.)"
                                       r"(?P<miliseconds>\d\d\d)(?:,|.)"
                                       r"(?P<nanoseconds>\d\d\d)\n")
        date = timestamp_pattern.search(frame_info).group("date")
        hours = timestamp_pattern.search(frame_info).group("hours")
        minutes = timestamp_pattern.search(frame_info).group("minutes")
        seconds = timestamp_pattern.search(frame_info).group("seconds") + "."\
                  + timestamp_pattern.search(frame_info).group("miliseconds")\
                  + timestamp_pattern.search(frame_info).group("nanoseconds")

        if date and hours and minutes and seconds:
            tstamp = f"{date} {hours}:{minutes}:{seconds}"

        if frame_match:
            frame = int(frame_match[0])
        if latlon_match:
            lat = float(latlon_match[0][0])
            lon = float(latlon_match[0][1])
        if yaw_match:
            yaw = float(yaw_match[0])
        if altitude_match:
            uav_internal_alt = float(altitude_match[0])

        logging.debug(f"Frame: {frame} | Lat.: {lat} | Lon. {lon} | Yaw: {yaw}")
        frame_telemetry.append({"frame": frame, "img_lat": lat, "img_lon": lon, "yaw": yaw, "internal_altitude": uav_internal_alt,
                                  "timestamp": tstamp})
    logging.info(f"Extracted telemetry data for {len(frame_telemetry)} frames.")
    return frame_telemetry


def get_telemetry_df(fpath_srt: str) -> pd.DataFrame:
    telemetry = get_telemetry_list(fpath_srt)
    return pd.DataFrame(telemetry)


def get_interpolated_telemetry(fpath_srt) -> pd.DataFrame:
    telemetry_df = get_telemetry_df(fpath_srt)
    telemetry_df["img_lat"] = telemetry_df["img_lat"] * 10_000
    telemetry_df["img_lon"] = telemetry_df["img_lon"] * 10_000

    """Interpolates the GPS coordinates, as the GPS records at 5 Hz, while the frames are at 30 FPS"""

    telemetry_df["lat_old"] = telemetry_df["img_lat"]
    telemetry_df["lon_old"] = telemetry_df["img_lon"]

    lat_interpolated = list(telemetry_df["img_lat"].values)
    lon_interpolated = list(telemetry_df["img_lon"].values)

    lat_old = telemetry_df["img_lat"][0]
    lon_old = telemetry_df["img_lon"][0]
    for i, line in telemetry_df.iterrows():
        if i % 6 == 0 and i > 0:
            lat_new = line["img_lat"]
            lon_new = line["img_lon"]
            lat_interp = interpolate(lat_old, lat_new, steps=6)
            lon_interp = interpolate(lon_old, lon_new, steps=6)
            assert lat_old == lat_interp[0]
            assert lon_old == lon_interp[0]

            # Update interpolated coordinates
            lat_interpolated[(i - 5):i] = lat_interp[1:]
            lon_interpolated[(i - 5):i] = lon_interp[1:]

            lat_old = line["img_lat"]
            lon_old = line["img_lon"]

    telemetry_df["img_lat"] = lat_interpolated
    telemetry_df["img_lon"] = lon_interpolated

    telemetry_df["lat_error"] = telemetry_df["lat_old"] - telemetry_df["img_lat"]
    telemetry_df["lon_error"] = telemetry_df["lon_old"] - telemetry_df["img_lon"]

    telemetry_df["img_lat"] = telemetry_df["img_lat"] / 10_000
    telemetry_df["img_lon"] = telemetry_df["img_lon"] / 10_000

    return telemetry_df



# def get_telemetry_df_exp(fpath_srt: str, altitude_m = None) -> pd.DataFrame:
#     telemetry = get_telemetry(fpath_srt)
#     telemetry_ready = {"frame": [], "latitude": [], "longitude": [], "yaw": [], "altitude_m": []}
#     for i, (frame, telemetry_dict) in enumerate(telemetry.items()):
#         latitude, longitude, yaw = telemetry_dict["latitude"], telemetry_dict["longitude"], telemetry_dict["yaw"]
#         telemetry_ready["frame"].append(frame)
#         telemetry_ready["latitude"].append(latitude)
#         telemetry_ready["longitude"].append(longitude)
#         telemetry_ready["yaw"].append(yaw)


def cvt_all_srt_to_csv(fdir, altitude_m = None):
    file_paths = ds_annotations.get_all_fpaths_by_extension(fdir, (".srt",))
    for fpath in file_paths:
        save_path = os.path.splitext(fpath)[0] + ".csv"
        df = get_telemetry_df(fpath, altitude_m=altitude_m)
        df.to_csv(save_path, index=False)


def extract_video_frames(fpath_video: str, frame_interval: int, output_dir=None, subtitle_file="",
                         show_progress=True, retrieve_GPS_coordinates=False, output_format=".tif",
                         altitude_m: int = None, save_csv: bool = False):
    """

    :param fpath_video:
    :param frame_interval: every nth frame will be exported
    :param output_dir: defaults to creating a subfolder in the dir where the video is
    :param subtitle_file: optional. path to subtitle file
    :param show_progress:
    :param retrieve_GPS_coordinates:
    :param output_format:
    :param altitude_m:
    :param save_csv:
    :return:
    """
    if not subtitle_file:
        subtitle_file = remove_extension(fpath_video) + ".SRT"
        logging.debug(f"Inferred subtitle file name: {subtitle_file}")
    if not os.path.exists(subtitle_file):
        print(f"[ Warning ] Did not find subtitle file {subtitle_file}. Continuing regardless.")
    # Initial setup and checks
    if not os.path.exists(fpath_video):
        raise FileNotFoundError(f"Video file not found: {fpath_video}")
    video_name = os.path.split(fpath_video)[-1].split('.')[0].replace(' ', '_')
    logging.info(f"Video name: {video_name}")
    total_frames = get_total_frame_count(fpath_video)
    if output_dir is None:
        output_dir = create_frames_output_dir(fpath_video, frame_interval)
    if retrieve_GPS_coordinates:
        telemetry_data = get_telemetry(subtitle_file)
    # Open video
    video = cv2.VideoCapture(fpath_video)
    if not video.isOpened():
        raise IOError("Cannot open video")
    # Extract frames
    current_frame = 0
    processed_frames = 0
    coordinates = {"img": [], "latitude": [], "longitude": [], "yaw": [], "internal_altitude": []}
    while video.isOpened():
        frame_retrieved, frame = video.read()
        if frame_retrieved:
            # Check if frame should be exported
            if current_frame % frame_interval == 0:
                if show_progress:
                    msg_params = {"perc": current_frame / total_frames * 100, "frame": current_frame}
                    print("{perc:05.2f} % completed. Processing frame {frame}".format(**msg_params))
                logging.debug(f"Output dir: {output_dir}")
                logging.debug(f"Video name: {video_name}")
                logging.debug(f"Current frame: {current_frame}")
                fpath_frame_out = os.path.join(output_dir,
                                               f"{video_name}_frame_{current_frame}.{output_format.lstrip('.')}")
                # Save frame
                cv2.imwrite(fpath_frame_out, frame)
                if retrieve_GPS_coordinates:
                    telemetry_at_frame = telemetry_data[current_frame]
                    logging.debug(f"Telemetry data: {telemetry_at_frame}")
                    if telemetry_at_frame is not None:
                        lat_lon: tuple = telemetry_at_frame.get("frame_lat"), telemetry_at_frame.get("frame_lon")
                        geoprocessing.inject_coord_info(fpath_frame_out, lat_lon, altitude_m=altitude_m)
                        geoprocessing.inject_uav_yaw(fpath_frame_out, telemetry_at_frame["yaw"])
                        coordinates["img"].append(fpath_frame_out)
                        coordinates["latitude"].append(lat_lon[0])
                        coordinates["longitude"].append(lat_lon[1])
                        coordinates["yaw"].append(telemetry_at_frame.get("yaw"))
                        coordinates["internal_altitude"].append(telemetry_at_frame.get("internal_altitude"))
                processed_frames += 1
            current_frame += 1
        else:  # If no frame received, i.e. end of video.
            print(f"Reached end of video. Exported {processed_frames} frames.")
            break
    video.release()
    if save_csv:
        pd.DataFrame(coordinates).to_csv(os.path.join(output_dir, "img_coords.csv"))
    print("Done")


if __name__ == "__main__":

    loglevel = logging.DEBUG
    logformat = "[%(levelname)s]\t%(funcName)15s: %(message)s"
    logging.basicConfig(level=loglevel, format=logformat)
    logging.disable()

    # srt_file = "/media/findux/DATA/Documents/Malta_II/surveys/Messina/new_tono_mela/DJI_0155_W.SRT"
    # print(get_telemetry_at_frame(srt_file, 3000))

    # video = "/media/findux/DATA/Documents/Malta_II/surveys/Messina/new_tono_mela/DJI_0167_W.MP4"
    # extract_video_frames(video, 250, retrieve_GPS_coordinates=True,
    #                      output_format=".jpg", altitude_m=8, save_csv=True)

    # srt_file = "/home/findux/Desktop/Catania_workshop/drone_tests/DJI_0495_W.SRT"
    # telemetry_interp = get_interpolated_telemetry(srt_file)
    # telemetry_interp.to_csv("/home/findux/Desktop/Catania_workshop/GPS_interpolation.csv")

    # interpolation_comparison()
    video = "/home/findux/Desktop/Next/Catania_workshop/drone_tests/DJI_0502_W.MP4"
    subs = "/home/findux/Desktop/Next/Catania_workshop/drone_tests/DJI_0502_W.SRT"
    extract_video_frames(video, 12, subtitle_file=subs)