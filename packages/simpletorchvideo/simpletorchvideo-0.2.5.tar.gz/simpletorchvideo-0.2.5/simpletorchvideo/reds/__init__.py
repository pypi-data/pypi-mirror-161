from .REDSZipReader import REDSZipReader
from .REDSZipReader import REDSZipReader_for_train_LR, REDSZipReader_for_train_HR
from .REDSZipReader import REDSZipReader_for_val_LR, REDSZipReader_for_val_HR


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
