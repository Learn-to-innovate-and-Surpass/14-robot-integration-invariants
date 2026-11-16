"""Explicit six-component pose semantics and fake motion feedback checks."""
from dataclasses import dataclass
import math


def finite_numbers(values, length):
    if len(values) != length or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError("wrong component count or non-finite/non-numeric value")
    return tuple(float(v) for v in values)


def label(value):
    if (not isinstance(value, str) or not value.strip() or
            value.strip().casefold() in {"unknown", "?", "none", "null", "n/a", "undefined", "unset", "tbd", "-"}):
        raise ValueError("frame/tool identity must be explicit")
    return value


@dataclass(frozen=True)
class Pose6:
    values: tuple
    length_unit: str
    angle_unit: str
    frame: str
    tool: str
    convention: str = "rpy_xyz"

    def __post_init__(self):
        object.__setattr__(self, "values", finite_numbers(self.values, 6))
        label(self.frame)
        label(self.tool)
        if self.length_unit not in ("mm", "m") or self.angle_unit not in ("deg", "rad"):
            raise ValueError("unknown length/angle unit")
        if self.convention != "rpy_xyz":
            raise ValueError("orientation convention not implemented")

    def canonical(self):
        length_scale = 1000.0 if self.length_unit == "m" else 1.0
        angle_scale = math.pi / 180 if self.angle_unit == "deg" else 1.0
        values = tuple(v * length_scale for v in self.values[:3]) + tuple(v * angle_scale for v in self.values[3:])
        return Pose6(values, "mm", "rad", self.frame, self.tool, self.convention)


def quaternion_from_rpy(angles):
    """Active Rz(yaw) Ry(pitch) Rx(roll), quaternion ordered w,x,y,z."""
    roll, pitch, yaw = finite_numbers(angles, 3)
    cr, cp, cy = (math.cos(a / 2) for a in (roll, pitch, yaw))
    sr, sp, sy = (math.sin(a / 2) for a in (roll, pitch, yaw))
    return (cr * cp * cy + sr * sp * sy,
            sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy,
            cr * cp * sy - sr * sp * cy)


def quaternion_angle_degrees(first, second):
    a, b = finite_numbers(first, 4), finite_numbers(second, 4)
    def normalized(values):
        scale = max(abs(value) for value in values)
        if scale == 0:
            raise ValueError("zero quaternion")
        scaled = tuple(value / scale for value in values)
        norm = math.hypot(*scaled)
        return tuple(value / norm for value in scaled)
    a, b = normalized(a), normalized(b)
    # Align equivalent signs, then use chord lengths to retain tiny angles.
    if math.fsum(x * y for x, y in zip(a, b)) < 0:
        b = tuple(-value for value in b)
    difference = math.hypot(*(x - y for x, y in zip(a, b)))
    total = math.hypot(*(x + y for x, y in zip(a, b)))
    return math.degrees(4 * math.atan2(difference, total))


def pose_error(target, actual):
    if (target.frame, target.tool, target.convention) != (actual.frame, actual.tool, actual.convention):
        raise ValueError("frame/tool/orientation semantics mismatch")
    target, actual = target.canonical(), actual.canonical()
    translation_mm = math.dist(target.values[:3], actual.values[:3])
    if not math.isfinite(translation_mm):
        raise ValueError("unrepresentable translation error")
    orientation_deg = quaternion_angle_degrees(quaternion_from_rpy(target.values[3:]), quaternion_from_rpy(actual.values[3:]))
    return translation_mm, orientation_deg


def verify_feedback(target, actual, *, translation_limit_mm, angle_limit_deg):
    limits = finite_numbers((translation_limit_mm, angle_limit_deg), 2)
    if min(limits) < 0:
        raise ValueError("negative tolerance")
    error = pose_error(target, actual)
    if error[0] > limits[0] or error[1] > limits[1]:
        raise ValueError("actual pose outside explicit tolerance")
    return error


class FakeExecutor:
    """No robot APIs; a receipt and an independent fake pose are required."""
    def __init__(self, supports_linear=True):
        self.supports_linear = supports_linear

    def complete(self, target, actual, *, motion_kind, receipt,
                 translation_limit_mm, angle_limit_deg):
        if motion_kind != "linear" or not self.supports_linear:
            raise ValueError("required linear motion semantics unavailable")
        if receipt != "completed":
            raise ValueError("fake execution failed/timed out")
        return verify_feedback(target, actual, translation_limit_mm=translation_limit_mm, angle_limit_deg=angle_limit_deg)
