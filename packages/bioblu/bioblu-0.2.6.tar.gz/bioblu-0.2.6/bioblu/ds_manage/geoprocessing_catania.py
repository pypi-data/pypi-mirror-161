#!/usr/bin/env python3

import logging
import math
from bioblu.ds_manage import geoprocessing

def catania_original():
    hfovan=84*math.pi/180 #angolo fov hor
    #h=100.70 #altezza dm
    h = row['Alt']*10
    z=2
    hfov=2*h*math.tan(hfovan/2)/z
    hres=1920
    vres=1080
    g_km = 111.139 #un grado = 111.195 km --> g/km
    A = hfov/hres/g_km   #transform in grade
    #lung/pixel_x
    #yaw = 51.7*math.pi/180
    yaw = row['Yaw']*math.pi/180
    D = math.sin(yaw)
    B = math.cos(yaw)
    E = A
    #C = 382590.38  #lat
    C = row['Lat']*10000
    #F = 155986.98 #lng
    F = row['Long']*10000 #lng
    #px = 1338
    #py = 389
    px = row['Px']
    py = row['Py']
    #formula c hres/2,vres/2
    mx = C + A * ((px-hres/2)*B  - (py-vres/2)*D)
    my = F + E * ((px-hres/2)*D + (py-vres/2)*B)


def catania_adjusted(altitude_m, px_x, px_y, fov_d=84, hres=1920, vres=1080, yaw_d: float = 0,
                     lat: float = 0, lon: float = 0):
    hfovan = fov_d * math.pi / 180  # angolo fov hor
    h = altitude_m
    z = 2
    hfov = 2 * h * math.tan(math.radians(hfovan / 2)) / z
    g_km = 111.139
    A = hfov / hres / g_km
    yaw = yaw_d * math.pi / 180
    D = math.sin(math.radians(yaw))
    B = math.cos(math.radians(yaw))
    E = A
    C = lat * 10000
    F = lon * 10000 #lng
    px = px_x
    py = px_y
    mx = C + A * ((px-hres/2)*B - (py-vres/2)*D)
    my = F + E * ((px-hres/2)*D + (py-vres/2)*B)
    return mx, my


def get_mx_my(latlon_img: tuple, px_wh: tuple, img_wh: tuple, yaw_angle):
    # From the presentation 2022-06-21
    pass


def catania_corrected(altitude, fov_deg = 84, hres=1920, vres=1080, uav_yaw=0):
    fov_h_rad = fov_deg * math.pi / 180  # R: Transform FOV to radians
    z = 2
    hfov = 2 * altitude * math.tan(fov_h_rad / 2) / z  # R: another way of doing:
    h_fp_half = math.tan(math.radians(fov_deg * 0.5)) * 100  # R: calc half the horz. footprint
    print(f"{hfov == h_fp_half = }")
    g_km = 111.139 #un grado = 111.195 km --> g/km  # R: Depends on the latitude
    g_m = g_km * 1000

    A = hfov/hres/g_km   #transform in grade
    #  I think this should be:
    A_r = hfov / (0.5 * hres) / g_m
    print(A, A_r)
    yaw = uav_yaw * math.pi / 180  # R: Transform to radians
    D = math.sin(yaw)
    B = math.cos(yaw)
    E = A
    # #C = 382590.38  #lat
    # C = row['Lat']*10000
    # #F = 155986.98 #lng
    # F = row['Long']*10000 #lng
    # #px = 1338
    # #py = 389
    # px = row['Px']
    # py = row['Py']
    # #formula c hres/2,vres/2
    # mx = C + A * ((px-hres/2)*B  - (py-vres/2)*D)
    # my = F + E * ((px-hres/2)*D + (py-vres/2)*B)


if __name__ == "__main__":
    loglvl = logging.DEBUG
    logformat = "[%(levelname)s]\t%(funcName)15s: %(message)s"
    logging.basicConfig(format=logformat, level=loglvl)
    # logging.disable()


    lat = 35.9
    lon = 14.4
    px_x = 2336
    px_y = 1424
    altitude = 3666
    hres = 5472
    vres = 3648
    drone_yaw = 45

    catania_results = catania_adjusted(altitude_m=altitude,
                                       px_x=px_x - (0.5 * hres),
                                       px_y=px_y - (0.5 * vres),
                                       yaw_d=45, lat=35.9, lon=14.1)
    my_results = geoprocessing.geolocate_point(pixel_xy=(px_x, px_y), img_dims_wh=(hres, vres), img_lat_lon=(lat, lon),
                                               gsd_cm=geoprocessing.get_gsd(altitude_m=altitude, img_width=hres),
                                               drone_yaw_deg=drone_yaw)
    print(catania_results)
    print(my_results)