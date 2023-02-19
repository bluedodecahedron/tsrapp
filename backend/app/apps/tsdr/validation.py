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


class VideoTestCase(TestCase):
    FRAME_DIM = 800
    vid_dir = 'resources/videos'
    vid1 = 'Zurich_back_highway_parking_street.mp4'
    vid2 = 'Zurich_sun.mp4'
    vid3 = 'Inssi Dashcam Footage.mp4'
    vid4 = 'Inssi short.mp4'

    def resize(self, image):
        height, width, _ = image.shape
        scale = self.FRAME_DIM / max(width, height)
        width = int(width * scale)
        height = int(height * scale)

        image = cv2.resize(image, (width, height))
        return image

    def test_video(self):
        for vid in [self.vid4, self.vid3, self.vid2, self.vid1]:
            vidcap = cv2.VideoCapture(f'{self.vid_dir}/{vid}')
            video_fps = vidcap.get(cv2.CAP_PROP_FPS)
            skip_frames = False
            if video_fps > 15:
                video_fps = int(video_fps/2)
                skip_frames = True
            self.tsdr_state = services.TsdrState(video_fps=video_fps)
            success, image = vidcap.read()
            count = 1
            while success:
                if skip_frames and (count % 2 == 0):
                    pass
                else:
                    image = self.resize(image)
                    self.tsdr_state.update(image)
                success, image = vidcap.read()
                count += 1
            self.tsdr_state.release()
