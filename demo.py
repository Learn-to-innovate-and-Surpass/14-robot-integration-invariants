from invariants import FakeExecutor, Pose6


def main():
    target = Pose6((.01, .02, .03, 0, 0, 90), "m", "deg", "synthetic-frame", "synthetic-tool")
    actual = Pose6((10, 20, 30, 0, 0, 1.5707963267948966), "mm", "rad", "synthetic-frame", "synthetic-tool")
    print("canonical target (mm, rad):", target.canonical().values)
    print("fake feedback error (mm, deg):", FakeExecutor().complete(
        target, actual, motion_kind="linear", receipt="completed", translation_limit_mm=.1, angle_limit_deg=.1))
    try:
        FakeExecutor().complete(target, actual, motion_kind="joint", receipt="completed", translation_limit_mm=.1, angle_limit_deg=.1)
    except ValueError as error:
        print("semantic rejection:", error)


if __name__ == "__main__":
    main()
