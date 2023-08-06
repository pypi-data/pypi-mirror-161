from __future__ import annotations

from code_golf_bagnon_sort.item import Item, ItemType


class Bag:
    # pylint: disable=redefined-builtin
    def __init__(
        self, id: int, size: int, item_type: ItemType | int = ItemType.STANDARD
    ):
        self.id: int = id
        self.size: int = size
        self.slots: list[Item | None] = [None] * size
        if isinstance(item_type, int):
            item_type = ItemType(item_type)
        self.item_type: ItemType = item_type

    def __str__(self):
        repr = f"Bag {self.id} ({self.item_type} - {self.size})\n"
        for i, slot in enumerate(self.slots):
            if slot is not None:
                repr += f"\t{i}: {slot.__repr__().format(bag=self.id, slot=i)}\n"
        return repr

    def __repr__(self):
        repr = (
            f'{{"id": {self.id}, "size": {self.size}, "type": {self.item_type.value}, '
        )
        items = []
        for i, slot in enumerate(self.slots):
            if slot is not None:
                items.append(f"{{{slot.__repr__().format(bag=self.id, slot=i)}}}")
        return repr + '"items": [' + ", ".join(items) + "]}"

    def pick(self, slot: int) -> Item | None:
        try:
            item = self.slots[slot]
        except IndexError as e:
            raise RuntimeError(
                f"Tried to pick an item from slot {slot} that does not exist in {self}"
            ) from e
        self.slots[slot] = None
        return item

    def stack(self, slot, item: Item) -> Item | None:
        other = self.slots[slot]
        assert_msg = f"Trying to stack {other} and {item}, that ain't gonna work"
        assert other.id == item.id, assert_msg
        assert other.max_stack == item.max_stack, assert_msg
        assert other.type == item.type, assert_msg
        total_item = other.stack + item.stack
        other.stack = max(other.max_stack, total_item)
        return Item(
            id=other.id,
            stack=other.stack - total_item,
            max_stack=other.max_stack,
            type=other.type,
        )

    def put(self, item: Item | None, slot: int) -> Item | None:
        existing_item = self.pick(slot)
        if item is None:
            return existing_item
        if self.item_type not in (ItemType.STANDARD, item.type):
            raise RuntimeError(
                f"Tried to put an item with type {item.type} in bag that can handle"
                f" type {self.item_type.name}"
            )
        try:
            self.slots[slot] = item
        except KeyError as e:
            raise RuntimeError(
                f"Tried to put an item in slot {slot} that does not exist in {self}"
            ) from e
        if existing_item is None:
            return None
        if item.id != existing_item.id or item.max_stack == 1:
            return existing_item
        return self.stack(slot, existing_item)
