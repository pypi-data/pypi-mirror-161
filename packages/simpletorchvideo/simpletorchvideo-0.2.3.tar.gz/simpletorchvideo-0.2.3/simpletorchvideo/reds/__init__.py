from .REDSZipReader import REDSZipReader


def REDSReader(path: str, root: str):
    """
    Construct a vimeo dataset.
    :param path: path to REDS dataset zip file.
    :param root: path to REDS dataset file in zip. its sub dir should be <video index>/<frame index>.png. e.g. "test/test_sharp_bicubic/X4" in test_sharp_bicubic.zip
    :return: a simpletorchvideo.reader.VideoReader
    """
    reader = None
    try:
        reader = REDSZipReader(path, root)
    except:
        pass
    assert reader is not None, "%s is not a valid REDS dataset" % path
    return reader
