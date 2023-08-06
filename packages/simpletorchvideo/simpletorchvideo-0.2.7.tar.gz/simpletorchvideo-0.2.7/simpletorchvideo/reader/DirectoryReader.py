import os

import cv2


class DirectoryImageReader:
    def __init__(self, root: str):
        """Read image file from directory
        :param root: root of the directory
        """
        super().__init__()
        self.root = os.path.expanduser(root)
        assert self.valid(), "Not a valid DirectoryImageReader"

    def valid(self) -> bool:
        return os.path.isdir(self.root)

    def read_image(self, path: str):
        """Read a image from the directory.
        :param path: path of the file in directory
        :returns array: (H, W, C) BGR image.
        """
        path = path[1:] if path[0] == "/" or path[0] == "\\" else path
        return cv2.imread(os.path.join(self.root, path), cv2.IMREAD_COLOR)

    def list_images(self, path: str = None) -> [str]:
        """List images in the dir.
        :param path: path of the dir
        :returns paths of the image files in the dir, include sub dir
        """
        if path is None or len(path) <= 0:
            root = self.root
        else:
            path = path[1:] if path[0] == "/" or path[0] == "\\" else path
            root = os.path.join(self.root, path)
        images = []
        for top, dirs, files in os.walk(root):
            for file in files:
                abspath = os.path.join(top, file)
                # if filetype.is_image(abspath): # should check, but cost too much time
                images.append(os.path.relpath(abspath, root))
        return images

    def is_dir(self, path: str):
        return os.path.isdir(os.path.join(self.root, path))
