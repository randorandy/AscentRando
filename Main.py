from collections import defaultdict
import random
import sys
import os
from typing import Literal, Optional, Type
import argparse

from connection_data import SunkenNestL, VanillaAreas
from fillInterface import FillAlgorithm
from game import Game, GameOptions
from item_data import Item, Items, items_unpackable
from loadout import Loadout
from location_data import Location, pullCSV, spacePortLocs
from logicExpert import Expert
import logic_updater
import fillAssumed
import fillMajor
import areaRando

from romWriter import RomWriter
from solver import solve


def plmidFromHiddenness(itemArray, hiddenness) -> bytes:
    if hiddenness == "open":
        plmid = itemArray[1]
    elif hiddenness == "chozo":
        plmid = itemArray[2]
    else:
        plmid = itemArray[3]
    return plmid

def write_location(romWriter: RomWriter, location: Location) -> None:
    """
    provide a location with an ['item'] value, such as Missile, Super, etc
    write all rom locations associated with the item location
    """
    item = location["item"]
    assert item, f"{location['fullitemname']} didn't get an item"
    # TODO: support locations with no items?
    plmid = plmidFromHiddenness(item, location['hiddenness'])
    for address in location['locids']:
        romWriter.writeItem(address, plmid, item[4])
    for address in location['alternateroomlocids']:
        if location['alternateroomdifferenthiddenness'] == "":
            # most of the alt rooms go here, having the same item hiddenness
            # as the corresponding "pre-item-move" item had
            plmid_altroom = plmid
        else:
            plmid_altroom = plmidFromHiddenness(item, location['alternateroomdifferenthiddenness'])
        romWriter.writeItem(address, plmid_altroom, item[4])


fillers: dict[str, Type[FillAlgorithm]] = {
    "D": fillAssumed.FillAssumed,
    "MM": fillMajor.FillMajor,
}


# main program
def Main(options: GameOptions, romWriter: Optional[RomWriter] = None) -> None:
    game = generate(options)
    rom_name = write_rom(game)
    write_spoiler_file(game, rom_name)

def generate(options: dict) -> Game:
    areaA = ""

    # hudFlicker=""
    # while hudFlicker != "Y" and hudFlicker != "N" :
    #     hudFlicker= input("Enter Y to patch HUD flicker on emulator, or N to decline:")
    #     hudFlicker = hudFlicker.title()
    random.seed(options.seed)


    csvdict = pullCSV()
    locArray = list(csvdict.values())
    
    seedComplete = False
    randomizeAttempts = 0
    logic = Expert
    #if options['logic'] == 'casual':
    #    logic = Casual
    game = Game(options,
                logic,
                csvdict,
                areaA == "A",
                VanillaAreas())
    while not seedComplete :
        if game.area_rando:  # area rando
            game.connections = areaRando.RandomizeAreas()
            # print(Connections) #test
        randomizeAttempts += 1
        if randomizeAttempts > 30 :
            print("Giving up after 30 attempts. Help?")
            break
        print("Starting randomization attempt:", randomizeAttempts)
        game.item_placement_spoiler = ""
        game.item_placement_spoiler += f"Starting randomization attempt: {randomizeAttempts}\n"
        game.item_placement_spoiler += f"Seed: {game.options.seed}"
        # now start randomizing
        seedComplete = assumed_fill(game)
        #seedComplete = assumed_fill(game)
        
    #_got_all, solve_lines, _locs = solve(game)
    #^ what is this?
            
    return game




def assumed_fill(game: Game) -> tuple[bool]:
    for loc in game.all_locations.values():
        loc["item"] = None
    dummy_locations: list[Location] = []
    loadout = Loadout(game)
    fill_algorithm = fillers[game.options.fill_choice](game)
    n_items_to_place = fill_algorithm.count_items_remaining()
    assert n_items_to_place <= len(game.all_locations), \
        f"{n_items_to_place} items to put in {len(game.all_locations)} locations"
    print(f"{fill_algorithm.count_items_remaining()} items to place")
    while fill_algorithm.count_items_remaining():
        placePair = fill_algorithm.choose_placement(dummy_locations, loadout)
        if placePair is None:
            message = ('Item placement was not successful in assumed. '
                       f'{fill_algorithm.count_items_remaining()} items remaining.')
            print(message)

            break
        placeLocation, placeItem = placePair
        placeLocation["item"] = placeItem

        if fill_algorithm.count_items_remaining() == 0:
            # Normally, assumed fill will always make a valid playthrough,
            # but dropping from spaceport can mess that up,
            # so it needs to be checked again.
            #completable, _, _ = solve(game)
            #completable = game.all_locations["Morph"]["item"] == Items.Morph
            completable = True
            fill_algorithm.validate(game)
            if completable:
                print("Item placements successful.")
            return completable

    return False

