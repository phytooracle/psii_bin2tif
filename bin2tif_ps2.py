#!/usr/bin/env python3
"""
Author : Emmanuel Gonzalez
Date   : 2020-08-20
Purpose: Convert PSII bin files to TIFF images
"""

import argparse
import os
import sys
import datetime
import logging
from typing import Optional
import numpy as np
from terrautils.spatial import scanalyzer_to_latlon
import json
import glob

from terrautils.formats import create_geotiff, create_image
from terrautils.spatial import geojson_to_tuples


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Rock the Casbah',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('dir',
                        nargs='+',
                        type=str,
                        #metavar='str',
                        help='Directory containing bin files')

    parser.add_argument('-m',
                        '--metadata',
                        help='Cleaned metadata file',
                        metavar='str',
                        type=str,
                        required=True)

    parser.add_argument('-z',
                        '--zoffset',
                        help='Z-axis offset',
                        metavar='z-offset',
                        type=int,
                        default=0.76)

    parser.add_argument('-o',
                        '--outdir',
                        help='TIF output directory',
                        metavar='str',
                        type=str,
                        default='bin2tif_out')

    return parser.parse_args()


# --------------------------------------------------
def get_boundingbox(metadata):
    args = get_args()
    z_offset = args.zoffset

    with open(metadata) as f:
        meta = json.load(f)['lemnatec_measurement_metadata']

    loc_gantry_x = float(meta['sensor_fixed_metadata']['location in camera box x [m]'])
    loc_gantry_y = float(meta['sensor_fixed_metadata']['location in camera box y [m]'])
    loc_gantry_z = float(meta['sensor_fixed_metadata']['location in camera box z [m]'])

    gantry_x = float(meta['gantry_system_variable_metadata']['position x [m]']) + loc_gantry_x
    gantry_y = float(meta['gantry_system_variable_metadata']['position y [m]']) + loc_gantry_y
    gantry_z = float(meta['gantry_system_variable_metadata']['position z [m]']) + z_offset + loc_gantry_z#offset in m

    fov_x, fov_y = meta['sensor_fixed_metadata']['field of view X [m]'], meta['sensor_fixed_metadata']['field of view y [m]']

    # img_height = int(meta['sensor_fixed_metadata']['camera resolution'].split('x')[0])
    # img_width = int(meta['sensor_fixed_metadata']['camera resolution'].split('x')[1])

    B = gantry_z
    A_x = np.arctan((0.5*float(fov_x))/0.8)#2)
    A_y = np.arctan((0.5*float(fov_y))/0.8)#2)
    L_x = 2*B*np.tan(A_x)
    L_y = 2*B*np.tan(A_y)

    x_n = gantry_x + (L_x/2)
    x_s = gantry_x - (L_x/2)
    y_w = gantry_y + (L_y/2)
    y_e = gantry_y - (L_y/2)

    bbox_nw_latlon = scanalyzer_to_latlon(x_n, y_w)
    bbox_se_latlon = scanalyzer_to_latlon(x_s, y_e)

    # TERRA-REF
    lon_shift = 0.000020308287

    # Drone
    lat_shift = 0.000018292 #0.000015258894
    b_box =  ( bbox_se_latlon[0] - lat_shift,
                bbox_nw_latlon[0] - lat_shift,
                bbox_nw_latlon[1] + lon_shift,
                bbox_se_latlon[1] + lon_shift )

    return b_box


# --------------------------------------------------
def main():
    """Read each bin file and convert to TIFF format"""

    args = get_args()
    start_timestamp = datetime.datetime.utcnow()
    path = os.getcwd()

    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)

    file_endings = ["{0:0>4}.bin".format(i) for i in range(0, 101)]

    img_width, img_height = 1216, 1936
    gps_bounds = get_boundingbox(args.metadata)

    png_frames = {}
    cnt = 0

    for one_file in args.dir:

        if one_file[-8:] in file_endings:
            cnt += 1
            pixels = np.fromfile(one_file, np.dtype('uint8')).reshape(-1, img_height)
            reshape_pixels = np.rot90(pixels, 3)

            tif_filename = os.path.join(args.outdir, os.path.basename(one_file.replace('.bin', '.tif')))
            create_geotiff(reshape_pixels, gps_bounds, tif_filename, None, True, None , None, compress=True)


# --------------------------------------------------
if __name__ == '__main__':
    main()
