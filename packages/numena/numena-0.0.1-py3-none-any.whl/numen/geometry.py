from __future__ import annotations

import math
from dataclasses import asdict, astuple, dataclass
from math import atan2, degrees, pi
from typing import ClassVar, Tuple

import cv2
import numpy as np

from numen.image.contour import contours_fill, contours_find
from numen.image.morphology import morph_dilate, morph_erode


@dataclass
class Vector2:
    x: float
    y: float
    ZERO: ClassVar[Vector2]
    UP: ClassVar[Vector2]
    DOWN: ClassVar[Vector2]
    LEFT: ClassVar[Vector2]
    RIGHT: ClassVar[Vector2]

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: float) -> Vector2:
        return Vector2(self.x * scalar, self.y * scalar)

    def dot(self, other: Vector2) -> float:
        return self.x * other.x + self.y * other.y

    def norm(self) -> float:
        return self.dot(self) ** 0.5

    def normalized(self) -> Vector2:
        norm = self.norm()
        return Vector2(self.x / norm, self.y / norm)

    def distance(self, other: Vector2) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def perp(self) -> Vector2:
        return Vector2(1, -self.x / self.y)

    def as_tuple(self) -> Tuple[float, float]:
        return self.x, self.y

    def as_int_tuple(self) -> Tuple[int, int]:
        return int(round(self.x)), int(round(self.y))

    def angle_with_x_axis(self, other: Vector2) -> float:
        diff = other - self
        rad = atan2(diff.y, diff.x)
        if rad < 0:
            rad += 2 * pi
        return degrees(rad)

    def __str__(self) -> str:
        return str(astuple(self))

    def __repr__(self) -> str:
        return f"Vector2 {asdict(self)}"


Vector2.ZERO = Vector2(0.0, 0.0)
Vector2.UP = Vector2(0.0, 1.0)
Vector2.DOWN = Vector2(0.0, -1.0)
Vector2.LEFT = Vector2(-1.0, 0.0)
Vector2.RIGHT = Vector2(1.0, 0.0)


class MicroEntity:
    def __init__(self, name, custom_data=None):
        self.name = name
        self.custom_data = custom_data
        if self.custom_data is None:
            self.custom_data = {}

    def set_data(self, data_name, data):
        self.custom_data[data_name] = data

    def get_data(self, data_name):
        return self.custom_data[data_name]


class MicroEntity2D(Vector2, MicroEntity):
    def __init__(self, name, mask, x, y, custom_data=None):
        MicroEntity.__init__(self, name, custom_data=custom_data)
        Vector2.__init__(self, x, y)
        self.mask = mask

    def get_mean(self, channel):
        return np.mean(channel, where=self.mask > 0)

    def get_sum(self, channel, threshold=0):
        return np.sum(channel, where=self.mask > threshold)

    def get_max(self, channel):
        return np.max(channel, where=self.mask > 0, initial=0)

    @property
    def area(self):
        return cv2.countNonZero(self.mask)

    @property
    def boundary(self):
        if self.area == 0:
            return None
        return contours_find(self.mask)

    @property
    def perimeter(self):
        return cv2.arcLength(self.boundary[0], True)

    @property
    def roundness(self):
        return 4 * math.pi * (self.area / self.perimeter**2)

    @property
    def min_x(self):
        return np.min(self.boundary[0], axis=0)[0, 0]

    @property
    def max_x(self):
        return np.max(self.boundary[0], axis=0)[0, 0]


class Particle2D(MicroEntity2D):
    pass


class Cell2D(MicroEntity2D):
    def __init__(self, name, mask, x, y, custom_data=None):
        super().__init__(name, mask, x, y, custom_data)

    def dilated_mask(self, dilation_size=1):
        return morph_dilate(self.mask, "circle", half_kernel_size=dilation_size)

    def eroded_mask(self, dilation_size=1):
        return morph_erode(self.mask, "circle", half_kernel_size=dilation_size)

    @staticmethod
    def from_mask(cell_mask, cell_name, area_range=None, custom_data={}):
        mask = np.zeros(cell_mask.shape, dtype=np.uint8)
        cnts = contours_find(cell_mask)
        if len(cnts) == 1:
            cnt = cnts[0]
            if len(cnt) >= 4:
                M = cv2.moments(cnt)
                if M["m00"] == 0:
                    return None
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                mask = contours_fill(mask, [cnt], color=255)

                if area_range is not None:
                    area = cv2.countNonZero(mask)
                    if area_range[0] <= area <= area_range[1]:
                        return Cell2D(cell_name, mask, cx, cy, custom_data=custom_data)
                    else:
                        return None
                else:
                    return Cell2D(cell_name, mask, cx, cy, custom_data=custom_data)
        return None
