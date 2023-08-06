import cv2
import numpy as np
from matplotlib.colors import hsv_to_rgb


def normalize(values):
    return np.interp(
        values, [np.percentile(values, 5), np.percentile(values, 95)], [0, 1]
    )


def map_colors(points, mode="default", color_map=cv2.COLORMAP_JET):
    """Set point's colors based on mode

    params:
        - points: Pointcloud
        - mode: Color mode ``default``
    """

    if mode == "depth":
        values = np.uint8(normalize(points[:, 2]) * 255)
        rgb = cv2.applyColorMap(values, color_map)
        return rgb.reshape((-1, 3))

    if mode == "intensity":
        values = 255 - np.uint8(normalize(points[:, 3]) * 255)
        rgb = cv2.applyColorMap(values, color_map)
        return rgb.reshape((-1, 3))

    if mode == "default":
        x, y, z, i = points.T
        i_range = [np.percentile(i, 10), np.percentile(i, 90)]

        value = np.sum(
            [np.interp(z, [0, 50], [100, -10]), np.interp(i, i_range, [-10, 10])],
            axis=0,
        )

        rgb = hsv_to_rgb(
            np.array(
                [
                    np.interp(value, [0, 100], [220 / 360, 1 / 360]),
                    np.interp(i, i_range, [0.5, 1]),
                    np.interp(i, i_range, [0.4, 1]),
                ]
            ).T
        )

        alpha = np.interp(i, [np.percentile(i, 10), np.percentile(i, 90)], [0.75, 1])

        return np.uint8(np.hstack([rgb.reshape((-1, 3)), alpha.reshape((-1, 1))]) * 255)

    # other mode
    values = np.uint8(normalize(points[:, 2]) * 255)
    rgb = cv2.applyColorMap(values, color_map)
    alpha = np.uint8(normalize(points[:, 3]) * 255)
    return np.hstack([rgb.reshape((-1, 3)), alpha.reshape((-1, 1))])
