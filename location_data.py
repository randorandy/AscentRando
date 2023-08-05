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
    "Pendulu Left Energy Tank",
    "Pendulu Sand Cavern Energy Tank",
    "Tchornobog Big Tree Energy",
    "Screw Attack",
    "Dead Pool Energy",
    "Plasma Beam",
    "Spo Spo Energy",
    "Springball Energy Tank",
    "Springball",
    "Wave Beam",
    "Grapple Beam",
    "Tchornobog Roots Energy",
    "Charge Beam",
    "Speed Booster",
    "Draygon Lab Energy Tank",
    "Spazer",
    "Space Jump",
    "Varia Suit",
    "Ice Beam",
    "Gold Torizo Energy",
    "Akhlys First Fortress Energy",
    "Akhlys Speed Pirates Energy",
    "Gravity Suit",
    "Shaktool Energy Tank",
    "HiJump"
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
