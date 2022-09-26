import pandas as pd

# Class names.
sign_names_df = pd.read_csv('resources/signnames.csv')
class_names = sign_names_df.SignName.tolist()


class InferResultList:
    def __init__(self):
        self.list = []

    def append(self, infer_result):
        self.list.append(infer_result)

    def infer_sum(self):
        infer_sum = 0
        for result in self.list:
            infer_sum += result.infer_time
        return infer_sum

    def __str__(self):
        str_list = []
        for result in self.list:
            str_list.append(str(result))
        return ', '.join(str_list)


class InferResult:
    def __init__(self, class_idx, top_prob, infer_time):
        self.class_idx = class_idx
        self.class_str = str(class_names[int(class_idx)])
        self.top_prob = top_prob
        self.infer_time = infer_time

    def __str__(self):
        return f"{self.class_str} ({self.top_prob*100:.2f}%, {self.infer_time:.4f}s)"
