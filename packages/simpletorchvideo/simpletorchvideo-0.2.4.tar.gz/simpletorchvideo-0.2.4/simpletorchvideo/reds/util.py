import os


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
