#!/usr/bin/env python3

from numpy.testing import assert_allclose
import os
import pathlib
import unittest
from numpy.testing import assert_allclose

from bioblu.ds_manage import geoprocessing, ds_annotations


class GeoprocessingTests(unittest.TestCase):

    def test_dms_to_dd(self):
        assert_allclose(geoprocessing.dms_to_dd((156, 11, 12.3)), 156.186759999)
        assert_allclose(geoprocessing.dms_to_dd((0, 0, 0.255)), 0.0000708333333)
        assert_allclose(geoprocessing.dms_to_dd((0, 0, 0.001)), 0.0000002777778)

    def test_dd_to_dms(self):
        assert_allclose(geoprocessing.dd_to_dms(156.742), (156, 44, 31.2))
        assert_allclose(geoprocessing.dd_to_dms(42.3601), (42, 21, 36.36))
        assert_allclose(geoprocessing.dd_to_dms(0.000856), (0, 0, 3.0816))
        assert_allclose(geoprocessing.dd_to_dms(-42.3601), (-42, -21, -36.36))

    def test_extract_coordinates(self):
        unittest_dirloc = pathlib.Path(__file__).parent.resolve()
        img_path = os.path.join(unittest_dirloc, "DJI_0503_resized.JPG")
        coords, coords_found = geoprocessing.get_coordinates_from_img(img_path)
        self.assertEqual(coords, (35.981887472222226, 14.332385416666666))

    def test_px_shift_euclidean_distance(self):
        self.assertEqual(geoprocessing.get_euclidean_shift_distance((40, 60)), 72.11102550927978)
        self.assertEqual(geoprocessing.get_euclidean_shift_distance((-40, 60)), 72.11102550927978)
        self.assertEqual(geoprocessing.get_euclidean_shift_distance((40, -60)), 72.11102550927978)
        self.assertEqual(geoprocessing.get_euclidean_shift_distance((40, -60)), 72.11102550927978)
        self.assertEqual(geoprocessing.get_euclidean_shift_distance((0, -60)), 60)
        self.assertEqual(geoprocessing.get_euclidean_shift_distance((40, 0)), 40)
        self.assertEqual(geoprocessing.get_euclidean_shift_distance((0, -0)), 0)
        self.assertEqual(geoprocessing.get_euclidean_shift_distance((-1700, -1700)), 2404.1630560342614)

    def test_px_shift_angle(self):
        self.assertEqual(geoprocessing.get_px_shift_angle((-40, -40)), -45)
        self.assertEqual(geoprocessing.get_px_shift_angle((40, -40)), -135)
        self.assertEqual(geoprocessing.get_px_shift_angle((-40, 40)), 45)
        self.assertEqual(geoprocessing.get_px_shift_angle((40, 40)), 135)
        self.assertEqual(geoprocessing.get_px_shift_angle((-40, 0)), 0)
        self.assertEqual(geoprocessing.get_px_shift_angle((40, 0)), 180)
        self.assertEqual(geoprocessing.get_px_shift_angle((0, -40)), -90)
        self.assertEqual(geoprocessing.get_px_shift_angle((0, 40)), 90)
        self.assertEqual(geoprocessing.get_px_shift_angle((0, 0)), 0)
        self.assertEqual(geoprocessing.get_px_shift_angle((-20, -20)), -45)
        self.assertEqual(geoprocessing.get_px_shift_angle((-20, 20)), 45)
        self.assertEqual(geoprocessing.get_px_shift_angle((20, 20)), 135)
        self.assertEqual(geoprocessing.get_px_shift_angle((20, -20)), -135)
        self.assertEqual(geoprocessing.get_px_shift_angle((0, 20)), 90)
        self.assertEqual(geoprocessing.get_px_shift_angle((20, 0)), 180)
        self.assertEqual(geoprocessing.get_px_shift_angle((-90, 0)), 0)
        self.assertEqual(geoprocessing.get_px_shift_angle((90, 0)), 180)
        self.assertEqual(geoprocessing.get_px_shift_angle((-90, -90)), -45)
        self.assertEqual(geoprocessing.get_px_shift_angle((-90, 90)), 45)
        self.assertEqual(geoprocessing.get_px_shift_angle((90, -90)), -135)
        self.assertEqual(geoprocessing.get_px_shift_angle((90, 90)), 135)

    def test_angle_to_within_180(self):
        self.assertEqual(geoprocessing.transform_angle_to_180_range(30), 30)
        self.assertEqual(geoprocessing.transform_angle_to_180_range(-30), -30)
        self.assertEqual(geoprocessing.transform_angle_to_180_range(179), 179)
        self.assertEqual(geoprocessing.transform_angle_to_180_range(-181), 179)
        self.assertEqual(geoprocessing.transform_angle_to_180_range(-190), 170)
        self.assertEqual(geoprocessing.transform_angle_to_180_range(181), -179)
        self.assertEqual(geoprocessing.transform_angle_to_180_range(-180), -180)
        self.assertEqual(geoprocessing.transform_angle_to_180_range(180), 180)
        self.assertEqual(geoprocessing.transform_angle_to_180_range(0), 0)
        self.assertEqual(geoprocessing.transform_angle_to_180_range(360), 0)
        self.assertEqual(geoprocessing.transform_angle_to_180_range(-360), 0)
        self.assertEqual(geoprocessing.transform_angle_to_180_range(-25), -25)

    def test_yx_shift_from_angle(self):
        self.assertAlmostEqual(geoprocessing.get_real_world_px_shift(282.842712474619, 45)[0], -200)
        self.assertAlmostEqual(geoprocessing.get_real_world_px_shift(282.842712474619, 45)[1], 200)
        self.assertAlmostEqual(geoprocessing.get_real_world_px_shift(282.842712474619, 135)[0], 200)
        self.assertAlmostEqual(geoprocessing.get_real_world_px_shift(282.842712474619, 135)[1], 200)
        self.assertAlmostEqual(geoprocessing.get_real_world_px_shift(282.842712474619, -45)[0], -200)
        self.assertAlmostEqual(geoprocessing.get_real_world_px_shift(282.842712474619, -45)[1], -200)
        self.assertAlmostEqual(geoprocessing.get_real_world_px_shift(282.842712474619, -135)[0], 200)
        self.assertAlmostEqual(geoprocessing.get_real_world_px_shift(282.842712474619, -135)[1], -200)
        self.assertEqual(geoprocessing.get_real_world_px_shift(2404.1630560342614, -25), (-2178.911698989681,
                                                                                          -1016.0432116824073))

    def test_axis_flipping(self):
        """Tests whether x becomes y at angles close to +/- 90."""
        img_dims_wh = (680, 480)
        px_yx = 123

    def test_geolocate_pixel(self):
        px_yx = (124, 1036)
        img_wh = (5472, 3648)
        gps_latlon = (35.9, 14.4)
        self.assertEqual(geoprocessing.geolocate_point(px_yx, img_wh, gps_latlon,
                                                       gsd_cm=99.99999525703795, drone_yaw_deg=20))


class AnnotationsTests(unittest.TestCase):

    def test_dict_creation(self):
        materials = ["trash", "pandas"]
        example_dict = {0: "trash", 1: "pandas"}
        self.assertEqual(ds_annotations.create_materials_dict(materials), example_dict)

    def test_basename(self):
        self.assertEqual(ds_annotations.get_basename_only("/foo/bar/pandas/ash_co.ord.txt"), "ash_co.ord")


class BBoxTests(unittest.TestCase):

    def test_bbox_conversions(self):
        bbox = ds_annotations.BBox([100, 100, 900, 900], "test", "voc", 2000, 1500)
        bbox_2 = ds_annotations.BBox([100, 100, 900, 900], "test", "voc", 2000, 1500)
        bbox_2.to_yolo()
        bbox_2.to_coco()
        bbox_2.to_labelme()
        bbox_2.to_voc()
        self.assertEqual(bbox, bbox_2)

    def test_bbox_center_calc(self):
        bbox = ds_annotations.BBox([100, 100, 900, 900], "test", "voc", 2000, 1500)
        self.assertEqual(bbox.box_center_xy, (500, 500))


if __name__ == "__main__":
    unittest.main()
