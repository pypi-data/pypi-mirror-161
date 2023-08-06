import os
import numpy as np
from .util import VideoReader
from .ZipReader import ZipImageReader


def parse_video_list_from_image_list(image_list: [str]) -> [[str]]:
    video_last = ''
    video_list = []
    for path in sorted(image_list):
        video = os.path.dirname(path)
        if not video == video_last:
            video_list.append([])
            video_last = video
        video_list[-1].append(path)
    return video_list


class ZipFolderReader(VideoReader):
    def __init__(self, zip_path: str, folder: str):
        """Read a REDS dataset zip file.
        :param zip_path: path to dataset zip file.
        :param folder: path to dataset file in zip. its sub dir should be <video index>/<frame index>.png. e.g. "test/test_sharp_bicubic/X4" in test_sharp_bicubic.zip
        """
        super().__init__()
        self.reader = ZipImageReader(zip_path)
        self.root = self._format_path(folder) + '/'
        assert self.valid(), "Not a valid REDS zip"

    def valid(self) -> bool:
        if not self.reader.valid():
            return False
        try:
            if self.reader.getinfo(self.root) is None:
                return False
            return True
        except:
            return False

    @staticmethod
    def _format_path(path):
        path = path.replace("\\", "/")
        path = path[1:] if path[0] == "/" else path
        path = path[0:-1] if path[-1] == "/" else path
        return path

    def read_images(self, paths: (str, [str]), flag='unchanged', channel_order='bgr', backend=None) -> [np.ndarray]:
        assert isinstance(paths, (str, list)), 'Paths must be a list or str type!'
        if isinstance(paths, str):
            paths = [paths]
        return [
            self.reader.read_image(self.root + self._format_path(path), flag, channel_order, backend)
            for path in paths
        ]

    def list_videos(self) -> [[str]]:
        return parse_video_list_from_image_list([p.replace(self.root, '') for p in self.reader.list_images(self.root)])
