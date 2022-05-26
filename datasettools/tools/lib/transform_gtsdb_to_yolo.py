from PIL import Image

import os
import csv


# transform images from source path (creates new image files in target path)
# transform labels in csv file from source filepath (creates new label files in target path)
# parameter files_to_use is a list of integers identifying the files to use
class Transform:
    def __init__(self,
                 img_path_source,
                 img_path_target,
                 label_filepath_source,
                 label_path_target,
                 img_extension_source,
                 img_extension_target,
                 label_extension_target,
                 files_to_use
                 ):
        self._img_path_source = img_path_source
        self._img_path_target = img_path_target
        self._label_filepath_source = label_filepath_source
        self._label_path_target = label_path_target
        self._img_extension_source = img_extension_source
        self._img_extension_target = img_extension_target
        self._label_extension_target = label_extension_target
        self._files_to_use = files_to_use
        self._check_files_exist()

    def execute(self):
        self._make_dirs()

        labels_source = LabelsSource(self._label_filepath_source)
        file_list = os.listdir(self._img_path_source)
        for i in self._files_to_use:
            filename_source = file_list[i]
            file_basename_source = filename_source.split('.')[0]

            if '.' + filename_source.split('.')[1] == self._img_extension_source:
                img = ImageFileTransform(
                    self._img_path_source,
                    self._img_path_target,
                    file_basename_source,
                    file_basename_source,
                    self._img_extension_source,
                    self._img_extension_target
                ).execute()
                LabelFileTransform(
                    labels_source,
                    file_basename_source,
                    file_basename_source,
                    self._label_path_target,
                    self._label_extension_target,
                    img.size[0],
                    img.size[1]
                ).execute()
            else:
                print('Ignoring file because it does not have the right extension: ' + filename_source)

    def _check_files_exist(self):
        file_list = os.listdir(self._img_path_source)
        if max(self._files_to_use) > len(file_list):
            raise RuntimeError('Invalid integers in files_to_use: '
                               + str(max(self._files_to_use))
                               + ' is greater than number of files.')

    def _make_dirs(self):
        os.makedirs(self._img_path_target, exist_ok=True)
        os.makedirs(self._label_path_target, exist_ok=True)


# transforms the image with basename (creates new image file with basename in target path)
class ImageFileTransform:
    def __init__(self, path_source, path_target, basename_source, basename_target, extension_source, extension_target):
        self._path_source = path_source
        self._path_target = path_target
        self._basename_source = basename_source
        self._basename_target = basename_target
        self._extension_source = extension_source
        self._extension_target = extension_target

    def execute(self):
        filename_source = self._basename_source + self._extension_source
        filepath_source = self._path_source + filename_source
        filename_target = self._basename_target + self._extension_target
        filepath_target = self._path_target + filename_target

        img = Image.open(filepath_source)
        try:
            os.remove(filepath_target)
        except FileNotFoundError:
            pass

        img.save(filepath_target)
        print('Successfully transformed image ' + filename_source + ' to ' + filename_target)
        return img


# transforms the label for image with basename (creates new label file with basename in target path)
class LabelFileTransform:
    def __init__(self, labels_source, basename_source, basename_target, path_target, extension_target, img_width, img_height):
        self._labels_source = labels_source
        self._basename_source = basename_source
        self._basename_target = basename_target
        self._path_target = path_target
        self._extension_target = extension_target
        self._img_width = img_width
        self._img_height = img_height
        self._labels_target = self._transform_labels()

    def execute(self):
        label = '\n'.join(self._labels_target + [''])

        label_filepath_target = self._path_target + self._basename_target + self._extension_target
        with open(label_filepath_target, 'w') as f:
            f.write(label)
            f.close()

        print('Successfully added labels to ' + self._basename_target + self._extension_target + ':\n' + label)

    def _transform_labels(self):
        labels_target = []
        for label in self._labels_source.get(self._basename_source):
            label_target = str(LabelTarget(label, self._img_width, self._img_height))
            labels_target.append(label_target)

        return labels_target


# reads source labels from the csv file in source filepath
# get(basename) returns labels for image with basename (name without extension)
class LabelsSource:
    def __init__(self, filepath_source):
        self._filepath_source = filepath_source
        self._labels = {}
        self._read()

    def _read(self):
        with open(self._filepath_source, newline='') as csvfile:
            spam_reader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in spam_reader:
                basename_source = row[0].split('.')[0]
                label = LabelSource(int(row[1]), int(row[2]), int(row[3]), int(row[4]), row[5])

                if basename_source in self._labels:
                    self._labels[basename_source].append(label)
                else:
                    self._labels[basename_source] = [label]

    def get(self, basename_source):
        if basename_source in self._labels:
            return self._labels[basename_source]
        else:
            return []


# defines source label schema
class LabelSource:
    def __init__(self, left_col, top_row, right_col, bottom_row, clas):
        self.left_col = left_col
        self.top_row = top_row
        self.right_col = right_col
        self.bottom_row = bottom_row
        self.clas = clas

    def __str__(self):
        return str(self.left_col) + ' ' + str(self.top_row) + ' ' + str(self.right_col) + ' ' + str(
            self.bottom_row) + ' ' + str(self.clas)


# defines target label schema
class LabelTarget:
    def __init__(self, label_source, img_width, img_height):
        self.clas = label_source.clas

        self.x_center = (label_source.left_col + label_source.right_col) // 2
        self.y_center = (label_source.bottom_row + label_source.top_row) // 2
        self.width = label_source.right_col - label_source.left_col
        self.height = label_source.bottom_row - label_source.top_row

        self.x_center = self.x_center / img_width
        self.y_center = self.y_center / img_height
        self.width = self.width / img_width
        self.height = self.height / img_height

    def __str__(self):
        return str(self.clas) + ' ' + str(self.x_center) + ' ' + str(self.y_center) + ' ' + str(self.width) + ' ' + str(
            self.height)