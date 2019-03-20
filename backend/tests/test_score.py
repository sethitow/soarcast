from app import score


def test_speed_outside_edge_upper():
    speed_limits = {"ideal_min": 0, "ideal_max": 8, "edge_min": 0, "edge_max": 13}
    assert score(14, speed_limits) == 0

def test_speed_outside_edge_lower():
    speed_limits = {"ideal_min": 5, "ideal_max": 8, "edge_min": 3, "edge_max": 13}
    assert score(1, speed_limits) == 0

def test_speed_outside_edge_ideal_same_bound_lower():
    speed_limits = {"ideal_min": 0, "ideal_max": 8, "edge_min": 0, "edge_max": 13}
    assert score(0, speed_limits) == 1

def test_speed_outside_edge_ideal_same_bound_upper():
    speed_limits = {"ideal_min": 0, "ideal_max": 13, "edge_min": 0, "edge_max": 13}
    assert score(13, speed_limits) == 1

def test_speed_within_ideal():
    speed_limits = {"ideal_min": 0, "ideal_max": 8, "edge_min": 0, "edge_max": 13}
    assert score(2, speed_limits) == 1

def test_speed_within_edge_upper():
    speed_limits = {"ideal_min": 0, "ideal_max": 8, "edge_min": 0, "edge_max": 13}
    assert score(9, speed_limits) == 0.8

def test_speed_within_edge_upper2():
    speed_limits = {"ideal_min": 0, "ideal_max": 8, "edge_min": 0, "edge_max": 13}
    assert score(12, speed_limits) == 12 * -0.2 - 13 * -0.2

def test_speed_within_edge_lower():
    speed_limits = {"ideal_min": 5, "ideal_max": 8, "edge_min": 2, "edge_max": 13}
    assert score(4, speed_limits) == 2/3

def test_speed_within_edge_lower2():
    speed_limits = {"ideal_min": 5, "ideal_max": 8, "edge_min": 2, "edge_max": 13}
    assert score(3, speed_limits) == 1/3
