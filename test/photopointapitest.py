import unittest
import os
from os import listdir
import sys
from PIL import Image, ImageTk, ImageChops
import shutil
import numpy as np


sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..','src'))

from photopointapi import PhotoPointApi, Photos2Points, PhotoProcessor

class PhotoPointApiTests(unittest.TestCase):
    def setUp(self):
        self.test_folder = os.path.join(os.path.dirname(__file__), 'test_data')
        self.simple_test_folder = os.path.join(os.path.dirname(__file__), 'test_data_simple')

    def test_count_images_in_folder_returns_correct_jpg_count(self):
        expected = 5

        ppa = PhotoPointApi()
        actual = ppa.count_images_in_folder(self.test_folder)

        self.assertEquals(expected,actual)

    def test_count_only_images_in_folder_returns_correct_count(self):
        test_folder = os.path.dirname(__file__)
        expected = 0

        ppa = PhotoPointApi()
        actual = ppa.count_images_in_folder(test_folder)

        self.assertEquals(expected,actual)

    def test_test_image_should_return_a_scaled_image_when_given_folder_with_images(self):
        expected_size = 128,72
        ppa = PhotoPointApi()
        (actual, filename) = ppa.test_image(self.test_folder,expected_size, (0,0,0),4)

        self.assertEquals(expected_size[0],actual.size[0])
        self.assertEquals(expected_size[1],actual.size[1])


class PhotoProcessorTests(unittest.TestCase):
    def setUp(self):
        self.test_folder = os.path.join(os.path.dirname(__file__), 'test_data')
        self.test_file = sorted([ os.path.join(self.test_folder,f) for f in listdir(self.test_folder)])[0]
        self.simple_test_folder = os.path.join(os.path.dirname(__file__), 'test_data_simple')
        self.simple_test_file1 = sorted([ os.path.join(self.simple_test_folder,f) for f in listdir(self.simple_test_folder)])[0]
        self.simple_test_file2 = sorted([ os.path.join(self.simple_test_folder,f) for f in listdir(self.simple_test_folder)])[1]
        self.simple_test_file4 = sorted([ os.path.join(self.simple_test_folder,f) for f in listdir(self.simple_test_folder)])[3]
        self.photo_processor = PhotoProcessor()

    def assert_image_equal(self,im1, im2):
        if (ImageChops.difference(im1, im2).getbbox() is None):
            return
        else:
            raise AssertionError("Images are not the same")

    def test_get_points_should_add_points_above_threshold(self):
        test_threshold = (255,255,255)
        test_z_pos = 0
        scale = 1
        simplification = 1
        crop = 0
        offset = (0,0)
        result = self.photo_processor.get_points(self.simple_test_file1,
                            test_threshold, 
                            test_z_pos, 
                            scale, 
                            simplification, 
                            crop,
                            offset
                            )
        expected_points =np.array([[46.0, 52.0, 0.0, 255, 255, 255,]])
        self.assertTrue(np.allclose(expected_points , result))

    def test_get_points_should_scale_points(self):
        test_threshold = (255,255,255)
        test_z_pos = 0
        scale = 0.1
        simplification = 1
        crop = 0
        offset = (0,0)
        result = self.photo_processor.get_points(self.simple_test_file1,
                            test_threshold, 
                            test_z_pos, 
                            scale, 
                            simplification, 
                            crop,
                            offset
                            )

        expected_points = np.array([[4.6,5.2,0.0,255,255,255]])
        self.assertTrue(np.allclose(expected_points , result))

    def test_get_points_should_simplify_points(self):
        test_threshold = (0,0,255)
        test_z_pos = 0
        scale = 0.1
        simplification = 10
        crop = 0
        offset = (0,0)
        result = self.photo_processor.get_points(self.test_file,
                            test_threshold, 
                            test_z_pos, 
                            scale, 
                            simplification, 
                            crop,
                            offset
                            )

        expected_points = 6
        actual_points = result.shape[0]
        self.assertEquals(expected_points,actual_points)

    def test_get_points_should_crop_and_offset_image_first(self):
        test_threshold = (255,255,255)
        test_z_pos = 0
        scale = 1
        simplification = 1
        crop = 50
        offset = (10,10)
        result = self.photo_processor.get_points(self.simple_test_file1,
                            test_threshold, 
                            test_z_pos, 
                            scale, 
                            simplification, 
                            crop,
                            offset
                            )

        expected_points = np.array([[31.0,37.0,0.0,255,255,255]])
        self.assertTrue(np.allclose(expected_points , result))

    def test_get_image_should_blacken_points_below_threshold(self):
        test_threshold = (255,255,255)
        crop = 0
        offset = (0,0)
        result = self.photo_processor.get_image(self.simple_test_file1,
                            test_threshold, 
                            crop,
                            offset
                            )
        expected_image = np.zeros((100,100,3))
        expected_image[52][46] = np.array([255,255,255])
        self.assertTrue(np.allclose(np.array(expected_image) , np.array(result)))

    def test_get_image_should_blacken_points_below_threshold_special(self):
        test_threshold = (255,64,0)
        crop = 0
        offset = (0,0)
        result = self.photo_processor.get_image(self.simple_test_file4,
                            test_threshold, 
                            crop,
                            offset
                            )
        expected_image = np.zeros((100,100,3))
        # expected_image[41][46] = np.array([255,64,0])
        self.assertTrue(np.allclose(np.array(expected_image) , np.array(result)))

    def test_get_image_should_return_a_altered_image_with_specified_background(self):
        test_threshold = (255,255,255)
        crop = 0
        offset = (0,0)
        background = (100,100,100)
        result = self.photo_processor.get_image(self.simple_test_file1,
                            test_threshold, 
                            crop,
                            offset,
                            background
                            )
        expected_image = np.ones((100,100,1)) * np.array(background)
        expected_image[52][46] = np.array([255,255,255])
        self.assertTrue(np.allclose(np.array(expected_image) , np.array(result)))

    def test_get_image_should_crop_offset_specifed_image(self):
        test_threshold = (255,255,255)
        crop = 50
        offset = (10,10)
        result = self.photo_processor.get_image(self.simple_test_file1,
                            test_threshold, 
                            crop,
                            offset
                            )
        expected_image = np.zeros((50,50,3))
        expected_image[37][31] = np.array([255,255,255])
        self.assertTrue(np.allclose(np.array(expected_image) , np.array(result)))   

