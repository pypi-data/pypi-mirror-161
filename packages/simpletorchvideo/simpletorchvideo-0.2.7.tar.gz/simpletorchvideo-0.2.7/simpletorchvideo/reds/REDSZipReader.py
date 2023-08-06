from simpletorchvideo.reader import ZipFolderReader


def REDSZipReader(zip_path: str, root: str):
    return ZipFolderReader(zip_path=zip_path, folder=root)


def REDSZipReader_for_train_LR(zip_path: str):
    return REDSZipReader(zip_path=zip_path, root='train/train_sharp_bicubic/X4')


def REDSZipReader_for_train_HR(zip_path: str):
    return REDSZipReader(zip_path=zip_path, root='train/train_sharp')


def REDSZipReader_for_val_LR(zip_path: str):
    return REDSZipReader(zip_path=zip_path, root='val/val_sharp_bicubic/X4')


def REDSZipReader_for_val_HR(zip_path: str):
    return REDSZipReader(zip_path=zip_path, root='val/val_sharp')
