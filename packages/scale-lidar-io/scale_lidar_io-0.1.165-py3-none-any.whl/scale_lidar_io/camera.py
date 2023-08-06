import random

import cv2
import numpy as np
from PIL import Image, ImageDraw

from .color_utils import map_colors
from .transform import Transform


class LidarCamera:
    """Camera object that contains all the camera information

    Camera properties:
        - id = camera id/Name/Identifier, type: int, str
        - pose: Camera pose/extrinsic, type: Transform
        - world_poses: World poses, this will make the camera ignore the frame poses, type: list(Transform)
        - K: Intrinsic matrix
        - D: Camera distortion coefficients [k1,k2,p1,p2,k3,k4], default all set to ``0``
        - model: Camera model, default ``brown_conrady``
        - scale_factor: Camera scale factor, default ``1``
        - skew: Camera scale factor, default ``0``

    Usefull extra documentation to understand better how this object works:
    https://docs.opencv.org/3.4/d9/d0c/group__calib3d.html

    """

    world2cam = Transform.from_euler([-90, 0, -90], degrees=True)

    def __init__(self, camera_id):
        self.id = camera_id
        self.pose = Transform(self.world2cam)
        self.world_poses = None
        self.K = np.eye(3, dtype=np.float32)
        self.D = np.zeros(6, dtype=np.float32)
        self.model = "brown_conrady"
        self.scale_factor = 1
        self.skew = 0

    @property
    def position(self) -> np.ndarray:
        """Camera position

        :getter: Return camera's position
        :setter: Set camera's position
        :type: list(x,y,z)
        """
        return self.pose.position

    @property
    def rotation(self) -> np.ndarray:
        """Camera rotation/heading

        :getter: Return camera's rotation
        :setter: Set camera's rotation
        :type: 3x3 rotation matrix
        """
        return self.pose.rotation

    @property
    def world_transform(self) -> Transform:
        """World transform/pose (to avoid frame pose)

        :getter: pose @ world2cam.T
        :setter: pose = transform @ world2cam
        :type: Transform
        """
        return self.pose @ self.world2cam.T

    @property
    def fx(self):
        """Camera X focal length

        :getter: Return camera's X focal length
        :type: double
        """
        return self.K[0, 0]

    @property
    def fy(self):
        """Camera Y focal length

        :getter: Return camera's Y focal length
        :type: double
        """
        return self.K[1, 1]

    @property
    def cx(self):
        """Camera X center point

        :getter: Return camera's X center point
        :type: double
        """
        return self.K[0, 2]

    @property
    def cy(self):
        """Camera Y center point

        :getter: Return camera's Y center point
        :type: double
        """
        return self.K[1, 2]

    @property
    def intrinsic_matrix(self):
        """Camera intrinsic/K

        :getter: Return camera's intrinsic matrix
        :type: 3x3 matrix
        """
        return self.K

    @property
    def extrinsic_matrix(self):
        """Camera extrinsic

        :getter: Return camera's extrinsic matrix (pose.inverse[:3, :4])
        :setter: pose = Transform(matrix).inverse
        :type: 3x4 matrix
        """
        return self.pose.inverse[:3, :4]

    @property
    def projection_matrix(self):
        """Projection matrix

        :getter: K @ extrinsic_matrix
        :setter: K, R, t, _, _, _, _ = cv2.decomposeProjectionMatrix(projection_matrix)
        :type: 3x4 projection matrix
        """
        return self.K @ self.extrinsic_matrix

    @position.setter
    def position(self, position: np.ndarray):
        self.pose.position = position

    @rotation.setter
    def rotation(self, rotation):
        self.pose.rotation = Transform(rotation).rotation

    @world_transform.setter
    def world_transform(self, transform: Transform):
        self.pose = transform @ self.world2cam

    @extrinsic_matrix.setter
    def extrinsic_matrix(self, matrix):
        self.pose = Transform(matrix).inverse

    @projection_matrix.setter
    def projection_matrix(self, P):
        assert P.shape == (3, 4), "Projection matrix should be 3x4"
        K, R, t, _, _, _, _ = cv2.decomposeProjectionMatrix(P)
        self.pose = Transform.from_Rt(R.T, t[:3, 0] / t[3, 0])
        self.K = K

    def calibrate(
        self,
        position=None,
        rotation=None,
        pose=None,
        extrinsic_matrix=None,
        projection_matrix=None,
        K=None,
        D=None,
        model=None,
        scale_factor=None,
        skew=None,
        world_transform=None,
        world_poses=None,
        **kwargs
    ):
        """Helper for camera calibration

        Args:
          position (list(int)): Camera position [x, y, z]
          rotation (rotation matrix): Camera rotation/heading
          pose (Transform): Camera pose (position + rotation)
          extrinsic_matrix (matrix 4x4): Extrinsic 4x4 matrix (world to camera transform) (pose = Transform(matrix).inverse)
          projection_matrix (matrix 3x4): 3x4 projection matrix (K, R, t, _, _, _, _ = cv2.decomposeProjectionMatrix(projection_matrix))
          K (matrix 3x3): Intrinsic 3x3 matrix
          D (list(double)): Distortion values following this order: [k1,k2,p1,p2,k3,k4,k5,k6], required [k1,k2,p1,p2,k3,k4]
          model (str): Camera model
          scale_factor (int): Image scale_factor
          skew (int): Camera skew coefficient
          world_transform (Transform): Overwrite camera pose with the world transform (pose = transform @ world2cam)
          world_poses (list(Transform)):  World poses, this will make the camera ignore the frame poses

        Keyword Args:
          fx (str): Focal length in X
          fy (str): Focal length in Y
          cx (str): Center point in X
          cy (str): Center point in Y
          k1 (double): Distortion value k1
          k2 (double): Distortion value k2
          k3 (double): Distortion value k3
          k4 (double): Distortion value k4
          k5 (double): Distortion value k5
          k6 (double): Distortion value k6
          p1 (double): Distortion value p1
          p2 (double): Distortion value p2

        """
        if position is not None:
            self.position = position
        if rotation is not None:
            self.rotation = rotation
        if pose is not None:
            self.pose = Transform(pose)
        if extrinsic_matrix is not None:
            self.extrinsic_matrix = extrinsic_matrix
        if projection_matrix is not None:
            self.projection_matrix = projection_matrix
        if K is not None:
            self.K = np.array(K[:3, :3])
        if D is not None:
            assert (
                len(D) >= 6
            ), "Distortion list should have have at least these values [k1,k2,p1,p2,k3,k4]"
            self.D = D
        if model is not None:
            self.model = model
        if scale_factor is not None:
            self.scale_factor = scale_factor
        if skew is not None:
            self.skew = skew
        if world_transform is not None:
            self.world_transform = world_transform
        if world_poses is not None:
            self.world_poses = world_poses
        if "fx" in kwargs:
            self.K[0, 0] = kwargs["fx"]
        if "fy" in kwargs:
            self.K[1, 1] = kwargs["fy"]
        if "cx" in kwargs:
            self.K[0, 2] = kwargs["cx"]
        if "cy" in kwargs:
            self.K[1, 2] = kwargs["cy"]
        if "k1" in kwargs:
            self.D[0] = kwargs["k1"]
        if "k2" in kwargs:
            self.D[1] = kwargs["k2"]
        if "p1" in kwargs:
            self.D[2] = kwargs["p1"]
        if "p2" in kwargs:
            self.D[3] = kwargs["p2"]
        if "k3" in kwargs:
            self.D[4] = kwargs["k3"]
        if "k4" in kwargs:
            self.D[5] = kwargs["k4"]
        if "k5" in kwargs:
            self.D = np.lib.pad(self.D, (0, 1), "constant", constant_values=(0))
            self.D[6] = kwargs["k5"]
        if "k6" in kwargs:
            if len(self.D) == 6:
                self.D = np.lib.pad(self.D, (0, 2), "constant", constant_values=(0))
            elif len(self.D) == 7:
                self.D = np.lib.pad(self.D, (0, 1), "constant", constant_values=(0))
            self.D[7] = kwargs["k6"]

    def apply_transform(self, transform: Transform):
        """Apply transformation to the camera (transform @ pose)

        :param transform: Transform to apply to the object
        :type transform: Transform
        """

        self.pose = transform @ self.pose

    def rotate(self, angles, degrees=True):
        """Rotate the camera,
        (pose = Transform.from_euler(angles, degrees=degrees) @ pose)

        :param angles: Angles to rotate (x,y,z)
        :type angles: list(float)
        :param degrees: Use rad or degrees
        :type degrees: boolean

        """
        self.apply_transform(Transform.from_euler(angles, degrees=degrees))

    def translate(self, vector):
        """Move the camera,
        (pose = Transform(angles, degrees=degrees) @ pose)

        :param vector: [x,y,z]
        :type vector: list(float)
        """
        self.apply_transform(Transform(vector))

    def project_points(self, points: np.ndarray, use_distortion=False):
        """Return array of projected points based on camera calibration values

        - When ``use_distortion=True`` it uses: cv.fisheye.projectPoints(	objectPoints, rvec, tvec, K, D[, imagePoints[, alpha[, jacobian]]]	)

        :param points: list of points
        :type points: list(float)
        :param use_distortion: For fisheye/omni cameras (not necesary for cameras like Brown-Conrady)
        :type use_distortion: boolean
        """
        projected = Transform(self.projection_matrix) @ points[:, :3]

        # projected = ((points[:, :3] - self.position) @ self.rotation) @ self.intrinsic_matrix[:3, :3].T
        projected[:, 0] /= np.where(projected[:, 2] == 0, np.inf, projected[:, 2])
        projected[:, 1] /= np.where(projected[:, 2] == 0, np.inf, projected[:, 2])

        if use_distortion:
            projected[:, :2] = cv2.fisheye.projectPoints(
                objectPoints=np.array([points[:, :3]], dtype=np.float32),
                rvec=cv2.Rodrigues(self.extrinsic_matrix[:3, :3])[0],
                tvec=self.extrinsic_matrix[:3, 3],
                D=np.array(
                    [self.D[0], self.D[1], self.D[4], self.D[5]], dtype=np.float32
                ),
                K=np.array(self.K, dtype=np.float32),
                alpha=self.skew,
            )[0].reshape((-1, 2))

        return np.hstack([projected[:, :3], points[:, 3:]])

    def get_projected_image(
        self, image, points, frame_transform, color_mode="default", oversample=3
    ):
        """Return image with points projected onto it

        :param image: Camera image
        :type image: PIL.Image
        :param points: list of points/pointcloud
        :type points: list(float)
        :param frame_transform: Frame transform/pose
        :type frame_transform: Transform
        :param color_mode: Color mode, default ``default``, modes are: 'depth', 'intensity' and 'default'
        :type color_mode: str
        :param oversample: Padding on projected points, this is used to project points outside the image, it's useful for debugging, default ``3`` = 3 times the image size
        :type oversample: int
        :returns: Image with points projected
        :rtype: PIL.Image
        """
        assert image, "No image loaded."

        def crop_points(points, bounding_box):
            conditions = np.logical_and(
                points[:, :3] >= bounding_box[0], points[:, :3] < bounding_box[1]
            )
            mask = np.all(conditions, axis=1)
            return points[mask]

        im = image.get_image().convert("RGBA")
        radius = 3
        points = np.array(
            random.sample(points.tolist(), int(len(points) / 2))
        )  # reduce the number of points projected, no need to project everything
        # Project points image
        points_im = Image.new(
            "RGBA", (im.size[0] * oversample, im.size[1] * oversample)
        )

        draw = ImageDraw.Draw(points_im)

        if self.model == "cylindrical":
            # handle cylindrical cameras
            epsilon = 0.0000001
            fisheye = frame_transform.inverse @ np.array(
                [points[:, 0], points[:, 1], points[:, 2]], dtype=np.float
            )  # 3D point in camera coordinates
            fisheye = fisheye.T  # 3D point in camera coordinates
            fisheye = self.pose.inverse @ fisheye
            fisheye[
                :, 1
            ] *= -1  # invert y because cylindrical y is up and cartesian y is down
            fisheye = (
                Transform(self.extrinsic_matrix[:3, :3]) @ fisheye.T
            )  # lift cylinder to stand up straight
            cylindrical = np.array(
                [
                    np.arctan2(fisheye[0, :], fisheye[2, :]),
                    fisheye[1, :] / np.sqrt(fisheye[0, :] ** 2 + fisheye[2, :] ** 2),
                    np.ones(fisheye.shape[1]),
                ]
            )
            cylindrical[
                1, :
            ] *= -1  # invert y because cylindrical y is up and cartesian y is down
            q = self.K @ cylindrical
            img_coords = q[[0, 1], :]  # pixels on image
            img_coords = img_coords.T

            for point in img_coords[:, :2]:
                draw.ellipse(
                    [tuple(point - radius), tuple(point + radius)],
                    fill=tuple([255, 10, 10]),
                )
            points_im = points_im.resize(im.size, Image.CUBIC)

            # Merge images
            projected_im = Image.composite(points_im, im, points_im)
            return projected_im
        if self.model == "fisheye":
            wct = self.pose @ frame_transform.T
            projected = self.project_points(points, use_distortion=True)
            #  projected = crop_points(projected,
            #  np.array([[0, 0, 0.1], [im.size[0], im.size[1], np.inf]]))
            fisheye = self.world_transform @ np.array(
                [projected[:, 0], projected[:, 1], projected[:, 2]], dtype=np.float
            )  # 3D point in camera coordinates
            fisheye = fisheye.T  # 3D point in camera coordinates
            fisheye = np.concatenate(
                (np.array(fisheye), np.array(projected[:, 3])[:, None]), axis=1
            )

            if not len(fisheye):
                return im

            colors = map_colors(fisheye, color_mode)

            for point, color in zip(fisheye[:, :2] * oversample, colors):
                draw.ellipse(
                    [tuple(point - radius), tuple(point + radius)], fill=tuple(color)
                )
            points_im = points_im.resize(im.size, Image.CUBIC)

            # Merge images
            projected_im = Image.composite(points_im, im, points_im)
            return projected_im
        else:
            projected = self.project_points(points, use_distortion=False)
            projected = crop_points(
                projected, np.array([[0, 0, 0.1], [im.size[0], im.size[1], np.inf]])
            )

            # Returns original image if not projected points on image
            if not len(projected):
                return im

            colors = map_colors(projected, color_mode)

            for point, color in zip(projected[:, :2] * oversample, colors):
                draw.ellipse(
                    [tuple(point - radius), tuple(point + radius)], fill=tuple(color)
                )
            points_im = points_im.resize(im.size, Image.CUBIC)

            # Merge images
            projected_im = Image.composite(points_im, im, points_im)
            return projected_im

        def __repr__(self):
            return "LidarCamera({0}) {1}".format(self.id, self.pose)
