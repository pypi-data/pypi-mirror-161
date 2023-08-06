import pandas as pd
import ujson
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import numpy as np
from io import BytesIO
from pyquaternion import Quaternion
from typing import Any
from scipy.spatial.transform import Rotation as R


from .camera import LidarCamera
from .image import LidarImage
from .connectors import Importer
from .transform import Transform
from .helper import (
    s3_smart_upload,
    format_lidar_point,
    format_point,
    format_quaternion,
    scale_file_upload,
)


class LidarFrame:
    """Frame object represents the point cloud, image and calibration data contained in a single frame

    Frame properties:
      - id: Frame id, used to identify the frame
      - cameras: List of LidarCamera
      - images: List of LidarImage
      - points: Pointcloud for this frame
      - radar_points: Radar points for this frame
      - colors: Colors for each point on the pointcloud for this frame
      - transform: Pose/ transform of this frame
    """

    def __init__(self, frame_id, cameras):
        self.id = frame_id
        self.cameras: pd.Series[Any, LidarCamera] = cameras
        self.images: pd.Series[Any, LidarImage] = pd.Series(dtype=object)
        self.points: np.ndarray = np.zeros((0, 5), dtype=float)
        self.radar_points: np.ndarray = np.zeros((0, 3), dtype=float)
        self.colors: np.ndarray = np.zeros((0, 3), dtype=float)
        self.transform = Transform()

    def get_image(self, camera_id) -> LidarImage:
        """Get image by camera_id or create one if it does not exist

        :param camera_id: Camera id
        :type camera_id: str, int
        :returns: LidarImage object
        :rtype: LidarImage

        """
        assert camera_id in self.cameras, "Camera not found"
        if camera_id not in self.images:
            if isinstance(camera_id, int):
                self.images.index = self.images.index.astype(int)
            self.images[camera_id] = LidarImage(camera=self.cameras[camera_id])
        return self.images[camera_id]

    def add_points_from_connector(
        self, connector: Importer, transform: Transform = None, intensity=1, sensor_id=0
    ):
        """Use Importer output to add points to the frame

        :param connector: Importer used to load the points
        :type connector: Importer
        :param transform: Transform that should be applied to the points
        :type transform: Transform
        :param intensity: If the points list does not include intensity, this value will be used as intensity for all the points (default ``1``)
        :type intensity: int
        :param sensor_id: Sensor id, used in case that you have more than one lidar sensor. (Default ``0``)
        :type sensor_id: int

        """
        self.add_points(connector.data, transform, intensity, sensor_id)

    def add_radar_points(self, points: np.array):
        """Add radar points to the frame, structure:

        .. highlight:: python
        .. code-block:: python

          radar_points = np.array([
            [
            [0.30694541, 0.27853175, 0.51152715],    // position - x,y,z
            [0.80424087, 0.24164057, 0.45256181],    // direction - x,y,z
            [0.73596422]    // size
            ],
            ...
          ])

        :param points: List of radar points data
        :type points: np.array

        """
        assert np.array(points).shape[1] == 3, "Radar points length is not 3"
        self.radar_points = points

    def add_points(
        self, points: np.array, transform: Transform = None, intensity=1, sensor_id=0
    ):
        """Add points to the frame, structure: np.array with dimension 1 and shape (N,3) or (N,4) (N being the number of point in the frame)

        Points with intensity:

        .. highlight:: python
        .. code-block:: python

          points = np.array([
            [0.30694541, 0.27853175, 0.51152715, 0.4],
            [0.80424087, 0.24164057, 0.45256181, 1],
            ...
          ])

        Points without intensity:

        .. highlight:: python
        .. code-block:: python

          points = np.array([
            [0.30694541, 0.27853175, 0.51152715],
            [0.80424087, 0.24164057, 0.45256181],
            ...
          ])

        :param points: List of points
        :type points: np.array
        :param transform: Transform that should be applied to the points
        :type transform: Transform
        :param intensity: If the points list doesn't include intensity, this value will be used as intensity for all the points (default ``1``)
        :type intensity: int
        :param sensor_id: Sensor id, used in case that you have more than one lidar sensor. (Default ``0``)
        :type sensor_id: int

        """
        if points.ndim == 1:
            points = np.array([points])
        if points.shape[1] == 3:
            points = np.hstack([points, np.ones((points.shape[0], 1)) * intensity])
        if transform is not None:
            points = transform.apply(points)

        points = np.hstack([points, np.ones((points.shape[0], 1)) * sensor_id])

        self.points = np.vstack([self.points, points])

    def add_colors(self, colors: np.ndarray):
        """Add colors to the pointcloud. This list should follow the same order as the point list.

        Each color should be in RGB with values between 0 and 255.

        .. highlight:: python
        .. code-block:: python

          colors = np.array([
            [10, 200, 230],
            [0, 0, 255],
            ...
          ])


        :param colors: List of colors
        :type colors: np.ndarray

        """
        self.colors = np.vstack([self.colors, colors])

    def add_debug_lines(self, intensity: int = 1, length: int = 5, device: int = 0):
        """Add debug lines.

        This will add a line starting from each camera position to the direction it is facing. This will use the camera position in this frame.

        :param intensity: Intensity of the points from the debugging line, default ``1``
        :type intensity: int
        :param length: Length of the line, default ``5`` points
        :type length: int
        :param device: Device id fror the points added, default ``0``
        :type device: int

        """
        x_line = np.array([np.array([length * k / 100, 0, 0]) for k in range(0, 100)])
        for camera in self.cameras:
            self.add_points(
                x_line, transform=camera.world_transform, intensity=intensity
            )

    def get_world_points(self):
        """Return the list of points with the frame transformation applied

        :returns: List of points in world coordinates
        :rtype: np.array

        """
        return np.hstack(
            [
                self.transform @ self.points[:, :3],
                self.points[:, 3:4],
                self.points[:, 4:5],
            ]
        )

    # leeaving this method as legacy / old code dependency
    def get_projected_image(self, camera_id, color_mode: str = "default", **kwargs):
        """Get camera_id image with projected points

        :param camera_id: Camera id/Name/Identifier
        :type camera_id: str, int
        :param color_mode:  Color mode, default ``default``, modes are: 'depth', 'intensity' and 'default'
        :type color_mode: str
        :returns: Image with the points projected
        :rtype: PIL.Image

        """
        return self.cameras[camera_id].get_projected_image(
            self.get_image(camera_id), self.points, self.transform, color_mode, **kwargs
        )

    def manual_calibration(
        self, camera_id, intrinsics_ratio: int = 1000, extrinsics_ratio: int = 10
    ):
        """Open a window with the camera with the points projected over it. The window also display dials to change the camera intrinsic and extrinsic values. The new values for the camera calibration will be display as matrices on the terminal.

        :param camera_id: Camera id/Name/Identifier
        :type camera_id: str, int
        :param intrinsics_ratio: Range of possible values for the intrinsic, center value will be the current one.
        :type intrinsics_ratio: int
        :param extrinsics_ratio:  Range of possible values for the extrinsic, center value will be the current one.
        :type extrinsics_ratio: int

        """
        fig = plt.figure(constrained_layout=True)
        intrinsics = ["fx", "fy", "cx", "cy"]
        extrinsics_position = ["x", "y", "z"]
        extrinsics_heading = ["qw", "qx", "qy", "qz"]
        heights = np.concatenate(
            (np.array([7]), np.array([0.2 for x in range(0, 7)])), axis=0
        )
        gs = fig.add_gridspec(
            ncols=3,
            nrows=1 + len(extrinsics_heading) + len(extrinsics_position),
            height_ratios=heights,
        )
        imgObj = fig.add_subplot(gs[0, :])
        imgObj.imshow(
            self.cameras[camera_id].get_projected_image(
                self.get_image(camera_id), self.points, self.transform, "depth", 1
            )
        )

        for index, key in enumerate(intrinsics):
            globals()[f"ax{key}"] = fig.add_subplot(gs[index + 1, 0])
            value = getattr(self.cameras[camera_id], key)
            globals()[key] = Slider(
                globals()[f"ax{key}"],
                f"{key}",
                value - intrinsics_ratio,
                value + intrinsics_ratio,
                valinit=value,
            )

        for index, key in enumerate(extrinsics_position):
            globals()[f"ax{key}"] = fig.add_subplot(gs[index + 1, 1])
            value = getattr(self.cameras[camera_id], "position")
            globals()[key] = Slider(
                globals()[f"ax{key}"],
                f"{key}",
                value[index] - extrinsics_ratio,
                value[index] + extrinsics_ratio,
                valinit=value[index],
            )

        for index, key in enumerate(extrinsics_heading):
            globals()[f"ax{key}"] = fig.add_subplot(
                gs[index + len(extrinsics_position) + 1, 1]
            )
            value = getattr(self.cameras[camera_id], "rotation")
            value = Quaternion(R.from_matrix(value).as_quat())
            globals()[key] = Slider(
                globals()[f"ax{key}"],
                f"{key}",
                value[index] - extrinsics_ratio,
                value[index] + extrinsics_ratio,
                valinit=value[index],
            )

        def update(val):
            self.cameras[camera_id].calibrate(
                K=np.array([[fx.val, 0, cx.val], [0, fy.val, cy.val], [0, 0, 1]]),
                pose=Transform.from_Rt(
                    Quaternion(qw.val, qx.val, qy.val, qz.val).rotation_matrix,
                    [x.val, y.val, z.val],
                ),
            )
            np.set_printoptions(suppress=True)
            print(f"New intrinsics for Camera {camera_id}")
            print(self.cameras[camera_id].K)
            print(f"New position for Camera {camera_id}")
            print(self.cameras[camera_id].position)
            print(f"New heading for Camera {camera_id}")
            print(
                dict(
                    zip(
                        ["w", "x", "y", "z"],
                        Transform(self.cameras[camera_id].rotation).quaternion,
                    )
                )
            )

            imgObj.imshow(
                self.cameras[camera_id].get_projected_image(
                    self.get_image(camera_id), self.points, self.transform, "depth", 1
                )
            )
            fig.canvas.draw_idle()

        axApply = fig.add_subplot(gs[1, 2])
        bApply = Button(axApply, "Apply changes")
        bApply.on_clicked(update)
        plt.show()

    def get_filename(self) -> str:
        """Get frame json file name

        :returns: Json file name
        :rtype: str

        """
        return "frame-%s.json" % self.id

    def apply_transform(self, T: Transform):
        """Apply the frame transformation. This will be used to define the device position and applied to cameras and points.

        :param T: Transform for this frame
        :type T: Transform

        """
        self.transform = Transform(T) @ self.transform

    def filter_points(self, min_intensity=None, min_intensity_percentile=None):
        """Filter points based on their intensity

        :param min_intensity: Minimun intensity allowed
        :type min_intensity: int
        :param min_intensity_percentile: Minimun percentile allowed (use np.percentile)
        :type min_intensity_percentile: int

        """
        if min_intensity is not None:
            self.points = self.points[self.points[:, 3] >= min_intensity]
        if min_intensity_percentile is not None:
            self.points = self.points[
                self.points[:, 3]
                >= np.percentile(self.points[:, 3], min_intensity_percentile)
            ]

    def to_json(
        self, base_url: str = "", s3_upload: bool = True, project_name: str = ""
    ):
        """Return the frame data in json format following Scale data format: https://private-docs.scale.com/?python#sensor-fusion-lidar-annotatio.

        This will return the final data from the frame, this means cameras and points will be in world coordinates.

        :param base_url: This url will concatenated with the image name, e.g.: `'%s/image-%s-%s.jpg' % (base_url, camera.id, frame.id)`
        :type base_url: str
        :returns: Frame object as a JSON formatted stream
        :rtype: str

        """

        def format_image(camera, s3_upload: bool, project_name: str):
            image = self.images[camera.id]
            if camera.world_poses:
                wct = camera.world_poses[self.id]
            else:
                wct = (image.transform or self.transform) @ camera.pose

            D = camera.D

            image_url = "%s/image-%s-%s.jpg" % (base_url, camera.id, self.id)
            if not s3_upload:
                image_url = self.images[camera.id].scale_file_upload(project_name)

            result = dict(
                position=format_point(wct.position),
                heading=format_quaternion(wct.quaternion),
                image_url=image_url,
                camera_model=camera.model,
                fx=camera.fx,
                fy=camera.fy,
                cx=camera.cx,
                cy=camera.cy,
                skew=camera.skew,
                k1=float(D[0]),
                k2=float(D[1]),
                p1=float(D[2]),
                p2=float(D[3]),
                k3=float(D[4]),
                k4=float(D[5]),
                k5=float(D[6]) if len(D) >= 7 else 0,
                k6=float(D[7]) if len(D) >= 8 else 0,
                scale_factor=camera.scale_factor,
            )
            if image.metadata:
                result["metadata"] = image.metadata
            if image.timestamp:
                result["timestamp"] = image.timestamp
            return result

        images_json = (
            self.cameras[self.images.index]
            .apply(format_image, args=(s3_upload, project_name))
            .to_json(orient="records")
        )
        points_json = pd.DataFrame(
            self.get_world_points(), columns=["x", "y", "z", "i", "d"]
        ).to_json(double_precision=4, orient="records", date_format=None)

        colors_json = pd.Series(self.colors.reshape(-1).astype(np.uint32)).to_json(
            orient="values", date_format=None
        )

        radar_points_json = ujson.dumps(
            list(
                np.array(
                    [
                        {
                            "position": format_point(row[0]),
                            "direction": format_point(row[1]),
                            "size": row[2][0],
                        }
                        for row in self.radar_points
                    ]
                )
            )
        )
        frame_object = {
            "images": "__IMAGES__",
            "points": "__POINTS__",
            "device_position": format_point(self.transform.position),
            "device_heading": format_quaternion(self.transform.quaternion),
        }

        if len(self.colors) > 0:
            frame_object["point_colors"] = "__COLORS__"

        if len(self.radar_points) > 0:
            frame_object["radar_points"] = "__RADAR_POINTS__"

        out = ujson.dumps(frame_object)
        out = out.replace('"__IMAGES__"', images_json)
        out = out.replace('"__POINTS__"', points_json)
        out = out.replace('"__COLORS__"', colors_json)
        out = out.replace('"__RADAR_POINTS__"', radar_points_json)

        return out

    def save(self, path: str, base_url: str = ""):
        """Save frame object in a json file

        :param path: Path in which the frame data should be saved
        :type path: str
        :param base_url: This url will concatenated with the image name, e.g.: `'%s/image-%s-%s.jpg' % (base_url, camera.id, frame.id)`
        :type base_url: str

        """
        # Save frame
        with open(os.path.join(path, "frame-%s.json" % self.id), "w") as file:
            file.write(self.to_json(base_url))

        # Save images
        for camera_id, image in self.images.items():
            image.save(os.path.join(path, "image-%s-%s.jpg" % (camera_id, self.id)))

    def s3_upload(self, bucket: str, path: str):
        """Save frame in S3

        :param bucket: S3 Bucket name
        :type bucket: str
        :param path: Path to store data
        :type key: str

        """
        # print(f'Uploading frame {self.id}...')
        base_url = f"s3://{bucket}/{path}"

        # Upload frame json file
        s3_smart_upload(
            fileobj=BytesIO(bytes(self.to_json(base_url), encoding="utf-8")),
            bucket=bucket,
            key=f"{path}/frame-{self.id}.json",
            content_type="application/json",
        )

        # Upload images
        for camera_id, image in self.images.items():
            image.s3_upload(bucket, f"{path}/image-{camera_id}-{self.id}.jpg")

    def scale_file_upload(self, project_name: str):
        """Save frame in Scale File

        :param project_name: File project name
        :type bucket: str

        """

        fileobj = BytesIO(
            bytes(
                self.to_json(s3_upload=False, project_name=project_name),
                encoding="utf-8",
            )
        )
        return scale_file_upload(fileobj, project_name)

    def __repr__(self):
        return "Frame({0}) {1}".format(self.id, self.transform)
