from simpletorchvideo.reader import ZipFolderReader


def Vid4ZipReader(zip_path: str, root: str):
    return ZipFolderReader(zip_path=zip_path, folder=root)


def Vid4ZipBIx4Reader(zip_path: str):
    return Vid4ZipReader(zip_path=zip_path, root='BIx4')


def Vid4ZipBDx4Reader(zip_path: str):
    return Vid4ZipReader(zip_path=zip_path, root='BDx4')


def Vid4ZipGTReader(zip_path: str):
    return Vid4ZipReader(zip_path=zip_path, root='GT')
