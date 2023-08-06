import logging
import random

from torch.utils.data import Dataset

from .reader import VideoReader

logger = logging.getLogger('VideoDataset')


class VideoDataset(Dataset):
    """
    Reading the training Vimeo dataset
    key example: train/00001/0001/im1.png
    """

    def __init__(self, video_reader: VideoReader, num_frames=7):
        super(VideoDataset, self).__init__()
        self.reader = video_reader
        self.video_list = self.reader.list_videos()
        if isinstance(num_frames, int):
            self.num_frames = num_frames
            self.len = sum([len(video) // num_frames for video in self.video_list])
        else:
            self.num_frames = None
            self.len = len(self.video_list)

    def __len__(self):
        return self.len

    def __getitem__(self, index):
        if isinstance(self.num_frames, int):
            return self.get_clip(index)
        else:
            return self.get_video(index)

    def get_video(self, index):
        logger.debug("Reading video: %s" % self.video_list[index])
        return self.reader.read_images(self.video_list[index])

    def get_clip(self, index):
        frame_index = index * self.num_frames

        # Get frame list
        for i in range(len(self.video_list)):
            if 0 <= frame_index <= len(self.video_list[i]) - self.num_frames:
                image_paths = self.video_list[i][frame_index:frame_index + self.num_frames]
                logger.debug("Reading images: %s" % image_paths)
                return self.reader.read_images(image_paths)
            else:
                frame_index = frame_index - (len(self.video_list[i]) - len(self.video_list[i]) % self.num_frames)
