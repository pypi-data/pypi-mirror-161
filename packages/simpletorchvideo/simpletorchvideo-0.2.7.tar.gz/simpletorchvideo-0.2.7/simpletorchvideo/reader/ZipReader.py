import logging
import os
import zipfile
import cv2
from cv2 import (IMREAD_COLOR, IMREAD_GRAYSCALE, IMREAD_IGNORE_ORIENTATION, IMREAD_UNCHANGED)
import numpy as np
import io

jpeg = None
supported_backends = ['cv2', 'pillow', 'tifffile']
imread_flags = {
    'color': IMREAD_COLOR,
    'grayscale': IMREAD_GRAYSCALE,
    'unchanged': IMREAD_UNCHANGED,
    'color_ignore_orientation': IMREAD_IGNORE_ORIENTATION | IMREAD_COLOR,
    'grayscale_ignore_orientation':
        IMREAD_IGNORE_ORIENTATION | IMREAD_GRAYSCALE
}
imread_backend = 'cv2'
try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None

try:
    import tifffile
except ImportError:
    tifffile = None

logger = logging.getLogger('base')

global_zipfiles = {}


class ZipImageReader:
    def __init__(self, path: str):
        """Read data from zip
        :param path: path of the zip file
        """
        super().__init__()
        self.path = os.path.expanduser(path)
        assert self.valid(), "Not a valid ZipReader"
        self.dir_struct = None

    def valid(self) -> bool:
        return zipfile.is_zipfile(self.path)

    @staticmethod
    def _format_path(path):
        path = path.replace("\\", "/")
        path = path[1:] if path[0] == "/" else path
        path = path[0:-1] if path[-1] == "/" else path
        return path

    def read_image(self, path: str, flag='unchanged', channel_order='bgr', backend=None):
        """Read a file from a zip, and custom the image, ref from mmcv.imfrombytes
        Args:
            path (str): path of the file in zip
            flag (str): Loading flag for images. Default: 'unchanged'.
            channel_order (str): Order of channel, candidates are 'bgr' and 'rgb'.
                Default: 'bgr'.
            backend (str): The image loading backend type. Options are `cv2`,
                `pillow`, and 'turbojpeg'. Default: None.
            :returns buffer-like file content
        Returns:
            ndarray: Loaded image array.
        """
        path = self._format_path(path)
        self._prepare_zip()
        try:
            img_bytes = global_zipfiles[self.path].read(path)
        except zipfile.BadZipFile:
            global_zipfiles[self.path].close()
            logger.debug("Reopen zip file: %s" % self.path)
            global_zipfiles[self.path] = zipfile.ZipFile(self.path, "r")
            img_bytes = global_zipfiles[self.path].read(path)
        return self._image_from_bytes(img_bytes,
                                      flag=flag,
                                      channel_order=channel_order,
                                      backend=backend)

    def _image_from_bytes(self, img_bytes, flag, channel_order, backend):
        if backend is None:
            backend = imread_backend
        if backend not in supported_backends:
            raise ValueError(f'backend: {backend} is not supported. Supported '
                             "backends are 'cv2', 'pillow', 'tifffile'")
        if backend == 'pillow':
            with io.BytesIO(img_bytes) as buff:
                img = Image.open(buff)
                img = self._pillow2array(img, flag, channel_order)
            return img
        elif backend == 'tifffile':
            with io.BytesIO(img_bytes) as buff:
                img = tifffile.imread(buff)
            return img
        else:
            img_np = np.frombuffer(img_bytes, np.uint8)
            flag = imread_flags[flag] if isinstance(flag, str) else flag
            img = cv2.imdecode(img_np, flag)
            if flag == IMREAD_COLOR and channel_order == 'rgb':
                cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img)
            return img

    @staticmethod
    def _pillow2array(img, flag='unchanged', channel_order='bgr'):
        """Convert a pillow image to numpy array.

        Args:
            img (:obj:`PIL.Image.Image`): The image loaded using PIL
            flag (str): Flags specifying the color type of a loaded image,
                candidates are 'color', 'grayscale' and 'unchanged'.
                Default to 'unchanged'.
            channel_order (str): The channel order of the output image array,
                candidates are 'bgr' and 'rgb'. Default to 'bgr'.

        Returns:
            np.ndarray: The converted numpy array
        """
        channel_order = channel_order.lower()
        if channel_order not in ['rgb', 'bgr']:
            raise ValueError('channel order must be either "rgb" or "bgr"')

        if flag == 'unchanged':
            array = np.array(img)
            if array.ndim >= 3 and array.shape[2] >= 3:  # color image
                array[:, :, :3] = array[:, :, (2, 1, 0)]  # RGB to BGR
        else:
            # Handle exif orientation tag
            if flag in ['color', 'grayscale']:
                img = ImageOps.exif_transpose(img)
            # If the image mode is not 'RGB', convert it to 'RGB' first.
            if img.mode != 'RGB':
                if img.mode != 'LA':
                    # Most formats except 'LA' can be directly converted to RGB
                    img = img.convert('RGB')
                else:
                    # When the mode is 'LA', the default conversion will fill in
                    #  the canvas with black, which sometimes shadows black objects
                    #  in the foreground.
                    #
                    # Therefore, a random color (124, 117, 104) is used for canvas
                    img_rgba = img.convert('RGBA')
                    img = Image.new('RGB', img_rgba.size, (124, 117, 104))
                    img.paste(img_rgba, mask=img_rgba.split()[3])  # 3 is alpha
            if flag in ['color', 'color_ignore_orientation']:
                array = np.array(img)
                if channel_order != 'rgb':
                    array = array[:, :, ::-1]  # RGB to BGR
            elif flag in ['grayscale', 'grayscale_ignore_orientation']:
                img = img.convert('L')
                array = np.array(img)
            else:
                raise ValueError(
                    'flag must be "color", "grayscale", "unchanged", '
                    f'"color_ignore_orientation" or "grayscale_ignore_orientation"'
                    f' but got {flag}')
        return array

    def _prepare_zip(self):
        if self.path not in global_zipfiles or global_zipfiles[self.path] is None:
            global_zipfiles[self.path] = zipfile.ZipFile(self.path, "r")

    def _prepare_dir_struct(self):
        self._prepare_zip()
        if self.dir_struct is not None:
            return
        self.dir_struct = {}
        for path in global_zipfiles[self.path].namelist():
            if path[-1] == '/':
                continue
            current = self.dir_struct
            split = path.split('/')
            for name in split[0:-1]:
                if name in current:
                    current = current[name]
                else:
                    current[name] = {}
                    current = current[name]
            name = split[-1]
            current[name] = None

    def list_images(self, path: str) -> [str]:
        """List a dir zip.
        :param path: path of the dir in zip
        :returns paths of the files in the dir, include sub dir
        """
        path = self._format_path(path)
        self._prepare_zip()
        self._prepare_dir_struct()
        current = self.dir_struct
        for name in path.split('/'):
            if name in current:
                current = current[name]
            else:
                return []

        def join(root: str, data):
            if type(data) is dict:
                for k, v in data.items():
                    if v is None:
                        yield root + "/" + k
                    else:
                        yield from join(root + "/" + k, v)
            else:
                yield root + "/" + data

        return sorted(list(join(path, current)))

    def getinfo(self, path: str):
        self._prepare_zip()
        return global_zipfiles[self.path].getinfo(path)
