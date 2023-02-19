import cv2
import numpy as np
import yolox.tools.infer_result as TSDResult
from tsrresnet.tools.infer_result import ResultList as TSRResultList


class TsdrResult:
    def __init__(self, tsd_result: TSDResult, tsr_result_list: TSRResultList):
        self.tsd_result = tsd_result
        self.tsr_result_list = tsr_result_list

    def visual(self):
        if self.tsd_result.output is None:
            return self.tsd_result.img_copy()

        tsd_box_borders = self.tsd_result.box_borders
        img = self.tsd_result.img_copy()
        tsd_ids = self.tsd_result.classes
        tsd_probs = self.tsd_result.scores
        tsd_conf = self.tsd_result.confthre
        tsd_names = self.tsd_result.cls_names
        tsr_ids = self.tsr_result_list.get_class_ids()
        tsr_probs = self.tsr_result_list.get_class_probs()
        tsr_names = self.tsr_result_list.cls_names
        tsr_conf = self.tsr_result_list.confthre
        vis_res = self.vis(img, tsd_box_borders, tsd_ids, tsd_probs, tsd_names, tsd_conf, tsr_ids, tsr_probs, tsr_names, tsr_conf)
        return vis_res

    def vis(self, img, tsd_box_borders, tsd_ids, tsd_probs, tsd_names, tsd_conf, tsr_ids, tsr_probs, tsr_names, tsr_conf):

        for i in range(len(tsd_box_borders)):
            box = tsd_box_borders[i]
            tsd_prob = tsd_probs[i]
            tsd_id = int(tsd_ids[i])
            tsr_id = tsr_ids[i]
            tsr_prob = tsr_probs[i]
            if tsd_prob < tsd_conf:
                continue
            x0 = int(box[0])
            y0 = int(box[1])
            x1 = int(box[2])
            y1 = int(box[3])

            rec_color = (_COLORS[tsr_id] * 255).astype(np.uint8).tolist()
            alt_rec_color =  (_COLORS[79] * 255).astype(np.uint8).tolist()
            tsd_text = '{}: {:.1f}%'.format(tsd_names[tsd_id], tsd_prob * 100)
            tsr_text = '{}: {:.1f}%'.format(tsr_names[tsr_id], tsr_prob * 100)
            alt_text = 'Unknown'
            txt_color = (0, 0, 0) if np.mean(_COLORS[tsr_id]) > 0.5 else (255, 255, 255)
            alt_color = (0, 0, 0) if np.mean(_COLORS[79]) > 0.5 else (255, 255, 255)
            font = cv2.FONT_HERSHEY_SIMPLEX

            tsd_txt_size = cv2.getTextSize(tsd_text, font, 0.4, 1)[0]
            tsr_txt_size = cv2.getTextSize(tsr_text, font, 0.4, 1)[0]
            txt_length = tsd_txt_size[0] if tsd_txt_size[0] > tsr_txt_size[0] else tsr_txt_size[0]
            txt_height = tsd_txt_size[1]

            txt_bk_color = (_COLORS[tsr_id] * 255 * 0.7).astype(np.uint8).tolist()
            alt_bk_color = (_COLORS[79] * 255 * 0.7).astype(np.uint8).tolist()

            if tsr_id != len(tsr_names)-1:
                cv2.rectangle(img, (x0, y0), (x1, y1), rec_color, 2)
                cv2.rectangle(
                    img,
                    (x0, y0 - int(3.0*txt_height)),
                    (x0 + txt_length + 1, y0),
                    txt_bk_color,
                    -1
                )
                cv2.putText(img, tsd_text, (x0, y0 - int(2.0*txt_height)), font, 0.4, txt_color, thickness=1)
                cv2.putText(img, tsr_text, (x0, y0 - int(0.5*txt_height)), font, 0.4, txt_color, thickness=1)
            else:
                cv2.rectangle(img, (x0, y0), (x1, y1), alt_rec_color, 2)
                cv2.rectangle(
                    img,
                    (x0, y0 - int(3.0*txt_height)),
                    (x0 + txt_length + 1, y0),
                    alt_bk_color,
                    -1
                )
                cv2.putText(img, tsd_text, (x0, y0 - int(2.0*txt_height)), font, 0.4, alt_color, thickness=1)
                cv2.putText(img, alt_text, (x0, y0 - int(0.5*txt_height)), font, 0.4, alt_color, thickness=1)

        return img


_COLORS = np.array(
    [
        0.000, 0.447, 0.741,
        0.850, 0.325, 0.098,
        0.929, 0.694, 0.125,
        0.494, 0.184, 0.556,
        0.466, 0.674, 0.188,
        0.301, 0.745, 0.933,
        0.635, 0.078, 0.184,
        0.300, 0.300, 0.300,
        0.600, 0.600, 0.600,
        1.000, 0.000, 0.000,
        1.000, 0.500, 0.000,
        0.749, 0.749, 0.000,
        0.000, 1.000, 0.000,
        0.000, 0.000, 1.000,
        0.667, 0.000, 1.000,
        0.333, 0.333, 0.000,
        0.333, 0.667, 0.000,
        0.333, 1.000, 0.000,
        0.667, 0.333, 0.000,
        0.667, 0.667, 0.000,
        0.667, 1.000, 0.000,
        1.000, 0.333, 0.000,
        1.000, 0.667, 0.000,
        1.000, 1.000, 0.000,
        0.000, 0.333, 0.500,
        0.000, 0.667, 0.500,
        0.000, 1.000, 0.500,
        0.333, 0.000, 0.500,
        0.333, 0.333, 0.500,
        0.333, 0.667, 0.500,
        0.333, 1.000, 0.500,
        0.667, 0.000, 0.500,
        0.667, 0.333, 0.500,
        0.667, 0.667, 0.500,
        0.667, 1.000, 0.500,
        1.000, 0.000, 0.500,
        1.000, 0.333, 0.500,
        1.000, 0.667, 0.500,
        1.000, 1.000, 0.500,
        0.000, 0.333, 1.000,
        0.000, 0.667, 1.000,
        0.000, 1.000, 1.000,
        0.333, 0.000, 1.000,
        0.333, 0.333, 1.000,
        0.333, 0.667, 1.000,
        0.333, 1.000, 1.000,
        0.667, 0.000, 1.000,
        0.667, 0.333, 1.000,
        0.667, 0.667, 1.000,
        0.667, 1.000, 1.000,
        1.000, 0.000, 1.000,
        1.000, 0.333, 1.000,
        1.000, 0.667, 1.000,
        0.333, 0.000, 0.000,
        0.500, 0.000, 0.000,
        0.667, 0.000, 0.000,
        0.833, 0.000, 0.000,
        1.000, 0.000, 0.000,
        0.000, 0.167, 0.000,
        0.000, 0.333, 0.000,
        0.000, 0.500, 0.000,
        0.000, 0.667, 0.000,
        0.000, 0.833, 0.000,
        0.000, 1.000, 0.000,
        0.000, 0.000, 0.167,
        0.000, 0.000, 0.333,
        0.000, 0.000, 0.500,
        0.000, 0.000, 0.667,
        0.000, 0.000, 0.833,
        0.000, 0.000, 1.000,
        0.000, 0.000, 0.000,
        0.143, 0.143, 0.143,
        0.286, 0.286, 0.286,
        0.429, 0.429, 0.429,
        0.571, 0.571, 0.571,
        0.714, 0.714, 0.714,
        0.857, 0.857, 0.857,
        0.000, 0.447, 0.741,
        0.314, 0.717, 0.741,
        0.0, 0.0, 0
    ]
).astype(np.float32).reshape(-1, 3)
