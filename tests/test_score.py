from app import score

speed_limits = {"ideal_min": 0, "ideal_max": 8, "edge_min": 0, "edge_max": 13}


def test_speed_outside_edge_upper():
    assert score(14, speed_limits) == 0


def test_speed_outside_edge_ideal_same_bound_lower():
    assert score(0, speed_limits) == 1


def test_speed_within_ideal():
    assert score(2, speed_limits) == 1


def test_speed_within_edge_upper():
    assert score(9, speed_limits) == 0.8


def test_speed_within_edge_upper2():
    assert score(12, speed_limits) == 12 * -0.2 - 13 * -0.2
