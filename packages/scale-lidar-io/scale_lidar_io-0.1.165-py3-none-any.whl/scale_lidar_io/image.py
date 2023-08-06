import shutil
import numpy as np
import tempfile
from PIL import Image, ImageEnhance
from .helper import s3_smart_upload, scale_file_upload


class LidarImage:
    """LidarImage objects represent an image with a LidarCamera reference.

    LidarImage properties:
      - camera: Camera id
      - image_path: Image path
      - transform: Transformation apply to LidarImage (will be used as: LidarImage.transform or LidarFrame.transform) @ camera.pose)
      - metadata: Metadata related to the image
      - timestamp: Timestamp
    """

    def __init__(self, camera):
        self.camera = camera
        self.image_path = None
        self.transform = None
        self.metadata = None
        self.timestamp = None

    # Legacy method
    def load_file(self, file: str):
        """Set LidarImage image_path
        (**Legacy method**)

        :param file: Set image path
        :type file: str
        """
        if not isinstance(file, str):
            print("WARNING: No file!")
        self.image_path = file

    def save_pil_image(self, pil_image: Image.Image):
        """Save image in image_path

        :param pil_image: Image to save
        :type pil_image: PIL.Image
        """
        self.image_path = tempfile.mktemp(suffix="jpg")
        pil_image = pil_image.convert("RGB")
        pil_image.save(self.image_path, format="JPEG", quality=70, optimize=True)
        print(f"Temp file created: {self.image_path}")

    def get_image(self) -> Image:
        """Open LidarImage

        :return: Image.open
        """
        return Image.open(self.image_path)

    def as_array(self) -> np.asarray:
        """Get the image as numpy array

        :returns: image as numpy array
        :rtype: np.asarray

        """
        return np.asarray(self.get_image())

    def set_scale(self, scale_factor: float):
        """Change image scale and save in image_path

        :param scale_factor: Scale factor
        :type scale_factor: float

        """
        im = self.get_image()
        size = (int(im.width * scale_factor), int(im.height * scale_factor))
        self.save_pil_image(im.resize(size, Image.LANCZOS))

    def set_brightness(self, factor: float):
        """Change image brightness and save in image_path
        (will use PIL.ImageEnhance.Brightness)


        :param factor: Brightness factor
        :type scale_factor: float

        """
        im = ImageEnhance.Brightness(self.get_image()).enhance(factor)
        self.save_pil_image(im)

    def save(self, target_file: str):
        """Save image in target_file path

        :param target_file: Path in which the image should be saved
        :type target_file: str

        """
        if not isinstance(target_file, str):
            print("WARNING: No file path!")
        shutil.copyfile(self.image_path, target_file)

    def s3_upload(self, bucket: str, key: str):
        """Save image in S3

        :param bucket: S3 Bucket name
        :type bucket: str
        :param key: file name
        :type key: str

        """
        with open(self.image_path, "rb") as fp:
            s3_smart_upload(
                bucket=bucket, key=key, fileobj=fp, content_type="image/jpeg"
            )

    def scale_file_upload(self, project_name: str):
        """Save image in Scale File

        :param project_name: File project name
        :type bucket: str
        """
        with open(self.image_path, "rb") as fp:
            return scale_file_upload(fp, project_name)
