from collections import defaultdict
import random
from typing import Optional

from connection_data import AreaDoor
from fillInterface import FillAlgorithm
from item_data import Item, Items, items_unpackable
from loadout import Loadout
from location_data import Location, spacePortLocs
from solver import solve
import logicExpert

_minor_items = {
    Items.Missile: 39,
    Items.Super: 11,
    Items.PowerBomb: 6,
    Items.Energy: 13,
    Items.Reserve: 7,
    Items.Weapon: 8,
    Items.Spark: 3,
}
# TODO: verify item counts

# Placing these items outside these areas opens up the possiblity of softlock
forced_zone_items = {
    'zone-1': [Items.Charge, Items.Morph, Items.Bombs, Items.Missile],
    'zone-2': [
        Items.Boostball,
        Items.SpeedBooster,
        Items.Super,
        Items.Varia,
        # need 3 energy tanks to get a shinespark out of zone-2
        Items.Energy,
        Items.Energy,
        Items.Energy,
    ],
    'zone-3': [Items.GravitySuit, Items.SpaceJump, Items.PowerBomb],
}

def get_available_zone_locations(loadout, zone_name):
    available_locations = []
    for location in loadout.game.all_locations.values():
        if location['fullitemname'] == 'Super Get':
            pass
        if location['zone'] == zone_name:
            if logicExpert.location_logic[location['fullitemname']](loadout):
                available_locations.append(location)
    return available_locations

class FillAssumed(FillAlgorithm):
    connections: list[tuple[AreaDoor, AreaDoor]]

    # earlyItemList: list[Item]
    prog_items: list[Item]
    extra_items: list[Item]
    itemLists: list[list[Item]]

    def __init__(self, game) -> None:
        self.game = game
        self.connections = game.connections

        self.forced_item_locations = []
        # TODO ASCENT_FIX should be a CLI option with choices:
        # force - force items into force item locations
        # duplicate - if necessary, replace a random non-unique item with duplicate key item
        # open - replace brown doors with pink doors to allow backtracking
        # none - do nothing and risk softlock
        if game.options.ascent_fix in ['force', 'duplicate']:
            self.forced_item_locations = self.get_forced_locations()

        # self.earlyItemList = [
        #     Missile,
        #     Morph,
        #     GravityBoots
        # ]
        self.prog_items = [
            Items.Missile,
            Items.Morph,
            Items.Super,
            Items.Grapple,
            Items.PowerBomb,
            Items.Boostball,
            Items.Bombs,
            Items.HiJump,
            Items.GravitySuit,
            Items.Varia,
            Items.Wave,
            Items.SpeedBooster,
            Items.Spazer,
            Items.Ice,
            Items.Plasma,
            Items.Screw,
            Items.SpaceJump,
            Items.Charge,
            Items.Energy,
            Items.Reserve,
            Items.Weapon,
            Items.Spark
        ]
        #assert len([it for it in self.prog_items if (it != Items.Energy and it != Items.Artifact)]) + 1 == len(set(self.prog_items)), \
        #    "duplicate majors?"
        self.extra_items = []
        for it, n in _minor_items.items():
            self.extra_items.extend([it for _ in range(n)])

        self.itemLists = [self.prog_items, self.extra_items]

    def get_forced_locations(self):
        # This is highly ascent specific
        # Get locations for the key items in each zone
        # "With the bare minimum items to access the zone, the key items will reachable
        forced_locations = []
        loadout = Loadout(self.game)

        # You can't leave zone one without these so no reason to force them
        for item in forced_zone_items['zone-1']:
            loadout.append(item)

        for item in forced_zone_items['zone-2']: # TODO shuffle these?
            # find a location the item could be, and then add it to the loadout
            locations = get_available_zone_locations(loadout, 'zone-2')
            forced_locations.append([item, locations])
            loadout.append(item)

        # Repeat with zone 3
        for item in forced_zone_items['zone-3']: # TODO shuffle these?
            # find a location the item could be, and then add it to the loadout
            locations = get_available_zone_locations(loadout, 'zone-3')
            forced_locations.append([item, locations])
            loadout.append(item)
        return forced_locations

    def _get_accessible_locations(self, loadout: Loadout) -> list[Location]:
        _, _, locs = solve(loadout.game, loadout)
        return locs

    def _get_available_locations(self, loadout: Loadout) -> list[Location]:
        return [loc for loc in self._get_accessible_locations(loadout) if loc["item"] is None]

    def _get_empty_locations(self, all_locations: dict[str, Location]) -> list[Location]:
        return [loc for loc in all_locations.values() if loc["item"] is None]

    @staticmethod
    def _choose_location(locs: list[Location], spaceport_deprio: int) -> Location:
        """
        to work against spaceport front-loading,
        because 1 progression item in space port
        will lead to more progression items in spaceport
        """
        distribution = locs.copy()
        for _ in range(spaceport_deprio):
            for loc in locs:
                if loc["fullitemname"] not in spacePortLocs:
                    distribution.append(loc)
        return random.choice(distribution)

    def choose_forced_placement(self):
        # select an item and a random location from the force list
        forced_item, forced_locations = self.forced_item_locations.pop()
        forced_location = random.choice(forced_locations)
        print('forcing', forced_item[0], forced_location['fullitemname'], len(forced_locations))

        # remove the location from the rest of the force lsit
        for _, locations in self.forced_item_locations:
            if forced_location in locations:
                locations.remove(forced_location)

        if forced_item in self.prog_items:
            self.prog_items.remove(forced_item)
        else:
            self.extra_items.remove(forced_item)
        return forced_location, forced_item

    def choose_placement(self,
                         availableLocations: list[Location],
                         loadout: Loadout) -> Optional[tuple[Location, Item]]:
        if self.game.options.ascent_fix == 'force' and self.forced_item_locations:
            return self.choose_forced_placement()

        """ returns (location to place an item, which item to place there) """

        from_items = (
            self.prog_items if len(self.prog_items) else (
                self.extra_items
            )
        )

        assert len(from_items), "tried to place item when placement algorithm has 0 items left in item pool"

        item_to_place = random.choice(from_items)

        from_items.remove(item_to_place)

        if from_items is self.prog_items:
            loadout = Loadout(loadout.game)
            for item in from_items:
                loadout.append(item)
            available_locations = self._get_available_locations(loadout)
        else:  # extra
            available_locations = self._get_empty_locations(loadout.game.all_locations)
        if len(available_locations) == 0:
            return None

        # This magic number 2 could be an option for "How loaded do you want the spaceport to be?"
        # (lower number means more progression items in spaceport)
        return self._choose_location(available_locations, 2), item_to_place

    def count_items_remaining(self) -> int:
        return sum(len(li) for li in self.itemLists)

    def remove_from_pool(self, item: Item) -> None:
        """ removes this item from the item pool """
        pass  # removed in placement function

    def validate(self, locations):
        if self.game.options.ascent_fix == 'force':
            zone_items = defaultdict(list)
            for loc in self.game.all_locations.values():
                zone_items[loc['zone']].append(loc['item'])
            for zone, items in forced_zone_items.items():
                for item in items:
                    try:
                        zone_items[zone].remove(item)
                    except ValueError as e:
                        raise ValueError(f'{item[0]} is not in {zone}')