from django.test import TestCase
from app.apps.tsdr import services
from app.apps.tsdr.services import ActiveTrafficSigns, TsdrState
import cv2
from pycocotools.coco import COCO
import logging


logger = logging.getLogger('backend')
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
        cv2.waitKey(1)
        cv2.destroyAllWindows()

    def test_tsdr_show_result_2(self):
        image = cv2.imread(f"{ROOT_FOLDER}/manytrafficsigns2.jpg")
        class_ids, img = services.tsdr(image)
        cv2.imshow("TSDR Result", img)
        cv2.waitKey(1)
        cv2.destroyAllWindows()

    def test_tsdr_show_result_3(self):
        image = cv2.imread(f"{ROOT_FOLDER}/childrencrossing.jpg")
        class_ids, img = services.tsdr(image)
        cv2.imshow("TSDR Result", img)
        cv2.waitKey(1)
        cv2.destroyAllWindows()


class ActiveTrafficSignsTestCase(TestCase):
    def test_active_traffic_signs_show_result_1(self):
        # image = cv2.imread(f"{ROOT_FOLDER}/childrencrossing.jpg")
        image1 = cv2.imread(f"{ROOT_FOLDER}/manytrafficsigns1.jpg")
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
        cv2.waitKey(1)
        cv2.destroyAllWindows()


class TsdrStateTestCase(TestCase):
    def test_tsdr_state_show_result_1(self):
        # image = cv2.imread(f"{ROOT_FOLDER}/childrencrossing.jpg")
        image1 = cv2.imread(f"{ROOT_FOLDER}/manytrafficsigns1.jpg")
        image2 = cv2.imread(f"{ROOT_FOLDER}/notrafficsigns.jpg")
        tsdr_state = TsdrState()
        result_img = tsdr_state.update(image1)
        result_img = tsdr_state.update(image1)
        result_img = tsdr_state.update(image1)
        result_img = tsdr_state.update(image1)
        result_img = tsdr_state.update(image2)
        result_img = tsdr_state.update(image2)
        result_img = tsdr_state.update(image1)
        result_img = tsdr_state.update(image1)
        result_img = tsdr_state.update(image1)
        result_img = tsdr_state.update(image1)
        tsdr_state.release()
        cv2.imshow("Active Traffic Signs", result_img)
        cv2.waitKey(1)
        cv2.destroyAllWindows()

class TsdrGtsdbValidationTestCase(TestCase):
    dataType = 'valid'
    imgDir = f'resources/valid'
    annFile = f'resources/valid/_annotations.coco.json'

    def setUp(self):
        # initialize COCO api for instance annotations
        self.coco = COCO(TsdrGtsdbValidationTestCase.annFile)

    def test_display_coco_categories(self):
        # display COCO categories and supercategories
        cats = self.coco.loadCats(self.coco.getCatIds())
        nms = [cat['name'] for cat in cats]
        print('COCO categories: \n{}\n'.format(' '.join(nms)))
        nms = set([cat['supercategory'] for cat in cats])
        print('COCO supercategories: \n{}'.format(' '.join(nms)))

    def test_tsdr_gtsdb_validation(self):
        true_positives = 0
        false_positives = 0
        false_negatives = 0

        for imgId in self.coco.imgs:
            catData = self.coco.loadCats(self.coco.cats)
            imgData = self.coco.loadImgs(ids=[imgId])
            imgAnnIds = self.coco.getAnnIds(imgIds=[imgId])
            imgAnns = self.coco.loadAnns(ids=imgAnnIds)
            class_ids_gt = []
            for imgAnn in imgAnns:
                cat = imgAnn['category_id']
                class_id = int(catData[cat]['name'])
                class_ids_gt.append(class_id)

            img = cv2.imread(f"{TsdrGtsdbValidationTestCase.imgDir}/{imgData[0]['file_name']}")
            class_ids_pd, img = services.tsdr(img)

            # cv2.imshow("prediction", img)
            # cv2.waitKey(1)

            combined_set = set(class_ids_gt)
            combined_set.update(class_ids_pd)
            for class_id in combined_set:
                if (class_id in class_ids_gt) and (class_id in class_ids_pd):
                    true_positives += 1
                elif class_id in class_ids_pd:
                    false_positives += 1
                elif class_id in class_ids_gt:
                    false_negatives += 1

        precision = true_positives / (true_positives + false_positives)
        recall = true_positives / (true_positives + false_negatives)
        logger.info(
            f'Results:\n'
            f'True Positives: {true_positives}\n'
            f'True False Positives: {false_positives}\n'
            f'True False Negatives: {false_negatives}\n'
            f'Precision: {precision}\n'
            f'Recall: {recall}\n'
        )
        cv2.destroyAllWindows()
