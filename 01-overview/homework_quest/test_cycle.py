from homework_quest.cycle import select_winners


def test_clear_winner():
    assert select_winners({1: 100, 2: 80, 3: 50}) == [1]


def test_two_way_tie_at_top():
    winners = select_winners({1: 100, 2: 100, 3: 50})
    assert sorted(winners) == [1, 2]


def test_three_way_tie_at_top():
    winners = select_winners({1: 75, 2: 75, 3: 75, 4: 20})
    assert sorted(winners) == [1, 2, 3]


def test_empty_household():
    assert select_winners({}) == []
