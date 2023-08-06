import abc
import numpy as np


class VideoReader(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def valid(self) -> bool:
        pass

    @abc.abstractmethod
    def read_images(self, paths: [str]) -> [np.ndarray]:
        pass

    @abc.abstractmethod
    def list_videos(self) -> [[str]]:
        pass


class VideoReaderList(VideoReader):
    """A series of VideoReader, different image output but same image name"""

    def __init__(self, *args: VideoReader):
        self.readers = args
        assert self.valid(), "Not a valid VideoReaderList"

    def valid(self):
        if len(self.readers):
            return True
        l0 = self.readers[0].list_videos()
        for reader in self.readers[1:]:
            if l0 != reader.list_videos():
                return False
        return True

    def list_videos(self) -> [[str]]:
        return self.readers[0].list_videos()

    def read_images(self, paths: [str]) -> [(np.ndarray,)]:
        return list(reader.read_images(paths) for reader in self.readers)