def write_rom(game: Game, romWriter: Optional[RomWriter] = None) -> str:
    logicChoice = "E"

    areaA = ""


    rom_clean_path = "roms/Ascent.sfc"
    rom_name = f"Ascent{game.options.seed}.sfc"
    rom1_path = f"roms/{rom_name}"

    if romWriter is None :
        romWriter = RomWriter.fromFilePaths(origRomPath=rom_clean_path)
    else :
        # remove .sfc extension and dirs
        romWriter.setBaseFilename(rom1_path[:-4].split("/")[-1])

    for loc in game.all_locations.values():
        write_location(romWriter, loc)

    # Morph Ball Fix
    romWriter.writeBytes(0x268ce, b"\x04")
    romWriter.writeBytes(0x26e02, b"\x04")

    # Suit animation skip patch
    romWriter.writeBytes(0x20717, b"\xea\xea\xea\xea")
    
    # Remove gravity suit heat protection #test
    romWriter.writeBytes(0x6e37d, b"\x01")
    romWriter.writeBytes(0x869dd, b"\x01")    #hellrun speed echoes patch ##verify
    romWriter.writeBytes(0x8b629, b"\x01")

    # Fix screw attack selection
    romWriter.writeBytes(0x134c5, b"\x0c")
    # Unlink two Varia suits
    romWriter.writeBytes(0x1c429b, b"\x32") #now plmid:50
    # Allow re-entry to zone 1 by removing gray doors
    romWriter.writeBytes(0x1c07c2, b"\x90")
    romWriter.writeBytes(0x1c0836, b"\x90")
    romWriter.writeBytes(0x1c0538, b"\x90")
    romWriter.writeBytes(0x1c0670, b"\x8a")
   
    romWriter.finalizeRom(rom1_path)
    print("Done!")
    print(f"Filename is {rom_name}")

    return rom_name

def get_spoiler(game: Game) -> str:
    """ the text in the spoiler file """

    spoilerSave = game.item_placement_spoiler + '\n'

    _completable, play_through, _locs = solve(game)
    #solve_lines = spoil_play_through(play_through)

    #s = f"RNG Seed: {game.seed}\n\n"
    s = "\n Spoiler \n\n Spoiler \n\n Spoiler \n\n Spoiler \n\n"
    s += spoilerSave
    s += '\n\n'
    for solve_line in play_through:
        s += solve_line + '\n'

    return s

def write_spoiler_file(game: Game, rom_name: str) -> None:
    text = get_spoiler(game)
    dest_dir = 'spoilers'
    dest = os.path.join(dest_dir, f'{rom_name}.spoiler.txt')
    with open(dest, "w") as spoiler_file:
        spoiler_file.write(text)
    print(f"Spoiler file is {dest}")

