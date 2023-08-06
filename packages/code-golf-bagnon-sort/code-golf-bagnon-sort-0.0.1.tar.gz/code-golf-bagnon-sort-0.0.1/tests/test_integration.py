from __future__ import annotations

import pytest

from code_golf_bagnon_sort.checker import MoveChecker, WrongMove


@pytest.fixture
def checker():
    bags = [
        {
            "id": 1,
            "size": 20,
            "type": 0,
            "items": [
                {"bag": 1, "slot": 1, "id": 2, "stack": 3, "max_stack": 10, "type": 8},
                {"bag": 1, "slot": 2, "id": 3, "stack": 15, "max_stack": 20, "type": 2},
                {"bag": 1, "slot": 3, "id": 2, "stack": 8, "max_stack": 10, "type": 8},
                {"bag": 1, "slot": 5, "id": 1, "stack": 1, "max_stack": 1, "type": 0},
                {"bag": 1, "slot": 9, "id": 1, "stack": 1, "max_stack": 1, "type": 0},
            ],
        },
        {"id": 2, "size": 6, "type": 8, "items": []},
        {"id": 3, "size": 6, "type": 2, "items": []},
    ]
    return MoveChecker(bags=bags)  # type: ignore


def test_one_reasonable_move(checker, dust):
    ticks = [
        [{"bo": 1, "so": 2, "bd": 3, "sd": 3}],
    ]
    checker.apply_move(ticks)
    moved_dust = checker.bags[2].pick(slot=3)
    assert moved_dust == dust


def test_one_impossible_move(checker):
    ticks = [
        [{"bo": 1, "so": 3, "bd": 3, "sd": 3}],
    ]
    with pytest.raises(
        WrongMove,
        match="item with type ItemType.SOUL in bag that can handle type ENCHANTING",
    ):
        checker.apply_move(ticks)
    ticks = [
        [{"bo": 1, "so": 3, "bd": 3, "sd": 6}],
    ]
    with pytest.raises(WrongMove, match="slot 6 that does not exist in Bag 3"):
        checker.apply_move(ticks)
    ticks = [
        [{"bo": 1, "so": 3, "bd": 3, "sd": -7}],
    ]
    with pytest.raises(WrongMove, match="slot -7 that does not exist in Bag 3"):
        checker.apply_move(ticks)


def test_full_sort_two_tics(checker):

    ticks = [
        # bags = [
        #     {
        #         "id": 1,
        #         "size": 20,
        #         "type": 0,
        #         "items": [
        #             {"bag": 1, "slot": 1, "id": 2, "stack": 3,
        #               "max_stack": 10, "type": 8},
        #             {"bag": 1, "slot": 2, "id": 3, "stack": 15,
        #               "max_stack": 20, "type": 2},
        #             {"bag": 1, "slot": 3, "id": 2, "stack": 8,
        #               "max_stack": 10, "type": 8},
        #             {"bag": 1, "slot": 5, "id": 1, "stack": 1,
        #               "max_stack": 1, "type": 0},
        #             {"bag": 1, "slot": 9, "id": 1, "stack": 1,
        #               "max_stack": 1, "type": 0},
        #         ],
        #     },
        #     {"id": 2, "size": 6, "type": 8, "items": []},
        #     {"id": 3, "size": 6, "type": 2, "items": []},
        # ]
        [
            {"bo": 1, "so": 1, "bd": 2, "sd": 1},
            {"bo": 1, "so": 2, "bd": 3, "sd": 1},
            {"bo": 1, "so": 3, "bd": 2, "sd": 2},
            {"bo": 1, "so": 5, "bd": 1, "sd": 1},
            {"bo": 1, "so": 9, "bd": 1, "sd": 2},
        ],
        [
            {"bo": 1, "so": 3, "bd": 3, "sd": 3},
            {"bo": 1, "so": 3, "bd": 3, "sd": 3},
            {"bo": 1, "so": 3, "bd": 3, "sd": 3},
            {"bo": 1, "so": 3, "bd": 3, "sd": 3},
        ],
    ]
    checker.apply_move(ticks)
