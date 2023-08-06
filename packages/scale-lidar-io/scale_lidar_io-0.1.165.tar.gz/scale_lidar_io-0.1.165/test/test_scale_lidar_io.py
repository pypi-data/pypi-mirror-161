import unittest
from pyquaternion import Quaternion
import numpy as np
from scale_lidar_io import LidarScene, Transform


class LidarTest(unittest.TestCase):
    """Test lidar frame implementation.
    The goal is to test if the frame poses working correctly
    """

    scene = LidarScene()

    def setUp(self):
        # Setup poses
        poses_data = {
            "heading": [
                0.9992067938556252,
                0.0,
                0.0,
                0.0398218923804761,
            ],
            "position": [
                0.0,
                0.0,
                0.0,
            ],
        }

        poses = []
        pose = Transform.from_Rt(
            R=Quaternion(
                poses_data["heading"][0],
                poses_data["heading"][1],
                poses_data["heading"][2],
                poses_data["heading"][3],
            ),
            t=np.array(
                [
                    poses_data["position"][0],
                    poses_data["position"][1],
                    poses_data["position"][2],
                ]
            ),
        )
        poses.append(pose)

        lidar_extrinsics = Transform.from_Rt(
            R=Quaternion(
                1.0,
                0.0,
                0.0,
                0.0,
            ).rotation_matrix,
            t=[-3.0, 0, 2.8572714],
        )

        points = np.array(
            [
                [6.592881, 7.3447638, -1.0611035, 181.3016],
                [6.0755334, 7.2042847, -0.9519308, 103.005844],
                [8.022584, 11.820594, 0.24009487, 161.13264],
                [7.4657607, 11.8752, 0.31154653, 169.24597],
            ]
        )

        self.scene.get_frame(0).add_points(points, transform=lidar_extrinsics)
        self.scene.get_frame(0).transform = poses[0]

    def test_poses(self):
        np.testing.assert_allclose(
            self.scene.get_frame(0).transform.position, [0.0, 0.0, 0.0]
        )
        np.testing.assert_allclose(
            self.scene.get_frame(0).transform.rotation,
            [
                [0.99682843, -0.07958061, 0.0],
                [0.07958061, 0.99682843, 0.0],
                [0.0, 0.0, 1.0],
            ],
        )

    def test_points(self):
        np.testing.assert_allclose(
            self.scene.get_frame(0).points[0],
            [3.5928812, 7.34476376, 1.79616794, 181.30160522, 0.0],
        )


class CameraTest(unittest.TestCase):
    """Test cameras implementation.
    The goal is to test if the cameras extrinsic
    and intrinsic are working correctly
    """

    scene = LidarScene()
    cams = {"forward": {}}

    def setUp(self):
        # Setup cameras
        extr = {
            "heading": [
                0.9992307979502907,
                0.0009624406647958967,
                0.03318256034771476,
                0.020875914934737397,
            ],
            "position": [
                -2.1498306,
                0.00635,
                2.346325,
            ],
        }

        intr = {
            "fx": -338.5609808656974,
            "fy": -335.3931513851273,
            "cx": -638.9593048466166,
            "cy": -397.69312118769875,
            "K": [
                [338.5609808656974, 0.0, 638.9593048466166],
                [0.0, 335.3931513851273, 397.69312118769875],
                [0.0, 0.0, 1.0],
            ],
            "D": [
                0.08577354267758332,
                -0.009275696593772212,
                0.002280136164042399,
                -0.0008592168095191392,
            ],
        }

        K = np.array(intr["K"])
        D = intr["D"]

        world2optical = Transform.from_euler([-90, 0, -90], degrees=True)
        extr_R = Quaternion(extr["heading"]).rotation_matrix @ world2optical.rotation
        extr_t = extr["position"]
        extr_opticalcoord = Transform.from_Rt(R=extr_R, t=extr_t)
        self.scene.get_camera("forward").calibrate(
            extrinsic_matrix=extr_opticalcoord.inverse,
            K=K,
            D=[D[0], D[1], 0.0, 0.0, D[2], D[3]],
            model="fisheye",
        )
        # Setup poses
        poses_data = {
            "heading": [
                0.9992067938556252,
                0.0,
                0.0,
                0.0398218923804761,
            ],
            "position": [
                0.0,
                0.0,
                0.0,
            ],
        }

        poses = []
        pose = Transform.from_Rt(
            R=Quaternion(
                poses_data["heading"][0],
                poses_data["heading"][1],
                poses_data["heading"][2],
                poses_data["heading"][3],
            ),
            t=np.array(
                [
                    poses_data["position"][0],
                    poses_data["position"][1],
                    poses_data["position"][2],
                ]
            ),
        )
        poses.append(pose)

        self.scene.get_frame(0).transform = poses[0]

    def test_camera_extrinsic(self):
        np.testing.assert_allclose(
            self.scene.get_frame(0).cameras["forward"].pose.position,
            [-2.1498306, 0.00635, 2.346325],
        )
        np.testing.assert_allclose(
            self.scene.get_frame(0).cameras["forward"].pose.rotation,
            [
                [4.16558418e-02, -6.63542562e-02, 9.96926228e-01],
                [-9.99126540e-01, 5.37968093e-04, 4.17835868e-02],
                [-3.30883332e-03, -9.97795983e-01, -6.62738888e-02],
            ],
        )

    def test_camera_intrinsic(self):
        np.testing.assert_allclose(
            self.scene.get_frame(0).cameras["forward"].K,
            [
                [338.56098087, 0.0, 638.95930485],
                [0.0, 335.39315139, 397.69312119],
                [0.0, 0.0, 1.0],
            ],
        )
        np.testing.assert_allclose(
            self.scene.get_frame(0).cameras["forward"].D,
            [
                0.08577354267758332,
                -0.009275696593772212,
                0.0,
                0.0,
                0.002280136164042399,
                -0.0008592168095191392,
            ],
        )


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
