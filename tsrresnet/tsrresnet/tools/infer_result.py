import pandas as pd


class InferResult:
    def __init__(self, classes_path):
        sign_names_df = pd.read_csv(classes_path)
        self.class_names = sign_names_df.SignName.tolist()
        self.class_names.append('Unknown')

    def result_list(self):
        return ResultList(self.class_names)

    def result(self, class_idx, top_prob, infer_time, confthre, q_index=0):
        return Result(self.class_names, class_idx, top_prob, infer_time, confthre, q_index=q_index)


class ResultList:
    def __init__(self, class_names, multi_time=0.0):
        self.list = []
        self.cls_names = class_names
        self.confthre = 0.0
        self.multi_time = multi_time

    def append(self, infer_result):
        self.list.append(infer_result)
        self.confthre = infer_result.confthre

    def infer_sum(self):
        infer_sum = 0
        for result in self.list:
            infer_sum += result.infer_time
        return infer_sum

    def get_class_ids(self):
        class_list = []
        for result in self.list:
            class_list.append(result.class_idx)
        return class_list

    def get_class_probs(self):
        prob_list = []
        for result in self.list:
            prob_list.append(result.top_prob)
        return prob_list

    def set_multi_time(self, multi_time):
        self.multi_time = multi_time

    def sort_by_qindex(self):
        self.list.sort(key=lambda x: x.q_index)

    def __str__(self):
        str_list = []
        for result in self.list:
            str_list.append(str(result))
        return ', '.join(str_list)


class Result:
    def __init__(self, class_names, class_idx, top_prob, infer_time, confthre, q_index=0):
        self.cls_names = class_names
        self.class_idx = class_idx
        self.class_str = str(class_names[class_idx])
        self.top_prob = top_prob
        self.infer_time = infer_time
        self.confthre = confthre
        self.q_index = q_index

    def __str__(self):
        return f"{self.class_str} ({self.top_prob*100:.2f}%, {self.infer_time:.4f}s)"