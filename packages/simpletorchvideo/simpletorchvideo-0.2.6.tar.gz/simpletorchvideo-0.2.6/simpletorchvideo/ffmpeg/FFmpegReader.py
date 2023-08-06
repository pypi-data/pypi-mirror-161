import os
import numpy as np
from simpletorchvideo.reader.util import VideoReader
from .ffmpeg import read_video_meta, read_video_sequence


class FFmpegReader(VideoReader):
    def __init__(self, videos: [str]):
        """Read data with ffmpeg
        :param videos: paths of the videos
        """
        super().__init__()
        self.paths = sorted(os.path.expanduser(path) for path in videos)
        assert self.valid(), "Hot a valid FFmpegReader"

    def valid(self) -> bool:
        try:
            for path in self.paths:
                _, _, _ = read_video_meta(path)
            return True
        except:
            return False

    @staticmethod
    def split_video_path(path: str):
        """split the path like <video path>/<frame index>
        :param path: path of the frame. Format: <video path>/<frame index>. e.g. such as: folder/some-video.mp4/03
        :returns (<video path>, <frame index>)
        """
        path = os.path.expanduser(path)
        frame_pos = int(os.path.basename(path))
        video_path = os.path.dirname(path)
        return video_path, frame_pos

    def read_images(self, paths: [str]) -> [np.ndarray]:
        """Read images using ffmpeg from video file.
        :param paths: paths of the images. Format: <video path>/<frame index>. e.g. such as: folder/some-video.mp4/03
        :returns array: (H, W, C) BGR image.
        """
        if len(paths) == 0:
            return []
        video_path, start = self.split_video_path(paths[0])
        stop = start
        for path in paths[1:]:
            vpath, pos = self.split_video_path(path)
            assert vpath == video_path, "should not read from other video!"
            assert pos == stop + 1, "should be a sequence"
            stop = pos
        width, height, n_frames = read_video_meta(video_path)
        assert n_frames > stop, "max frame num is %d!" % n_frames
        frames = read_video_sequence(video_path, start, stop + 1, width, height)
        return [frames[i, :, :] for i in range(frames.shape[0])]

    def list_videos(self) -> [[str]]:
        paths = []
        for path in self.paths:
            _, _, n_frames = read_video_meta(path)
            paths.append([os.path.join(path, "%08d" % i) for i in range(n_frames)])
        return paths
