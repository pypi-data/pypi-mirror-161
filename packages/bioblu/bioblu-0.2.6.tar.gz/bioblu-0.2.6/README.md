# BIOBLU

Git repository for the BIOBLU Italia-Malta project.  
## As of 2022-05-11:  
**Version 0.1.20** (but check using `bioblu.__version__`)  
File list:

```
.
├── bioblu/
│   ├── cluster_scripts/    .   .   .   .   .   .   .   .   .   .   .   General cluster scripts
│   │
│   ├── detectron   .   .   .   .   .   .   .   .   .   .   .   .   .   Detectron2 scripts
│   │   ├── caffe_check.sh  .   .   .   .   .   .   .   .   .   .   .   checks for caffe availability
│   │   ├── detectron2_colab_customized_2022-05-06_nointernet.py    .   colab script
│   │   ├── detectron2_colab_tutorial_ORIGINAL_DONT_TOUCH.7z    .   .   colab script (original)
│   │   ├── detectron2_colab_tutorial.py    .   .   .   .   .   .   .   colab script
│   │   ├── detectron2_test_input.jpg   .   .   .   .   .   .   .   .   test input img
│   │   ├── detectron_install.py    .   .   .   .   .   .   .   .   .   install detectron (deprecated)
│   │   ├── detectron_predict.py    .   .   .   .   .   .   .   .   .   Predict using detectron2
│   │   ├── detectron_predict.sh    .   .   .   .   .   .   .   .   .   Predict using detectron2 in bash
│   │   ├── detectron.py    .   .   .   .   .   .   .   .   .   .   .   Module to handle detectron data
│   │   ├── detectron_training_local.py .   .   .   .   .   .   .   .   Local detectron training
│   │   ├── detectron_training.py   .   .   .   .   .   .   .   .   .   Detectron training module
│   │   ├── get_coco_api.sh .   .   .   .   .   .   .   .   .   .   .   get coco api
│   │   ├── radagast_detectron.sh   .   .   .   .   .   .   .   .   .   run detectron on cluster
│   │   ├── requirements_detectron2.txt .   .   .   .   .   .   .   .   detectron2 reqs
│   │   ├── setup_detectron_local.sh    .   .   .   .   .   .   .   .   setup detectron locally
│   │   └── setup_detectron.sh  .   .   .   .   .   .   .   .   .   .   setup detectron on cluster
│   │
│   ├── ds_manage/  .   .   .   .   .   .   .   .   .   .   .   .   .   General dataset handling scripts
│   │   ├── bbox_conversions.py .   .   .   .   .   .   .   .   .   .   Bounding box conversions
│   │   ├── ds_annotations.py   .   .   .   .   .   .   .   .   .   .   Dataset annotation handling
│   │   ├── ds_convert.py   .   .   .   .   .   .   .   .   .   .   .   Dataset conversions
│   │   ├── ds_split.py .   .   .   .   .   .   .   .   .   .   .   .   Dataset splitting
│   │   ├── geoprocessing.py    .   .   .   .   .   .   .   .   .   .   Mainly for GPS coordinate handling
│   │   ├── image_cutting.py    .   .   .   .   .   .   .   .   .   .   Cutting images into tiles
│   │   ├── labelme_to_yolo.py  .   .   .   .   .   .   .   .   .   .   Convert labelme to yolo
│   │   └── shrink_dataset.py   .   .   .   .   .   .   .   .   .   .   Dataset shrinking
│   │
│   ├── other_files/
│   │   ├── bioblu_yolo.cfg .   .   .   .   .   .   .   .   .   .   .   Used for yolo training settings
│   │   └── ...
│   │
│   ├── tests/
│   │
│   ├── thermal_fusing/ .   .   .   .   .   .   .   .   .   .   .   .   Tests for RGB/OIR overlays. Incomplete
│   │
│   ├── unittests/
│   │
│   ├── yolo/   .   .   .   .   .   .   .   .   .   .   .   .   .   .   Yolo-related scripts
│   │   ├── bioblu_yolo.cfg .   .   .   .   .   .   .   .   .   .   .   Used to store training settings
│   │   ├── radagast_yolo_training.sh   .   .   .   .   .   .   .   .   Train on cluster
│   │   ├── yolo_detector.sh    .   .   .   .   .   .   .   .   .   .   Inference using yolo
│   │   └── yolo_validate.sh    .   .   .   .   .   .   .   .   .   .   Validation
│   │
│   ├── compare_annotations.py
│   ├── create_tiles.py .   .   .   .   .   .   .   .   .   .   .   .   Cutting imgs into tiles
│   ├── cudacheck.py    .   .   .   .   .   .   .   .   .   .   .   .   Cuda availability
│   ├── resampling.py   .   .   .   .   .   .   .   .   .   .   .   .   Img. resampling
│   └── tensorboard_results.py  .   .   .   .   .   .   .   .   .   .   Show training performance using tb
│   
├── README.md   .   .   .   .   .   .   .   .   .   .   .   .   .   .   This readme
├── requirements.txt
└── setup.py


```


| Module             | Function                                                                          |
|--------------------|-----------------------------------------------------------------------------------|
| detectron          | Provides funtionalities around running detectron2                                 |
| ds_annotations     | Annotation operations (e.g. loading annotations, displaying bounding boxes, etc.) |
| ds_convert         | Dataset conversion scripts                                                        |
| ds_split           | Dataset splitting functionalities                                                 |
| geoprocessing.py   | Coordinate calculations etc.                                                      |
| image_cutting.py   | Cutting images into tiles                                                         |
