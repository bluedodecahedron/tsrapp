from django.test import TestCase
from app.apps.tsdr import services
import cv2


class TsdTestCase(TestCase):
    def test_tsd_detects_many_classes1(self):
        image = cv2.imread("resources/manytrafficsigns1.jpg")
        tsd_result = services.tsd(image)
        assert len(tsd_result.get_boxed_images()) == 9


class TsdrTestCase(TestCase):
    def test_tsdr_detects_many_classes_1(self):
        image = cv2.imread("resources/images/manytrafficsigns1.jpg")
        class_ids, img = services.tsdr(image)
        assert len(class_ids) == 9

    def test_tsdr_detects_many_classes_2(self):
        image = cv2.imread("resources/images/manytrafficsigns2.jpg")
        class_ids, img = services.tsdr(image)
        assert len(class_ids) == 12

    def test_tsdr_detects_some_classes_1(self):
        image = cv2.imread("resources/images/sometrafficsigns1.jpg")
        class_ids, img = services.tsdr(image)
        assert len(class_ids) == 3

    def test_tsdr_detects_some_classes_2(self):
        image = cv2.imread("resources/images/sometrafficsigns2.jpg")
        class_ids, img = services.tsdr(image)
        assert len(class_ids) == 3

    def test_tsdr_detects_no_classes(self):
        image = cv2.imread("resources/images/notrafficsigns.jpg")
        class_ids, img = services.tsdr(image)
        assert len(class_ids) == 0
