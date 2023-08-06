import numpy as np
from simpletorchvideo.reader import VideoReader, ZipImageReader
from .util import *


class VimeoZipReader(VideoReader):
    def __init__(self, zip_path: str, include_list: [str]):
        """Read a Vimeo dataset zip file. structure like vimeo_septuplet/sequences/<video index>/<slice index>/<image name>.png
        :param zip_path: path to vimeo dataset zip file.
        :param include_list: include of vimeo dataset. format like content in vimeo_septuplet/sep_trainlist.txt, <video index>/<slice index>
        """
        super().__init__()
        self.reader = ZipImageReader(zip_path)
        self.include_list = sorted([self._format_path(p) for p in include_list])
        assert self.valid(), "Not a valid Vimeo zip"

    def valid(self) -> bool:
        if not self.reader.valid():
            return False
        try:
            if self.reader.getinfo('vimeo_septuplet/sequences/') is None:
                return False
            for p in self.include_list:
                if self.reader.getinfo('vimeo_septuplet/sequences/' + self._format_path(p) + '/') is None:
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
            self.reader.read_image('vimeo_septuplet/sequences/' + self._format_path(path), flag, channel_order, backend)
            for path in paths
        ]

    def list_videos(self) -> [[str]]:
        paths = []
        root = "vimeo_septuplet/sequences/"
        for include in self.include_list:
            paths.extend([p.replace(root, '') for p in self.reader.list_images(root + include)])
        return parse_video_list_from_image_list(paths)
