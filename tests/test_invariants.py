import math
import unittest
from invariants import FakeExecutor, Pose6, pose_error, quaternion_angle_degrees, verify_feedback


def pose(values=(0, 0, 0, 0, 0, 0), **kwargs):
    options = dict(length_unit="mm", angle_unit="deg", frame="synthetic-frame", tool="synthetic-tool")
    options.update(kwargs)
    return Pose6(values, **options)


class InvariantTests(unittest.TestCase):
    def test_explicit_conversion(self):
        first = pose((.001, .002, .003, 0, 0, 180), length_unit="m")
        second = pose((1, 2, 3, 0, 0, math.pi), angle_unit="rad")
        distance, angle = pose_error(first, second)
        self.assertAlmostEqual(distance, 0)
        self.assertAlmostEqual(angle, 0)

    def test_reject_invalid_components_and_semantics(self):
        for values in ((0,) * 5, (0, 0, 0, 0, 0, math.nan), (0, 0, 0, 0, 0, math.inf), (0, 0, 0, 0, 0, True)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                pose(values)
        for options in (dict(length_unit="unknown"), dict(angle_unit="unknown"), dict(frame=""), dict(convention="unknown")):
            with self.assertRaises(ValueError):
                pose(**options)
        with self.assertRaises(ValueError):
            pose_error(pose(), pose(tool="other"))

    def test_placeholder_frame_and_tool_are_rejected(self):
        for value in ("unknown", " UNKNOWN ", "?", "none", "null", "n/a", "undefined", "unset", "tbd", "-"):
            for field in ("frame", "tool"):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    pose(**{field: value})

    def test_quaternion_sign_and_zero(self):
        self.assertAlmostEqual(quaternion_angle_degrees((1, 0, 0, 0), (-1, 0, 0, 0)), 0)
        with self.assertRaises(ValueError):
            quaternion_angle_degrees((0, 0, 0, 0), (1, 0, 0, 0))

    def test_identical_pose_zero_tolerance_and_subnormal_quaternions(self):
        angles = (.48445211389369014, -.649175723618987, 2.9923990819306976)
        same = pose((0, 0, 0) + angles, angle_unit="rad")
        self.assertEqual(verify_feedback(same, same, translation_limit_mm=0, angle_limit_deg=0), (0, 0))
        self.assertAlmostEqual(quaternion_angle_degrees((5e-324, 5e-324, 0, 0), (5e-324, 0, 0, 0)), 90)
        self.assertAlmostEqual(quaternion_angle_degrees((1e308, 1e308, 0, 0), (1e308, 0, 0, 0)), 90)

    def test_orientation_only_error_checks_tolerance(self):
        target = pose()
        for degrees in (.05, 1e-8):
            actual = pose((0, 0, 0, 0, 0, degrees))
            with self.subTest(degrees=degrees):
                error = verify_feedback(target, actual, translation_limit_mm=0, angle_limit_deg=degrees * 1.1)
                self.assertAlmostEqual(error[1], degrees)
                with self.assertRaises(ValueError):
                    verify_feedback(target, actual, translation_limit_mm=0, angle_limit_deg=degrees * .9)

    def test_overflow_is_explicit(self):
        with self.assertRaises(ValueError):
            pose((1e308, 0, 0, 0, 0, 0), length_unit="m").canonical()
        with self.assertRaises(ValueError):
            pose_error(pose((1e308, 0, 0, 0, 0, 0)), pose((-1e308, 0, 0, 0, 0, 0)))

    def test_fresh_feedback_and_motion_semantics(self):
        executor = FakeExecutor()
        options = dict(motion_kind="linear", receipt="completed", translation_limit_mm=.1, angle_limit_deg=.1)
        self.assertEqual(executor.complete(pose(), pose(), **options), (0, 0))
        for changed in (dict(receipt="timeout"), dict(receipt="error"), dict(motion_kind="joint")):
            with self.assertRaises(ValueError):
                executor.complete(pose(), pose(), **(options | changed))
        with self.assertRaises(ValueError):
            FakeExecutor(False).complete(pose(), pose(), **options)
        with self.assertRaises(ValueError):
            executor.complete(pose(), pose((1, 0, 0, 0, 0, 0)), **options)
        with self.assertRaises(ValueError):
            verify_feedback(pose(), pose(), translation_limit_mm=-1, angle_limit_deg=1)


if __name__ == "__main__":
    unittest.main()
