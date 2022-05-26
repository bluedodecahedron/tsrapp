import os


class ImageList:
    def __init__(self, path_source, prefix_to_add):
        self._path_source = path_source
        self._prefix_to_add = prefix_to_add
        self._list = []
        self._create_list()

    def _create_list(self):
        filelist = os.listdir(self._path_source)
        filelist.sort()
        for filename in filelist:
            if filename.split('.')[1] == 'jpg':
                self._list.append(self._prefix_to_add + filename)

    def __str__(self):
        return str(self._list)

    def create_file(self, filepath):
        with open(filepath, 'w') as f:
            f.write('\n'.join(self._list) + '\n')
            f.close()
