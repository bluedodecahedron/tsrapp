import os
import shutil


def sort_files(path_source):
    files = os.listdir(path_source)
    #sorted_files = sorted(files, key=lambda x: int(x.split('_')[1]))
    sorted_files = sorted(files)
    return sorted_files


def list_files(path_source):
    for f in sort_files(path_source):
        print(f)


def rename_files(path_source, path_target):
    os.makedirs(path_target, exist_ok=True)

    i = 0
    for filename in sort_files(path_source):
        splits = filename.split('.')
        if splits[len(splits)-1] == 'jpg':
            i = i + 1
            filepath_source = path_source + '/' + filename
            filepath_target = path_target + '/' + 'gtsdbtest' + str(i) + '.jpg'

            shutil.copyfile(filepath_source, filepath_target)
            print('Renamed ' + filepath_source + ' to ' + filepath_target)
