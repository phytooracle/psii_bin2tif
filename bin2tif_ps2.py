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

    parser.add_argument('-o',
                        '--outdir',
                        help='TIF output directory',
                        metavar='str',
                        type=str,
                        default='bin2tif_out')

    return parser.parse_args()


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

    with open(args.metadata) as f:
        meta = json.load(f)['content']
        gps_bounds = geojson_to_tuples(meta['spatial_metadata']['ps2Top']['bounding_box'])
        print(gps_bounds)

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
