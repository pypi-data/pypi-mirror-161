import os

import cv2
import ffmpeg
import numpy as np

loglevel = 'error'


def read_video_sequence(path: str, start: int, stop: int, width: int, height: int):
    path = os.path.expanduser(path)
    process = (ffmpeg
               .input(path, loglevel=loglevel)
               .trim(start_frame=start, end_frame=stop)
               .setpts('PTS-STARTPTS')
               .output('pipe:', format='rawvideo', pix_fmt='rgb24')
               .run_async(pipe_stdout=True, pipe_stderr=False))
    out, err = process.communicate()
    if err:
        raise err
    return np.frombuffer(out, np.uint8).reshape([-1, height, width, 3])


def read_video_meta(path: str):
    path = os.path.expanduser(path)
    capture = cv2.VideoCapture(path)
    n_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    capture.release()
    return width, height, n_frames


if __name__ == "__main__":
    width, height, n_frames = read_video_meta("~/Videos/1080p.flv")
    print(width, height, n_frames)
    print(read_video_sequence("~/Videos/1080p.flv", 1012, 1080, width, height).shape)
