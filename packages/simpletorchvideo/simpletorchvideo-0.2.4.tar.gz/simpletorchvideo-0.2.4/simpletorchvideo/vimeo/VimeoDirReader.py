import numpy as np
from simpletorchvideo.reader import VideoReader, DirectoryImageReader
from .util import *


class VimeoDirReader(VideoReader):
    def __init__(self, dir_path: str, include_list: [str]):
        """Read a Vimeo dataset directory. structure like sequences/<video index>/<slice index>/<image name>.png
        :param dir_path: path to vimeo dataset directory.
        :param include_list: include of vimeo dataset. format like content in vimeo_septuplet/sep_trainlist.txt, <video index>/<slice index>
        """
        super().__init__()
        self.reader = DirectoryImageReader(os.path.join(dir_path, "sequences"))
        self.include_list = sorted(include_list)
        assert self.valid(), "Not a valid Vimeo directory"

    def valid(self) -> bool:
        if not self.reader.valid():
            return False
        try:
            for p in self.include_list:
                if not self.reader.is_dir(p):
                    return False
            return True
        except:
            return False

    def read_images(self, paths: [str]) -> [np.ndarray]:
        return [self.reader.read_image(path) for path in paths]

    def list_videos(self) -> [[str]]:
        return parse_video_list_from_image_list(self.reader.list_images())
