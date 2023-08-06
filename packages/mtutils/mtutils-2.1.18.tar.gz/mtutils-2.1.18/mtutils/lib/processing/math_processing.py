import math
import numpy as np
from ..utils import cal_distance
from ..utils import is_iterable


def cartesian_to_polar(point_xy, center_xy, reverse_y=True):
    x, y = point_xy
    center_x, center_y = center_xy
    r = cal_distance(point_xy, center_xy)
    if r == 0:
        theta = 0
    elif r > 0:
        y_ = y - center_y
        if reverse_y:
            y_ = - y_
        x_ = x - center_x
        theta = math.asin(abs(y_) / max(1, abs(r)))
        if y_ >= 0 and x_ >= 0:
            pass
        elif y_ >= 0 and x_ < 0:
            theta = np.pi - theta
        elif y_ < 0 and x_ < 0:
            theta = np.pi + theta
        elif y_ < 0 and x_ >= 0:
            theta = 2 * np.pi - theta
        else:
            raise RuntimeError(f'bad y_ {y_} x_ {x_}')
    else:
        raise RuntimeError(f'bad distance {r}')
    return r, theta


def polar_to_cartesian(r, theta, center_xy, reverse_y=False):
    center_x, center_y = center_xy
    if reverse_y:
        y = center_y - r * math.sin(theta)
    else:
        y = center_y + r * math.sin(theta)
    x = center_x + r * math.cos(theta)

    point_xy = [x, y]
    return point_xy


class LogicOp:
    @staticmethod
    def EqualTo(value):
        def func(input):
            if input == value:
                return True
            else:
                return False
        return func

    @staticmethod
    def NotEqualTo(value):
        def func(input):
            if input != value:
                return True
            else:
                return False
        return func

    @staticmethod
    def LargerThan(value):
        def func(input):
            if input > value:
                return True
            else:
                return False
        return func

    @staticmethod
    def LessThan(value):
        def func(input):
            if input < value:
                return True
            else:
                return False
        return func

    @staticmethod
    def NotLessThan(value):
        def func(input):
            if input >= value:
                return True
            else:
                return False
        return func
    
    @staticmethod
    def NotLargerThan(value):
        def func(input):
            if input <= value:
                return True
            else:
                return False
        return func
    
    @staticmethod
    def In(value):
        assert is_iterable(value)
        def func(input):
            if input in value:
                return True
            else:
                return False
        return func

    @staticmethod
    def NotIn(value):
        assert is_iterable(value)
        def func(input):
            if input in value:
                return False
            else:
                return True
        return func
    
    @staticmethod
    def Is(value):
        def func(input):
            if input is value:
                return True
            else:
                return False
        return func
    
    @staticmethod
    def IsNot(value):
        def func(input):
            if input is not value:
                return True
            else:
                return False
        return func
    
    @staticmethod
    def IsTrue():
        def func(input):
            if input:
                return True
            else:
                return False
        return func
    
    @staticmethod
    def IsFalse():
        def func(input):
            if not input:
                return True
            else:
                return False
        return func

