from .VimeoDirReader import VimeoDirReader
from .VimeoZipReader import VimeoZipReader


def VimeoReader(path: str, include_list: [str]):
    """
    Construct a vimeo dataset.
    :param path: Could be path to a vimeo_septuplet.zip or a vimeo_septuplet directory
    if a vimeo_septuplet.zip, structure in zip should like vimeo_septuplet/sequences/<video index>/<slice index>/<image name>.png
    if a vimeo_septuplet directory structure in dir should  like sequences/<video index>/<slice index>/<image name>.png
    :param include_list: include of vimeo dataset. format like content in vimeo_septuplet/sep_trainlist.txt, <video index>/<slice index>
    :return: a simpletorchvideo.reader.VideoReader
    """
    reader = None
    try:
        reader = VimeoDirReader(path, include_list)
    except:
        pass
    try:
        reader = VimeoZipReader(path, include_list)
    except:
        pass
    assert reader is not None, "%s is not a valid vimeo dataset" % path
    return reader
