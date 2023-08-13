import random
from typing import Optional

from fillAssumed import FillAssumed
from item_data import Item, Items
from location_data import majorLocs, Location
from loadout import Loadout

def match_item_to_location(item, location):
    major_item = item not in [Items.Missile, Items.Super, Items.PowerBomb]
    major_location = location['fullitemname'] in majorLocs
    return major_item == major_location

class FillMajor(FillAssumed):
    def __init__(self, game):
        super().__init__(game)

        # Filter forced_item_locations for m/m
        filtered_item_locations = []
        for item, locations in self.forced_item_locations:
            filtered_locations = [
                loc for loc in locations
                if match_item_to_location(item, loc)
            ]
            filtered_item_locations.append([item, filtered_locations])
        self.forced_item_locations = filtered_item_locations

    def filter_locations_for_item(self, locations, item):
        return [
            loc for loc in locations
            if match_item_to_location(item, loc)
        ]

    def choose_placement(self,
                         availableLocations: list[Location],
                         loadout: Loadout) -> Optional[tuple[Location, Item]]:
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

        available_locations = self.filter_locations_for_item(available_locations, item_to_place)
        if len(available_locations) == 0:
            return None

        # This magic number 2 could be an option for "How loaded do you want the spaceport to be?"
        # (lower number means more progression items in spaceport)
        return self._choose_location(available_locations, 2), item_to_place

    def validate(self, game):
        super().validate(game)
        for location in game.all_locations.values():
            assert match_item_to_location(location['item'], location)
