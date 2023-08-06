from __future__ import annotations

import sys

from code_golf_bagnon_sort.bag import Bag
from code_golf_bagnon_sort.item import Item, ItemType

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class DictItem(TypedDict):
    id: int
    bag: int
    slot: int
    type: ItemType
    stack: int
    max_stack: int


class DictBag(TypedDict):
    id: int
    type: ItemType
    size: int
    items: list[DictItem]


class DictMove(TypedDict):
    bo: int
    so: int
    bd: int
    sd: int


class WrongMove(Exception):
    """Raised when a wrong move was detected by the checker."""


class MoveChecker:
    tick_descr = {
        0: "first",
        1: "second",
        2: "third",
    }

    def __init__(self, bags: list[DictBag]):
        self.bags: list[Bag] = []
        for bag in bags:
            current_bag = Bag(id=bag["id"], item_type=bag["type"], size=bag["size"])
            for item in bag["items"]:
                current_item = Item(
                    id=item["id"],
                    max_stack=item["max_stack"],
                    stack=item["stack"],
                    type=item["type"],
                )
                current_bag.put(item=current_item, slot=item["slot"])
            self.bags.append(current_bag)

    def apply_move(self, ticks: list[list[DictMove]]):
        problems = []
        for i, moves in enumerate(ticks):
            print(f"Bag state: {self.bags}")
            tick_desc = self.tick_descr.get(i, f"{i + 1}th")
            for j, move in enumerate(moves):
                try:
                    item = self.bags[move["bo"] - 1].pick(move["so"])
                    self.bags[move["bd"] - 1].put(item, slot=move["sd"])
                except RuntimeError as e:
                    move_desr = self.tick_descr.get(j, f"{j + 1}th")
                    problems.append(f"In the {move_desr} move ({move}) : {e}")
            if problems:
                plural = "s" if len(problems) > 1 else ""
                raise WrongMove(
                    f"Wrong move{plural} in the {tick_desc} tick:\n"
                    + "\n".join(problems)
                )
        print(f"Final result: {self.bags}: {problems}")
