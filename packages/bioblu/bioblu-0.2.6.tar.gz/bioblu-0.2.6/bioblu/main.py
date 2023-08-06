#!/usr/bin/env python3

IMG_FORMATS = ("tif", "tiff", "jpg", "jpeg", "png", "bmp", "gif", "webp")
YOLO_IMG_FORMATS = ('.bmp', '.jpg', '.jpeg', '.png', '.tif', '.tiff', '.dng', '.webp', '.mpo')
DRONE_MODELS = {"P4P": {"sensor_width_mm": 12.8333,
                        "focal_length_real_mm": 8.6},
                "M2EA": {"sensor_width_mm": 7.68,
                         "focal_length_real_mm": 4.0}}