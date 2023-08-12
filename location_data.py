import csv
from typing import Optional, TypedDict, cast

from item_data import Item
import os

# other unused columns in Location:
# "roomid", "area", "xy","plmtypename","state","roomname","alternateroomid"
class Location(TypedDict):
    fullitemname: str
    locids: list[int]
    plmtypeid: int
    plmparamhi: int
    plmparamlo: int
    hiddenness: str
    alternateroomlocids: list[int]
    alternateroomdifferenthiddenness: str
    inlogic: bool
    item: Optional[Item]


spacePortLocs = ["Ready Room",
                 "Torpedo Bay",
                 "Extract Storage",
                 "Gantry",
                 "Docking Port 4",
                 "Docking Port 3",
                 "Weapon Locker",
                 "Aft Battery",
                 "Forward Battery"]

majorLocs = frozenset([
    "Morph Ball",
    "Bombs",
    "Charge Beam",
    "Green Giant Energy",
    "Green Giant Reserve",
    "Crystal Glade W Open Energy",
    "My Other Jump 7 Reserve Tank",
    "My Other Jump 7 Energy Tank",
    "Plasma Beam",
    "HiJump",
    "Station Plot Reserve Tank",
    "Half Satiation Weapon Upgrade",
    "1x1 Goodness Energy",
    "Time N Sync Weapon Upgrade",
    "Volonus Weapon Upgrade",
    "Speed Booster",
    "Living Presence Energy",
    "Chain Reaction Spark Upgrade",
    "Grapple Beam",
    "Target Jump Reserve",
    "Closing the Loop Energy Tank",
    "Moisture Challenge Weapon Upgrade",
    "Jail Energy",
    "Trap Weapon Upgrade",
    "Expand Shaft L Energy",
    "Mount Top Energy",
    "Energizer Energy",
    "Boost Ball",
    "Explorer Reserve",
    "Reflects Trail Weapon Upgrade",
    "Endgame Blockade Spark Upgrade",
    "Spazer",
    "Gettin Around It Varia",
    "Taste the Rainbow Varia",
    "West Shaft Reserve",
    "Wave Beam",
    "Abyss Main Energy",
    "Abyss Main Spark Upgrade",
    "Pushy Blocks Weapon Upgrade",
    "Forgotten Room Reserve",
    "Ice Beam",
    "Space Jump",
    "Above is Easier Reserve",
    "Best Beam Hard Energy",
    "Pbs Limited Radius Weapon Upgrade",
    "Gravity Suit",
    "Water Logged Energy",
    "HP Killer Energy",
    "Mind Puzzled Spark Upgrade",
    "Mind Puzzled Weapon Upgrade",
    "Screw Attack",
])


def pullCSV() -> dict[str, Location]:
    csvdict: dict[str, Location] = {}

    def commentfilter(line: str) -> bool:
        return (line[0] != '#')

    dir_path = os.path.dirname(os.path.realpath(__file__))
    nature_csv = os.path.join(dir_path, 'ascentcsv1.csv')
    with open(nature_csv, 'r') as csvfile:
        reader = csv.DictReader(filter(commentfilter, csvfile))
        for row in reader:
            # commas within fields -> array
            row['locids'] = row['locids'].split(',')
            row['alternateroomlocids'] = row['alternateroomlocids'].split(',')
            # hex fields we want to use -> int
            row['locids'] = [int(locstr, 16)
                             for locstr in row['locids'] if locstr != '']
            row['alternateroomlocids'] = [
                int(locstr, 16) for locstr in row['alternateroomlocids'] if locstr != '']
            row['plmtypeid'] = int(row['plmtypeid'], 16)
            row['plmparamhi'] = int(row['plmparamhi'], 16)
            row['plmparamlo'] = int(row['plmparamlo'], 16)
            # new key: 'inlogic'
            row['inlogic'] = False
            # the item that we place in this location
            row["item"] = None
            csvdict[row['fullitemname']] = cast(Location, row)
    return csvdict
