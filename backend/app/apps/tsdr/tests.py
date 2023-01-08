from django.test import TestCase
from app.apps.tsdr import services
from app.apps.tsdr.services import ActiveTrafficSigns
import cv2


ROOT_FOLDER = "resources/images/test"


class TsdTestCase(TestCase):
    def test_tsd_detects_many_classes1(self):
        image = cv2.imread(f"{ROOT_FOLDER}/manytrafficsigns1.jpg")
        tsd_result = services.tsd(image)
        assert len(tsd_result.get_boxed_images()) == 9


class TsdrTestCase(TestCase):
    def test_tsdr_detects_many_classes_1(self):
        image = cv2.imread(f"{ROOT_FOLDER}/manytrafficsigns1.jpg")
        class_ids, img = services.tsdr(image)
        assert len(class_ids) == 9

    def test_tsdr_detects_many_classes_2(self):
        image = cv2.imread(f"{ROOT_FOLDER}/manytrafficsigns2.jpg")
        class_ids, img = services.tsdr(image)
        assert len(class_ids) == 12

    def test_tsdr_detects_some_classes_1(self):
        image = cv2.imread(f"{ROOT_FOLDER}/sometrafficsigns1.jpg")
        class_ids, img = services.tsdr(image)
        assert len(class_ids) == 2

    def test_tsdr_detects_some_classes_2(self):
        image = cv2.imread(f"{ROOT_FOLDER}/sometrafficsigns2.jpg")
        class_ids, img = services.tsdr(image)
        assert len(class_ids) == 3

    def test_tsdr_detects_no_classes(self):
        image = cv2.imread(f"{ROOT_FOLDER}/notrafficsigns.jpg")
        class_ids, img = services.tsdr(image)
        assert len(class_ids) == 0
    def test_tsdr_show_result_1(self):
        image = cv2.imread(f"{ROOT_FOLDER}/manytrafficsigns1.jpg")
        class_ids, img = services.tsdr(image)
        cv2.imshow("TSDR Result", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    def test_tsdr_show_result_2(self):
        image = cv2.imread(f"{ROOT_FOLDER}/manytrafficsigns2.jpg")
        class_ids, img = services.tsdr(image)
        cv2.imshow("TSDR Result", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    def test_tsdr_show_result_3(self):
        image = cv2.imread(f"{ROOT_FOLDER}/childrencrossing.jpg")
        class_ids, img = services.tsdr(image)
        cv2.imshow("TSDR Result", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


class ActiveTrafficSignsTestCase(TestCase):
    def test_active_traffic_signs_show_result_1(self):
        # image = cv2.imread(f"{ROOT_FOLDER}/childrencrossing.jpg")
        image1 = cv2.imread(f"{ROOT_FOLDER}/sometrafficsigns1.jpg")
        image2 = cv2.imread(f"{ROOT_FOLDER}/notrafficsigns.jpg")
        active_traffic_signs = ActiveTrafficSigns()
        result_img = active_traffic_signs.update(image1)
        result_img = active_traffic_signs.update(image1)
        result_img = active_traffic_signs.update(image1)
        result_img = active_traffic_signs.update(image1)
        result_img = active_traffic_signs.update(image2)
        result_img = active_traffic_signs.update(image2)
        result_img = active_traffic_signs.update(image1)
        result_img = active_traffic_signs.update(image1)
        result_img = active_traffic_signs.update(image1)
        result_img = active_traffic_signs.update(image1)
        cv2.imshow("Active Traffic Signs", result_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
