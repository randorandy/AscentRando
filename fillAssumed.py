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

# reverse lookup for the above
forced_item_zone = {}
for zone_name, items in forced_zone_items.items():
    for item in items:
        forced_item_zone[item] = zone_name

class FillAssumed(FillAlgorithm):
    connections: list[tuple[AreaDoor, AreaDoor]]

    # earlyItemList: list[Item]
    prog_items: list[Item]
    extra_items: list[Item]
    itemLists: list[list[Item]]

    def __init__(self, game) -> None:
        self.game = game
        self.connections = game.connections

        # This needs to be run now because _get_available_locations requires empty locations
        if self.game.options.ascent_fix:
            self.forced_locations = self.get_forced_locations()

        self.plando = []
        if game.options.plando:
            locations = game.all_locations.values()
            for loc_name, item_name in game.options.plando.items():
                location = next(l for l in locations if l['fullitemname'] == loc_name)
                item = getattr(Items, item_name)
                self.plando.append([location, item])

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
            locations = self._get_available_locations(loadout)
            locations = [l for l in locations if l['zone'] == 'zone-2']
            forced_locations.append([item, locations])
            loadout.append(item)

        # Repeat with zone 3
        for item in forced_zone_items['zone-3']: # TODO shuffle these?
            # find a location the item could be, and then add it to the loadout
            locations = self._get_available_locations(loadout)
            locations = [l for l in locations if l['zone'] == 'zone-3']
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

    def choose_placement(self,
                         availableLocations: list[Location],
                         loadout: Loadout) -> Optional[tuple[Location, Item]]:
        """ returns (location to place an item, which item to place there) """
        if self.plando:
            location, item = self.plando.pop(0)

            # remove the item from prog or extra items so it can't be used again
            if item in self.prog_items:
                self.prog_items.remove(item)
            elif item in self.extra_items:
                self.extra_items.remove(item)

            return location, item

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

    def filter_locations_for_item(self, locations, item):
        return locations

    def validate(self, game):
        if self.game.options.ascent_fix:
            self.do_ascent_fix()

    def do_ascent_fix(self):
        zone_items = defaultdict(list)
        for loc in self.game.all_locations.values():
            zone_items[loc['zone']].append(loc['item'])

        # shallow copy of all locations
        all_locations = self.game.all_locations.values()
        needs_duplicate = []

        for zone_name, items in forced_zone_items.items():
            for item in items:
                if item in zone_items[zone_name]:
                    zone_items[zone_name].remove(item)
                else:
                    needs_duplicate.append(item)

        # print('duplicates:', [i[0] for i in needs_duplicate])
        # remove a minor item from forced locations an replace with item
        for forced_item, forced_locations in self.forced_locations:
            if forced_item not in needs_duplicate:
                # all good, continue loop
                continue
            open_locations = [l for l in forced_locations if l['item'] in _minor_items]
            if len(open_locations) == 0:
                zone_name = forced_item_zone[forced_item]
                raise ValueError(f'Unable to place duplicate item{forced_item[0]} in {zone_name}')
            open_location = open_locations[0]
            open_location['item'] = forced_item

            # remove the location from the rest of the force list
            for _, locations in self.forced_locations:
                if open_location in locations:
                    locations.remove(open_location)

