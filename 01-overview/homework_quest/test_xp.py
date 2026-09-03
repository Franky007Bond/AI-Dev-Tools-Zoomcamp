from homework_quest.xp import xp_from_minutes


def test_five_minutes_returns_ten_xp():
    assert xp_from_minutes(5) == 10


def test_forty_five_minutes_returns_one_hundred_xp():
    assert xp_from_minutes(45) == 100


def test_zero_minutes_returns_zero_xp():
    assert xp_from_minutes(0) == 0


def test_sixty_plus_minutes_scales_beyond_one_hundred():
    assert xp_from_minutes(60) == 134


def test_midpoint_interpolation():
    assert xp_from_minutes(25) == 55