class Photos2PointsTests(unittest.TestCase):

    def setUp(self):
        self.test_folder = os.path.join(os.path.dirname(__file__), 'test_data')
        self.test_files = sorted([ os.path.join(self.test_folder,f) for f in listdir(self.test_folder)])
        self.simple_test_folder = os.path.join(os.path.dirname(__file__), 'test_data_simple')
        self.simple_test_files = sorted([ os.path.join(self.simple_test_folder,f) for f in listdir(self.simple_test_folder)])
        self.output_folder = os.path.join(os.path.dirname(__file__), 'test_output')
        try:
            os.stat(self.output_folder)
            shutil.rmtree(self.output_folder)
        except:
            pass
        os.mkdir(self.output_folder)
        self.output_file = os.path.join(self.output_folder, 'output.ply')

    def test_process_should_create_specified_ply_file(self):
        test_threshold = (255,255,255)
        test_z_pixels = 1
        self.assertFalse(os.path.isfile(self.output_file))
        ppa = Photos2Points(self.simple_test_files,
                            self.output_file,
                            test_threshold,
                            test_z_pixels,
                            1,
                            1,
                            None,
                            0,
                            (0,0)
                            )
        ppa.start()
        ppa.join()
        self.assertTrue(os.path.isfile(self.output_file))

    def test_process_should_create_specified_ply_file_and_add_headers(self):
        test_threshold = (255,255,255)
        test_z_pixels = 1
        ppa = Photos2Points(self.simple_test_files,
                            self.output_file,
                            test_threshold,
                            test_z_pixels,
                            1,
                            1,
                            None,
                            0,
                            (0,0))
        ppa.start()
        ppa.join()
        expected_headers ='''ply
format ascii 1.0
comment object: %s
element vertex %s
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
''' % (self.simple_test_folder, 3)
        with open(self.output_file, 'r') as actual:
            data = actual.read()
            self.assertTrue(data.startswith(expected_headers),data )

    def test_process_should_add_points_above_threshold_with_correct_z(self):
        test_threshold = (255,255,255)
        test_z_pixels = 2
        ppa = Photos2Points(self.simple_test_files,
                            self.output_file,
                            test_threshold,
                            test_z_pixels,
                            1,
                            1,
                            None,
                            0,
                            (0,0)
                            )
        ppa.start()
        ppa.join()
        expected_points ='''46.0 52.0 0.0 255 255 255\n46.0 52.0 2.0 255 255 255\n46.0 52.0 4.0 255 255 255\n'''
        with open(self.output_file, 'r') as actual:
            data = actual.read()
            self.assertTrue(data.endswith(expected_points),"Expected: [%s] but was [%s]" % (expected_points, data) )


if __name__ == '__main__':
    unittest.main()