def forward_fill(game: Game,
                 fillChoice: Literal["M", "S", "MM"],
                 spoilerSave: str) -> tuple[bool, str]:
    unusedLocations : list[Location] = []
    unusedLocations.extend(game.all_locations.values())
    availableLocations: list[Location] = []
    # visitedLocations = []
    loadout = Loadout(game)
    loadout.append(SunkenNestL)  # starting area
    # use appropriate fill algorithm for initializing item lists
    fill_algorithm = fillers[fillChoice](game.connections)
    while len(unusedLocations) != 0 or len(availableLocations) != 0:
        # print("loadout contains:")
        # print(loadout)
        # for a in loadout:
        #     print("-",a[0])
        # update logic by updating unusedLocations
        # using helper function, modular for more logic options later
        # unusedLocations[i]['inlogic'] holds the True or False for logic
        logic_updater.updateAreaLogic(loadout)
        logic_updater.updateLogic(unusedLocations, loadout)

        # update unusedLocations and availableLocations
        for i in reversed(range(len(unusedLocations))):  # iterate in reverse so we can remove freely
            if unusedLocations[i]['inlogic'] is True:
                # print("Found available location at",unusedLocations[i]['fullitemname'])
                availableLocations.append(unusedLocations[i])
                unusedLocations.pop(i)
        # print("Available locations sits at:",len(availableLocations))
        # for al in availableLocations :
        #     print(al[0])
        # print("Unused locations sits at size:",len(unusedLocations))
        # print("unusedLocations:")
        # for u in unusedLocations :
        #     print(u['fullitemname'])

        if availableLocations == [] and unusedLocations != [] :
            print(f'Item placement was not successful. {len(unusedLocations)} locations remaining.')
            spoilerSave += f'Item placement was not successful. {len(unusedLocations)} locations remaining.\n'
            # for i in loadout:
            #     print(i[0])
            # for u in unusedLocations :
            #     print("--",u['fullitemname'])

            break

        placePair = fill_algorithm.choose_placement(availableLocations, loadout)
        if placePair is None:
            print(f'Item placement was not successful due to majors. {len(unusedLocations)} locations remaining.')
            spoilerSave += f'Item placement was not successful. {len(unusedLocations)} locations remaining.\n'
            break
        # it returns your location and item, which are handled here
        placeLocation, placeItem = placePair
        if (placeLocation in unusedLocations) :
            unusedLocations.remove(placeLocation)
        placeLocation["item"] = placeItem
        availableLocations.remove(placeLocation)
        fill_algorithm.remove_from_pool(placeItem)
        loadout.append(placeItem)
        if not ((placeLocation['fullitemname'] in spacePortLocs) or (Items.spaceDrop in loadout)):
            loadout.append(Items.spaceDrop)
        spoilerSave += f"{placeLocation['fullitemname']} - - - {placeItem[0]}\n"
        # print(placeLocation['fullitemname']+placeItem[0])

        if availableLocations == [] and unusedLocations == [] :
            print("Item placements successful.")
            spoilerSave += "Item placements successful.\n"
            return True, spoilerSave
    return False, spoilerSave


def args_to_game_options(args):
    args = args[:]
    options = GameOptions(
        logic=Expert,
        fill_choice='D',
        can=[],
    )
    options._inventory = defaultdict(int)
    while args:
        option = args.pop(0)
        if option in ['-l', '--logic']:
            logic = args.pop(0).lower()
            if logic.startswith('e'):
                options.logic = Expert
            elif logic.startswith('c'):
                options.logic = Casual
            else:
                print(f'Warning: unrecognized logic option "{logic}"')
        elif option in ['-s', '--seed']:
            options.seed = int(args.pop(0))
        elif option == '-d':
            options.fill_choice = 'D'
        elif option == '-mm':
            options.fill_choice = 'MM'
        elif option == '--can':
            options.can = args.pop(0).split(',')
        elif option == '--inventory':
            names = args.pop(0).split(',')
            for name in names:
                options._inventory[name] += 1
        else:
            print(f'Warning: unrecognized option "{option}"')
    return options

if __name__ == "__main__":
    import time
    t0 = time.perf_counter()
    options = GameOptions(
        logic=Expert,
        fill_choice='D',
        can=[],
    )
    args = sys.argv[1:]
    while args:
        option = args.pop(0)
        if option in ['-l', '--logic']:
            logic = args.pop(0).lower()
            if logic.startswith('e'):
                options.logic = Expert
            elif logic.startswith('c'):
                options.logic = Casual
            else:
                print(f'Warning: unrecognized logic option "{logic}"')
        elif option in ['-s', '--seed']:
            options.seed = int(args.pop(0))
        elif option == '-d':
            options.fill_choice = 'D'
        elif option == '-mm':
            options.fill_choice = 'MM'
        elif option == '--can':
            options.can = args.pop(0).split(',')
        else:
            print(f'Warning: unrecognized option "{option}"')

    Main(options)
    t1 = time.perf_counter()
    print(f"time taken: {t1 - t0}")
