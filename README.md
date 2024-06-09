# PSii Bin to Tif
This script converts BIN files to GeoTIFF images for photosystem II (PSII) sensors.

Note that image height and width are collected from the provided metadata, including:

```
    img_width, img_height = 1216, 1936
```

Also, a experimentally derived offset is applied:

```
    # TERRA-REF
    lon_shift = 0.000020308287

    # Drone
    lat_shift = 0.000018292 #0.000015258894
```

## Inputs
A directory of bin files.

## Outputs
All bin files in the input directory converted to geotiff format.

## Arguments and Flags
* **Positional Arguments:**
    * **Directory containing bin files:** 'dir'
* **Required Arguments:**
    * **Cleaned metadata file:** '-m', '--metadata'
    * **Z-Axis offset:** '-z', '-zoffset'
* **Optional Arguments:**
    * **TIF output directory:** '-o', '--outdir', default = 'bin2tif_out'
