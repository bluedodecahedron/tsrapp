from django.test import TestCase
from app.apps.tsdr import services
import cv2
from pycocotools.coco import COCO
import logging


logger = logging.getLogger('backend')


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
            # cv2.waitKey(0)

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
            f'False Positives: {false_positives}\n'
            f'False Negatives: {false_negatives}\n'
            f'Precision: {precision}\n'
            f'Recall: {recall}\n'
        )
        cv2.destroyAllWindows()