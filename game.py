from dataclasses import dataclass, field
import random
from typing import TYPE_CHECKING, Literal, Mapping, Type, Union

from connection_data import AreaDoor, vanilla_doors
from item_data import Item
from location_data import Location
from logicInterface import LogicInterface
from logic_shortcut import LogicShortcut


def door_factory() -> dict[AreaDoor, Union[Item, LogicShortcut]]:
    return vanilla_doors

@dataclass
class GameOptions:
    logic: LogicInterface
    fill_choice: str
    can: list = field(default_factory=lambda: [])
    seed: int = field(default_factory=lambda: random.randint(0, 9999999))
    ascent_fix: bool = field(default_factory= lambda: True)
    plando: dict = field(default_factory= dict)
    def get_file_hash(self):
        fill = self.fill_choice[0]
        fix = 'F' if self.ascent_fix else 'N'
        plando = '_plando' if self.plando else ''
        return f'_{fill}{fix}{plando}_{self.seed}'.upper()


@dataclass
class Game:
    """ a composition of all the components that make up the generated seed """
    options: GameOptions
    logic: Type[LogicInterface]
    all_locations: dict[str, Location]
    area_rando: bool
    connections: list[tuple[AreaDoor, AreaDoor]]
    item_placement_spoiler: str = ""
    door_data: Mapping[AreaDoor, Union[Item, LogicShortcut]] = field(default_factory=door_factory)
