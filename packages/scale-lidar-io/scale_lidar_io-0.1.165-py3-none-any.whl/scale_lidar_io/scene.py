import zipfile
from multiprocessing.pool import ThreadPool
from functools import partial
from io import BytesIO
from typing import MutableMapping, List, Dict
from tqdm import tqdm

import numpy as np
import pandas as pd
import ujson
from scaleapi.tasks import Task, TaskType

from .camera import LidarCamera
from .image import LidarImage
from .frame import LidarFrame
from .connectors import Importer
from .transform import Transform
from .helper import s3_smart_upload, get_signed_url

UPLOAD_POOL_SIZE = 8


class LidarScene:
    """LidarScene object representing all frames in a scene.

    Scene properties:
      - cameras: List of cameras
      - frames: List of frames
      - base_url: Url used to host the data in S3

    """

    def __init__(self):
        """
        :rtype: object
        """
        self.cameras: MutableMapping[LidarCamera] = pd.Series()
        self.frames: MutableMapping[LidarFrame] = pd.Series()
        self.base_url = None
        self.scale_file_attachments = None

    def get_camera(self, camera_id=None, index: int = None) -> LidarCamera:
        """Get a camera by id (or index) or create one if it does not exist

        :param camera_id: The camera id
        :type camera_id: str, int
        :param index: The camera index
        :type index: int

        :return: LidarCamera
        :rtype:  LidarCamera

        """
        assert (
            camera_id is not None or index is not None
        ), "id or index must be specified"

        if camera_id is None:
            camera_id = self.cameras.index[index]

        if camera_id not in self.cameras:
            if isinstance(camera_id, int):
                self.cameras.index = self.cameras.index.astype(int)
            self.cameras[camera_id] = LidarCamera(camera_id)
        return self.cameras[camera_id]

    def get_frame(self, frame_id=None, index: int = None) -> LidarFrame:
        """Get a frame by id (or index) or create one if it does not exist

        :param frame_id: The frame id
        :type frame_id: str, int
        :param index: The frame index
        :type index: int

        :return: LidarFrame
        :rtype: LidarFrame

        """
        assert (
            frame_id is not None or index is not None
        ), "id or index must be specified"

        if frame_id is None:
            frame_id = self.frames.index[index]

        if frame_id not in self.frames:
            if isinstance(frame_id, int):
                self.frames.index = self.frames.index.astype(int)
            self.frames[frame_id] = LidarFrame(frame_id, cameras=self.cameras)
        return self.frames[frame_id]

    def apply_transforms(self, world_transforms: List[Transform]):
        """Apply transformations to all the frames (the number of Transformation should match the number of frames)

        :param world_transforms: List of Transform
        :type world_transforms: list(Transform)

        """
        assert len(world_transforms) != len(
            self.frames
        ), "world_transforms should have the same length as frames"

        for idx in range(len(self.frames)):
            self.get_frame(index=idx).apply_transform(world_transforms[idx])

    def filter_points(self, min_intensity=None, min_intensity_percentile=None):
        """Filter points based on intensity

        :param min_intensity: Minimun intensity allowed
        :type min_intensity: int
        :param min_intensity_percentile: Minimun percentile allowed (use np.percentile)
        :type min_intensity_percentile: int

        """
        for frame in self.frames:
            frame.filter_points(min_intensity, min_intensity_percentile)

    def get_projected_image(
        self, camera_id, color_mode="intensity", frames_index=range(0, 1), **kwargs
    ):
        """Get camera_id image with projected points, (**Legacy method**)

        :param camera_id: Camera id/Name/Identifier
        :type camera_id: str, int
        :param color_mode:  Color mode, default ``default``, modes are: 'depth', 'intensity' and 'default'
        :type color_mode: str
        :param frames_index: Project points for a range of frames, default `first frame`
        :type frames_index: range

        :returns: Image with points projected
        :rtype: Image

        """
        all_points = np.array([]).reshape(0, 4)
        for idx in frames_index:
            points = np.array(self.frames[idx].points)[:, :4]
            print(points.shape)
            points[:, 3] = idx
            all_points = np.concatenate((all_points, points), axis=0)
        return self.cameras[camera_id].get_projected_image(
            self.frames[frames_index[0]].get_image(camera_id),
            all_points,
            self.frames[frames_index[0]].transform,
            color_mode,
        )

    def apply_transform(self, world_transform: Transform):
        """Apply a Transformation to all the frames

        :param world_transform: Transform to apply to all the frames
        :type world_transform: Transform

        """

        for idx in range(len(self.frames)):
            self.get_frame(index=idx).apply_transform(world_transform)

    def make_transforms_relative(self):
        """Make all the frame transform relative to the first transform/frame. This will set the first transform to position (0,0,0) and heading (1,0,0,0)"""
        offset = self.get_frame(index=0).transform.inverse
        for frame in self.frames:
            frame.transform = offset @ frame.transform

    def to_dict(self, base_url: str = None) -> dict:
        """Return a dictionary with the frame urls using the base_url as base.

        :param base_url: This url will be concatenated with the frames name, e.g.: `'%s/frame-%s.json' % (base_url, frame.id)`
        :type base_url: str
        :return: Dictionary with the frame urls data
        :rtype: dict

        """
        if base_url is None:
            base_url = self.base_url
        return dict(
            frames=["%s/frame-%s.json" % (base_url, frame.id) for frame in self.frames]
        )

    def s3_upload(
        self,
        bucket: str,
        path=None,
        mock_upload: float = False,
        use_threads: float = True,
    ):
        """Save scene in S3

        :param bucket: S3 Bucket name
        :type bucket: str
        :param path: Path to store data
        :type key: str
        :param mock_upload: To avoid upload the data to S3  (defualt ``False``)
        :type mock_upload: float
        :param use_threads: In order to upload multiple files at the same time using threads  (defualt ``True``)
        :type use_threads: float

        :return: Scene S3 url
        :rtype: str

        """
        self.base_url = f"s3://{bucket}/{path}"

        print("Uploading scene to S3: %s" % self.base_url)
        scene_dict = self.to_dict(self.base_url)

        poses_csv = pd.DataFrame(
            self.frames.map(lambda f: list(f.transform.matrix.reshape(-1))).to_dict()
        ).T.to_csv(header=False)

        if not mock_upload:
            # Upload scene json file
            s3_smart_upload(
                bucket=bucket,
                key=f"{path}/scene.json",
                fileobj=BytesIO(bytes(ujson.dumps(scene_dict), encoding="utf-8")),
                content_type="application/json",
            )

            # Upload ego2world csv file
            s3_smart_upload(
                bucket=bucket,
                key=f"{path}/ego2world.csv",
                fileobj=BytesIO(bytes(poses_csv, encoding="utf-8")),
                content_type="text/plain",
            )

            if use_threads:
                p = ThreadPool(processes=UPLOAD_POOL_SIZE)
                func = partial(LidarFrame.s3_upload, bucket=bucket, path=path)
                p.map(func, self.frames)
            else:
                for frame in self.frames:
                    frame.s3_upload(bucket, path)

        signed_url = get_signed_url(bucket, path)

        print(f"Scene uploaded: {signed_url}")
        return self.base_url

    def scale_file_upload(
        self,
        project_name: str,
    ):
        """Save scene in Scale file

        :param project_name: File project name
        :type project_name: str
        :param verbose: Set to false to not show the progress bar

        :return: Scene file url
        :rtype: str

        """

        print("Uploading scene to Scale file")
        p = ThreadPool(processes=UPLOAD_POOL_SIZE)
        func = partial(LidarFrame.scale_file_upload, project_name=project_name)
        self.scale_file_attachments = p.map(func, self.frames)

        print(
            f"Finishes uploading scene to Scale file, uploaded {len(self.scale_file_attachments)} frames"
        )
        return self.scale_file_attachments

    def save_task(self, filepath: str, template=None):
        """Save the entire scene (with frame and images) in zipfile format to local filepath

        :param filepath: File name and path in which the scene should be saved
        :type filepath: str

        """
        print("Saving scene:", filepath)
        with zipfile.ZipFile(filepath, mode="w") as out:
            # Save task
            scene_dict = self.to_dict()
            task_dict = dict(
                template or {}, attachment_type="json", attachments=scene_dict["frames"]
            )
            out.writestr("task.json", ujson.dumps(task_dict))

            # Save frames
            for frame in self.frames:
                # Save points
                data = frame.to_json(self.base_url)
                out.writestr(
                    "frame-%s.json" % frame.id, data, compress_type=zipfile.ZIP_DEFLATED
                )

                # Save frame images
                for camera_id, image in frame.images.items():
                    if not image.image_path:
                        assert NotImplementedError(
                            "Only file-imported Images supported"
                        )
                    out.write(
                        image.image_path, "image-%s-%s.jpg" % (camera_id, frame.id)
                    )
        print("Scene saved.")

    def create_task(
        self, template: Dict = None, task_type: TaskType = TaskType.LidarAnnotation
    ) -> Task:
        """Create a Scale platform task from the configured scene

        :param template: Dictionary of payload for task creation (https://private-docs.scale.com/?python#parameters), attachments data will be filled automatically.
        :type template: dict
        :param task_type: Select a Scale API endpoint top upload data to, currently supports 'lidarannotation', 'lidarsegmentation', and 'lidartopdown'. Defaults to 'lidarannotation'.
        :type task_type: str

        :return: Task object with related information. Inherited from `scaleapi.Task` object.
        :rtype: Task
        """
        if task_type == TaskType.LidarAnnotation:
            from .task import LidarAnnotationTask

            return LidarAnnotationTask.from_scene(self, template)
        elif task_type == TaskType.LidarTopdown:
            from .task import LidarTopDownTask

            return LidarTopDownTask.from_scene(self, template)
        elif task_type == TaskType.LidarSegmentation:
            from .task import LidarSegmentationTask

            return LidarSegmentationTask.from_scene(self, template)
        else:
            raise NotImplementedError(
                f"Specified task_type {task_type} is not supported"
            )
