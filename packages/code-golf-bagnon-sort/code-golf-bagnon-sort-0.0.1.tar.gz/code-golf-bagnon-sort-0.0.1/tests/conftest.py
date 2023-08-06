from __future__ import annotations

import pytest

from code_golf_bagnon_sort.bag import Bag
from code_golf_bagnon_sort.item import Item, ItemType


@pytest.fixture
def stacked_soul():
    return Item(id=2, max_stack=10, stack=3, type=ItemType.SOUL)


@pytest.fixture
def dust():
    return Item(id=3, max_stack=20, stack=15, type=ItemType.ENCHANTING)


@pytest.fixture
def standard_bag(stacked_soul, dust):
    main_bag = Bag(id="1", size=20, item_type=ItemType.STANDARD)
    weapon = Item(id=1, max_stack=1, stack=1, type=ItemType.STANDARD)
    same_weapon = Item(id=1, max_stack=1, stack=1, type=ItemType.STANDARD)
    other_stacked_soul = Item(id=2, max_stack=10, stack=8, type=ItemType.SOUL)
    main_bag.put(slot=5, item=weapon)
    main_bag.put(slot=9, item=same_weapon)
    main_bag.put(slot=1, item=stacked_soul)
    main_bag.put(slot=3, item=other_stacked_soul)
    main_bag.put(slot=2, item=dust)
    return main_bag


@pytest.fixture
def soul_bag():
    return Bag(id="2", size=6, item_type=ItemType.SOUL)


@pytest.fixture
def enchanting_bag():
    return Bag(id="3", size=6, item_type=ItemType.ENCHANTING)


@pytest.fixture
def bags(standard_bag, soul_bag, enchanting_bag):

    return [standard_bag, soul_bag, enchanting_bag]
